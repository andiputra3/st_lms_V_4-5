-- ST-LMS SQLite Schema Freeze v1
-- Purpose: foundation for collector, simulation, statistics, knowledge, BAG, governance, replay, benchmark, and audit.
-- SQLite target: 3.38+

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- =========================================================
-- 0) CORE METADATA
-- =========================================================

CREATE TABLE IF NOT EXISTS app_sessions (
  session_id TEXT PRIMARY KEY,
  session_kind TEXT NOT NULL CHECK (session_kind IN ('build','simulation','replay','benchmark','analysis','manual')),
  symbol TEXT,
  timeframe TEXT,
  started_at INTEGER NOT NULL,
  ended_at INTEGER,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','closed','failed','frozen')),
  notes TEXT
);

CREATE TABLE IF NOT EXISTS symbols (
  symbol TEXT PRIMARY KEY,
  asset_class TEXT NOT NULL DEFAULT 'spot',
  exchange TEXT NOT NULL DEFAULT 'binance',
  quote_asset TEXT NOT NULL DEFAULT 'USDT',
  tick_size REAL,
  step_size REAL,
  min_qty REAL,
  min_notional REAL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS timeframes (
  timeframe TEXT PRIMARY KEY,
  seconds INTEGER NOT NULL UNIQUE,
  label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
  run_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  run_kind TEXT NOT NULL CHECK (run_kind IN ('collector','simulation','replay','benchmark','audit','build')),
  started_at INTEGER NOT NULL,
  ended_at INTEGER,
  status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running','pass','fail','stopped')),
  input_hash TEXT,
  output_hash TEXT,
  notes TEXT
);

-- =========================================================
-- 1) MARKET LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS market_candles (
  candle_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  run_id TEXT REFERENCES pipeline_runs(run_id) ON DELETE SET NULL,
  symbol TEXT NOT NULL REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT NOT NULL REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  open REAL NOT NULL,
  high REAL NOT NULL,
  low REAL NOT NULL,
  close REAL NOT NULL,
  volume REAL NOT NULL,
  quote_volume REAL,
  taker_buy_volume REAL,
  taker_sell_volume REAL,
  gap_flag INTEGER NOT NULL DEFAULT 0 CHECK (gap_flag IN (0,1)),
  data_status TEXT NOT NULL DEFAULT 'ok' CHECK (data_status IN ('ok','warmup','provisional','insufficient','gap','invalid')),
  source TEXT NOT NULL DEFAULT 'exchange',
  created_at INTEGER NOT NULL,
  UNIQUE(symbol, timeframe, ts)
);

CREATE INDEX IF NOT EXISTS idx_market_candles_symbol_tf_ts
ON market_candles(symbol, timeframe, ts);

CREATE TABLE IF NOT EXISTS market_metadata (
  meta_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  symbol TEXT NOT NULL REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT NOT NULL REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  ts INTEGER NOT NULL,
  created_at INTEGER NOT NULL,
  UNIQUE(symbol, timeframe, key, ts)
);

CREATE TABLE IF NOT EXISTS open_interest_series (
  oi_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  symbol TEXT NOT NULL REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT NOT NULL REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  open_interest REAL,
  open_interest_delta REAL,
  source TEXT NOT NULL DEFAULT 'proxy',
  status TEXT NOT NULL DEFAULT 'ok' CHECK (status IN ('ok','proxy','missing','warmup')),
  created_at INTEGER NOT NULL,
  UNIQUE(symbol, timeframe, ts)
);

CREATE INDEX IF NOT EXISTS idx_oi_symbol_tf_ts
ON open_interest_series(symbol, timeframe, ts);

CREATE TABLE IF NOT EXISTS market_gaps (
  gap_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  symbol TEXT NOT NULL REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT NOT NULL REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  gap_type TEXT NOT NULL,
  gap_size REAL,
  created_at INTEGER NOT NULL
);

-- =========================================================
-- 2) TRUTH LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS truth_snapshots (
  truth_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  candle_id TEXT NOT NULL REFERENCES market_candles(candle_id) ON DELETE CASCADE,
  symbol TEXT NOT NULL REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT NOT NULL REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  close REAL NOT NULL,
  st REAL,
  st_dir INTEGER,
  st_color TEXT,
  st_point INTEGER,
  atr REAL,
  ema REAL,
  ema12 REAL,
  ema26 REAL,
  macd REAL,
  macd_signal REAL,
  macd_hist REAL,
  rsi REAL,
  wpr REAL,
  volume REAL,
  volume_delta REAL,
  oi REAL,
  oi_delta REAL,
  dist_atr REAL,
  dist_to_st REAL,
  truth_status TEXT NOT NULL DEFAULT 'ok' CHECK (truth_status IN ('ok','warmup','provisional','insufficient','invalid')),
  created_at INTEGER NOT NULL,
  UNIQUE(candle_id)
);

CREATE INDEX IF NOT EXISTS idx_truth_symbol_tf_ts
ON truth_snapshots(symbol, timeframe, ts);

CREATE TABLE IF NOT EXISTS truth_cache (
  cache_id TEXT PRIMARY KEY,
  truth_id TEXT NOT NULL REFERENCES truth_snapshots(truth_id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  UNIQUE(truth_id, key)
);

-- =========================================================
-- 3) STRUCTURE LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS structure_snapshots (
  structure_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  candle_id TEXT NOT NULL REFERENCES market_candles(candle_id) ON DELETE CASCADE,
  truth_id TEXT NOT NULL REFERENCES truth_snapshots(truth_id) ON DELETE CASCADE,
  symbol TEXT NOT NULL REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT NOT NULL REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  wave_structure TEXT,
  wave_line_count INTEGER NOT NULL DEFAULT 0,
  slope REAL,
  ladder_level INTEGER,
  cage_status TEXT,
  cage_upper REAL,
  cage_lower REAL,
  cage_pp REAL,
  cage_range_atr REAL,
  cage_breakout TEXT,
  price_position REAL,
  dist_ceiling REAL,
  dist_floor REAL,
  market_phase TEXT,
  support_level REAL,
  resistance_level REAL,
  escape_path TEXT,
  structure_status TEXT NOT NULL DEFAULT 'ok' CHECK (structure_status IN ('ok','warmup','provisional','insufficient','invalid')),
  created_at INTEGER NOT NULL,
  UNIQUE(candle_id)
);

CREATE INDEX IF NOT EXISTS idx_structure_symbol_tf_ts
ON structure_snapshots(symbol, timeframe, ts);

CREATE TABLE IF NOT EXISTS wave_history (
  wave_history_id TEXT PRIMARY KEY,
  structure_id TEXT NOT NULL REFERENCES structure_snapshots(structure_id) ON DELETE CASCADE,
  wave_index INTEGER NOT NULL,
  line_dom TEXT,
  line_value REAL,
  line_color TEXT,
  created_at INTEGER NOT NULL,
  UNIQUE(structure_id, wave_index)
);

CREATE TABLE IF NOT EXISTS cage_history (
  cage_history_id TEXT PRIMARY KEY,
  structure_id TEXT NOT NULL REFERENCES structure_snapshots(structure_id) ON DELETE CASCADE,
  version_label TEXT NOT NULL,
  upper REAL,
  lower REAL,
  breakout TEXT,
  pressure REAL,
  created_at INTEGER NOT NULL
);

-- =========================================================
-- 4) EVIDENCE LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS evidence_snapshots (
  evidence_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  candle_id TEXT NOT NULL REFERENCES market_candles(candle_id) ON DELETE CASCADE,
  truth_id TEXT NOT NULL REFERENCES truth_snapshots(truth_id) ON DELETE CASCADE,
  structure_id TEXT NOT NULL REFERENCES structure_snapshots(structure_id) ON DELETE CASCADE,
  symbol TEXT NOT NULL REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT NOT NULL REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  direction_bus_json TEXT,
  correction_bus_json TEXT,
  exit_bus_json TEXT,
  max_score REAL,
  data_quality_json TEXT,
  evidence_status TEXT NOT NULL DEFAULT 'ok' CHECK (evidence_status IN ('ok','warmup','provisional','insufficient','invalid')),
  created_at INTEGER NOT NULL,
  UNIQUE(candle_id)
);

CREATE INDEX IF NOT EXISTS idx_evidence_symbol_tf_ts
ON evidence_snapshots(symbol, timeframe, ts);

-- =========================================================
-- 5) CLONE LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS clones (
  clone_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  symbol TEXT NOT NULL REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT NOT NULL REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  clone_kind TEXT NOT NULL CHECK (clone_kind IN ('LONG','SHORT','GRID')),
  created_at INTEGER NOT NULL,
  UNIQUE(session_id, symbol, timeframe, clone_kind)
);

CREATE TABLE IF NOT EXISTS clone_observations (
  observation_id TEXT PRIMARY KEY,
  clone_id TEXT NOT NULL REFERENCES clones(clone_id) ON DELETE CASCADE,
  evidence_id TEXT NOT NULL REFERENCES evidence_snapshots(evidence_id) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  clone_bias TEXT,
  entry_legal INTEGER NOT NULL DEFAULT 0 CHECK (entry_legal IN (0,1)),
  exit_legal INTEGER NOT NULL DEFAULT 0 CHECK (exit_legal IN (0,1)),
  observation_json TEXT,
  created_at INTEGER NOT NULL,
  UNIQUE(clone_id, ts)
);

-- =========================================================
-- 6) TRADE LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS trade_markers (
  marker_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  clone_id TEXT NOT NULL REFERENCES clones(clone_id) ON DELETE CASCADE,
  candle_id TEXT NOT NULL REFERENCES market_candles(candle_id) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('ENTRY','EXIT','PARTIAL','BREAKEVEN','TRAILING','HOLD','PASS','NO_TRADE')),
  side TEXT CHECK (side IN ('LONG','SHORT','GRID')),
  reason TEXT,
  entry REAL,
  exit REAL,
  gross REAL,
  fee REAL,
  slip REAL,
  net REAL,
  result TEXT CHECK (result IN ('WIN','LOSS','BREAKEVEN','OPEN','PASS','NA')),
  mae REAL,
  mfe REAL,
  hold_count INTEGER NOT NULL DEFAULT 0,
  marker_json TEXT,
  created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trade_markers_clone_ts
ON trade_markers(clone_id, ts);

-- =========================================================
-- 7) POSITION LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS positions (
  position_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  clone_id TEXT NOT NULL REFERENCES clones(clone_id) ON DELETE CASCADE,
  entry_marker_id TEXT REFERENCES trade_markers(marker_id) ON DELETE SET NULL,
  exit_marker_id TEXT REFERENCES trade_markers(marker_id) ON DELETE SET NULL,
  symbol TEXT NOT NULL REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT NOT NULL REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  side TEXT NOT NULL CHECK (side IN ('LONG','SHORT','GRID')),
  status TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','HOLD','CLOSED','BREAKEVEN','TRAILING','PARTIAL')),
  entry_ts INTEGER NOT NULL,
  exit_ts INTEGER,
  entry_price REAL NOT NULL,
  exit_price REAL,
  qty REAL NOT NULL DEFAULT 0,
  leverage REAL,
  stop_loss REAL,
  take_profit REAL,
  profit_lock REAL,
  trailing_stop REAL,
  liquidation_distance REAL,
  mae REAL,
  mfe REAL,
  hold_count INTEGER NOT NULL DEFAULT 0,
  risk_json TEXT,
  position_json TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_positions_clone_status
ON positions(clone_id, status);

CREATE TABLE IF NOT EXISTS position_timeline (
  timeline_id TEXT PRIMARY KEY,
  position_id TEXT NOT NULL REFERENCES positions(position_id) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  price REAL,
  mae REAL,
  mfe REAL,
  hold_count INTEGER,
  note TEXT,
  created_at INTEGER NOT NULL
);

-- =========================================================
-- 8) STATISTICS LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS trade_statistics (
  stat_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  clone_id TEXT REFERENCES clones(clone_id) ON DELETE CASCADE,
  symbol TEXT REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  bucket_key TEXT,
  sample_count INTEGER NOT NULL DEFAULT 0,
  win_rate REAL,
  expectancy REAL,
  profit_factor REAL,
  mae REAL,
  mfe REAL,
  fee_drag REAL,
  wrong_rate REAL,
  coverage REAL,
  distance_health_hist TEXT,
  fee_safe_margin_dist TEXT,
  wrong_entry_dist TEXT,
  avg_hold REAL,
  created_at INTEGER NOT NULL,
  UNIQUE(session_id, clone_id, bucket_key)
);

CREATE TABLE IF NOT EXISTS market_statistics (
  market_stat_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  symbol TEXT REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  phase TEXT,
  wave_structure TEXT,
  price_position REAL,
  dist_bucket TEXT,
  support_hits INTEGER DEFAULT 0,
  resistance_hits INTEGER DEFAULT 0,
  breakout_count INTEGER DEFAULT 0,
  sideways_count INTEGER DEFAULT 0,
  trend_count INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL
);

-- =========================================================
-- 9) BAG LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS bag_artifacts (
  bag_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  stat_id TEXT REFERENCES trade_statistics(stat_id) ON DELETE SET NULL,
  symbol TEXT REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  bag_kind TEXT NOT NULL DEFAULT 'behavior' CHECK (bag_kind IN ('behavior','market','entry','exit','risk','knowledge')),
  bag_key TEXT NOT NULL,
  consensus TEXT,
  conflict_level TEXT,
  confidence REAL,
  sample_count INTEGER NOT NULL DEFAULT 0,
  payload_json TEXT,
  created_at INTEGER NOT NULL,
  UNIQUE(session_id, bag_key)
);

CREATE TABLE IF NOT EXISTS bag_patterns (
  pattern_id TEXT PRIMARY KEY,
  bag_id TEXT NOT NULL REFERENCES bag_artifacts(bag_id) ON DELETE CASCADE,
  pattern_rank INTEGER NOT NULL DEFAULT 1,
  pattern_key TEXT NOT NULL,
  pattern_value TEXT,
  created_at INTEGER NOT NULL,
  UNIQUE(bag_id, pattern_rank)
);

CREATE TABLE IF NOT EXISTS bag_compression (
  compression_id TEXT PRIMARY KEY,
  bag_id TEXT NOT NULL REFERENCES bag_artifacts(bag_id) ON DELETE CASCADE,
  source_count INTEGER NOT NULL DEFAULT 0,
  compressed_count INTEGER NOT NULL DEFAULT 0,
  compression_ratio REAL,
  created_at INTEGER NOT NULL
);

-- =========================================================
-- 10) KNOWLEDGE LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS knowledge_artifacts (
  knowledge_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  bag_id TEXT REFERENCES bag_artifacts(bag_id) ON DELETE SET NULL,
  stat_id TEXT REFERENCES trade_statistics(stat_id) ON DELETE SET NULL,
  entity TEXT NOT NULL CHECK (entity IN ('ACADEMY','RIVER','ORACLE','HIVEMIND','DARWIN','LIBRARIAN','CERMIN')),
  sub_entity TEXT,
  bucket_key TEXT,
  sample_count INTEGER NOT NULL DEFAULT 0,
  win_rate REAL,
  expectancy REAL,
  confidence REAL,
  payload_json TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_knowledge_entity_bucket
ON knowledge_artifacts(entity, bucket_key);

-- =========================================================
-- 11) PREDICTION LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS predictions (
  prediction_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  knowledge_id TEXT REFERENCES knowledge_artifacts(knowledge_id) ON DELETE SET NULL,
  symbol TEXT REFERENCES symbols(symbol) ON DELETE CASCADE,
  timeframe TEXT REFERENCES timeframes(timeframe) ON DELETE CASCADE,
  ts INTEGER NOT NULL,
  predicted_side TEXT CHECK (predicted_side IN ('LONG','SHORT','GRID','PASS')),
  confidence REAL,
  similarity_score REAL,
  empirical_win_rate REAL,
  oracle_boost REAL,
  pattern_boost REAL,
  cermin_error REAL,
  payload_json TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS prediction_results (
  result_id TEXT PRIMARY KEY,
  prediction_id TEXT NOT NULL REFERENCES predictions(prediction_id) ON DELETE CASCADE,
  actual_side TEXT CHECK (actual_side IN ('LONG','SHORT','GRID','PASS')),
  actual_result TEXT,
  actual_profit REAL,
  actual_hold REAL,
  created_at INTEGER NOT NULL
);

-- =========================================================
-- 12) GOVERNANCE LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS governance_proposals (
  proposal_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  knowledge_id TEXT REFERENCES knowledge_artifacts(knowledge_id) ON DELETE SET NULL,
  param_name TEXT NOT NULL,
  proposed_value TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','APPROVED','REJECTED','ROLLED_BACK')),
  reason TEXT,
  bounded_check TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS governance_logs (
  log_id TEXT PRIMARY KEY,
  proposal_id TEXT REFERENCES governance_proposals(proposal_id) ON DELETE SET NULL,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  event_ts INTEGER NOT NULL,
  payload_json TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rollback_logs (
  rollback_id TEXT PRIMARY KEY,
  proposal_id TEXT REFERENCES governance_proposals(proposal_id) ON DELETE SET NULL,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  reason TEXT,
  rollback_ts INTEGER NOT NULL,
  payload_json TEXT,
  created_at INTEGER NOT NULL
);

-- =========================================================
-- 13) REPLAY LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS replay_sessions (
  replay_session_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  replay_kind TEXT NOT NULL CHECK (replay_kind IN ('candle','snapshot','trade','clone','knowledge','governance')),
  started_at INTEGER NOT NULL,
  ended_at INTEGER,
  status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running','pass','fail','stopped')),
  payload_json TEXT
);

CREATE TABLE IF NOT EXISTS replay_frames (
  replay_frame_id TEXT PRIMARY KEY,
  replay_session_id TEXT NOT NULL REFERENCES replay_sessions(replay_session_id) ON DELETE CASCADE,
  frame_index INTEGER NOT NULL,
  ts INTEGER NOT NULL,
  frame_kind TEXT NOT NULL,
  frame_json TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  UNIQUE(replay_session_id, frame_index)
);

-- =========================================================
-- 14) BENCHMARK LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS benchmark_runs (
  benchmark_run_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  run_kind TEXT NOT NULL CHECK (run_kind IN ('wasit','walk_forward','clone','trade','market')),
  started_at INTEGER NOT NULL,
  ended_at INTEGER,
  status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running','pass','fail','stopped')),
  gates_json TEXT,
  verdict TEXT,
  payload_json TEXT
);

CREATE TABLE IF NOT EXISTS benchmark_cases (
  benchmark_case_id TEXT PRIMARY KEY,
  benchmark_run_id TEXT NOT NULL REFERENCES benchmark_runs(benchmark_run_id) ON DELETE CASCADE,
  case_index INTEGER NOT NULL,
  label TEXT,
  input_json TEXT,
  output_json TEXT,
  pass_flag INTEGER NOT NULL DEFAULT 0 CHECK (pass_flag IN (0,1)),
  created_at INTEGER NOT NULL,
  UNIQUE(benchmark_run_id, case_index)
);

-- =========================================================
-- 15) AUDIT LAYER
-- =========================================================

CREATE TABLE IF NOT EXISTS audit_logs (
  audit_log_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  run_id TEXT REFERENCES pipeline_runs(run_id) ON DELETE SET NULL,
  domain TEXT NOT NULL,
  audit_type TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('CRITICAL','HIGH','MEDIUM','LOW','INFO')),
  title TEXT NOT NULL,
  detail TEXT,
  evidence_json TEXT,
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','closed','ignored')),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_issues (
  issue_id TEXT PRIMARY KEY,
  audit_log_id TEXT NOT NULL REFERENCES audit_logs(audit_log_id) ON DELETE CASCADE,
  issue_key TEXT NOT NULL,
  issue_value TEXT,
  created_at INTEGER NOT NULL,
  UNIQUE(audit_log_id, issue_key)
);

-- =========================================================
-- 16) SETTINGS / DICTIONARY / CRUD HELPERS
-- =========================================================

CREATE TABLE IF NOT EXISTS app_settings (
  setting_key TEXT PRIMARY KEY,
  setting_value TEXT NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS domain_dictionary (
  domain_key TEXT PRIMARY KEY,
  domain_name TEXT NOT NULL,
  display_order INTEGER NOT NULL,
  description TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

-- =========================================================
-- 17) DELETION / PURGE SUPPORT
-- =========================================================

CREATE TABLE IF NOT EXISTS purge_jobs (
  purge_job_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES app_sessions(session_id) ON DELETE CASCADE,
  domain TEXT NOT NULL,
  scope TEXT NOT NULL,
  target_symbol TEXT,
  target_timeframe TEXT,
  target_clone TEXT,
  target_bucket TEXT,
  target_id TEXT,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','done','failed')),
  reason TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_purge_jobs_domain_scope
ON purge_jobs(domain, scope);

-- =========================================================
-- 18) GENERIC ROW-LIFE SUPPORT
-- =========================================================

CREATE TABLE IF NOT EXISTS row_lifecycle (
  row_lifecycle_id TEXT PRIMARY KEY,
  table_name TEXT NOT NULL,
  row_id TEXT NOT NULL,
  lifecycle_state TEXT NOT NULL,
  ts INTEGER NOT NULL,
  payload_json TEXT,
  created_at INTEGER NOT NULL,
  UNIQUE(table_name, row_id, lifecycle_state, ts)
);

-- =========================================================
-- TRIGGERS: updated_at maintenance
-- =========================================================

CREATE TRIGGER IF NOT EXISTS trg_symbols_updated_at
AFTER UPDATE ON symbols
BEGIN
  UPDATE symbols SET updated_at = NEW.updated_at WHERE symbol = NEW.symbol;
END;

CREATE TRIGGER IF NOT EXISTS trg_knowledge_updated_at
AFTER UPDATE ON knowledge_artifacts
BEGIN
  UPDATE knowledge_artifacts SET updated_at = NEW.updated_at WHERE knowledge_id = NEW.knowledge_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_governance_updated_at
AFTER UPDATE ON governance_proposals
BEGIN
  UPDATE governance_proposals SET updated_at = NEW.updated_at WHERE proposal_id = NEW.proposal_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_audit_updated_at
AFTER UPDATE ON audit_logs
BEGIN
  UPDATE audit_logs SET updated_at = NEW.updated_at WHERE audit_log_id = NEW.audit_log_id;
END;

-- =========================================================
-- SEED DICTIONARIES
-- =========================================================

INSERT OR IGNORE INTO timeframes(timeframe, seconds, label) VALUES
('1m', 60, '1 Minute'),
('3m', 180, '3 Minutes'),
('5m', 300, '5 Minutes'),
('15m', 900, '15 Minutes'),
('30m', 1800, '30 Minutes'),
('1h', 3600, '1 Hour'),
('2h', 7200, '2 Hours'),
('4h', 14400, '4 Hours'),
('1d', 86400, '1 Day');

INSERT OR IGNORE INTO app_settings(setting_key, setting_value, updated_at) VALUES
('schema_version', '1.0.0', strftime('%s','now')),
('schema_name', 'ST-LMS SQLite Schema', strftime('%s','now'));

INSERT OR IGNORE INTO domain_dictionary(domain_key, domain_name, display_order, description, created_at, updated_at) VALUES
('market', 'MARKET', 1, 'Market observation layer', strftime('%s','now'), strftime('%s','now')),
('truth', 'TRUTH', 2, 'Truth physics layer', strftime('%s','now'), strftime('%s','now')),
('structure', 'STRUCTURE', 3, 'Market geometry layer', strftime('%s','now'), strftime('%s','now')),
('evidence', 'EVIDENCE', 4, 'Bus separation layer', strftime('%s','now'), strftime('%s','now')),
('clone', 'CLONE', 5, 'Clone runtime layer', strftime('%s','now'), strftime('%s','now')),
('trade', 'TRADE', 6, 'Trade marker layer', strftime('%s','now'), strftime('%s','now')),
('position', 'POSITION', 7, 'Position lifecycle layer', strftime('%s','now'), strftime('%s','now')),
('statistics', 'STATISTICS', 8, 'Statistics and aggregation layer', strftime('%s','now'), strftime('%s','now')),
('bag', 'BAG', 9, 'Behavior acquisition layer', strftime('%s','now'), strftime('%s','now')),
('knowledge', 'KNOWLEDGE', 10, 'Knowledge engine layer', strftime('%s','now'), strftime('%s','now')),
('prediction', 'PREDICTION', 11, 'Empirical prediction layer', strftime('%s','now'), strftime('%s','now')),
('governance', 'GOVERNANCE', 12, 'Proposal and rule layer', strftime('%s','now'), strftime('%s','now')),
('replay', 'REPLAY', 13, 'Replay layer', strftime('%s','now'), strftime('%s','now')),
('benchmark', 'BENCHMARK', 14, 'Benchmark layer', strftime('%s','now'), strftime('%s','now')),
('audit', 'AUDIT', 15, 'Audit layer', strftime('%s','now'), strftime('%s','now'));

COMMIT;
