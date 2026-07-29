"""
=====================================================
MODULE:     truth_point.py
PURPOSE:    Supertrend Point — unit truth utama ST-LMS.
            Satu SP = satu truth_snapshot per candle.
            Menghitung: st, stDir, color, atr, ema,
            macd, rsi, wpr, vel, acc, dist, distAtr,
            volDelta, flip.
OWNER:      PHASE-03 SUPERTREND POINT
INPUT:      Candle data (dari MarketConsumer)
OUTPUT:     truth_snapshot (immutable card)
DEPENDENCY: stlms.core.constants, stlms.core.utils,
            stlms.foundation.base_artifact
ARCHITECTURE:
            SP adalah unit truth utama. Setelah Market
            Collection, seluruh sistem bekerja pada level
            SP, bukan candle. SP dihitung sequential per
            simbol karena state kontigu (EMA, ATR).
RUNTIME:
            Sequential per simbol. Tidak bisa diparalelkan
            per-candle karena EMA/ATR continuity.
            Main thread (hot path).
RESOURCE:
            Memory: O(1) state per simbol.
            CPU: ringan — komputasi matematika sederhana.
=====================================================
"""

from dataclasses import dataclass, field
from typing import Optional
from ..core.types import Candle, PointStatus
from ..core.constants import (
    ATR_PERIOD, EMA_PERIOD, ST_MULTIPLIER,
    EMA_FAST, EMA_SLOW, MACD_SIGNAL,
    RSI_PERIOD, WPR_PERIOD, MS_PER_MINUTE
)
from ..core.utils import Card, IDGenerator, wib_iso, round_prec, canon, clamp
from ..foundation.base_artifact import BaseArtifact


@dataclass
class TruthPoint:
    """
    Satu Supertrend Point = output per candle dari Truth Layer.
    
    SP Philosophy:
        Setelah Market Collection, ST-LMS bekerja pada level SP.
        SP adalah unit truth utama. Line, Wave, Structure, Knowledge,
        Prediction — semuanya dibangun dari kumpulan SP.
    """
    ts: int
    close: float
    st: float
    st_canon: str
    st_dir: int  # 1=UP, -1=DOWN
    st_color: str  # HIJAU / MERAH
    atr: Optional[float] = None
    ema: Optional[float] = None
    ema12: Optional[float] = None
    ema26: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    rsi: Optional[float] = None
    wpr: Optional[float] = None
    vel: Optional[float] = None
    acc: Optional[float] = None
    vol_delta: float = 0.0
    dist: Optional[float] = None
    dist_atr: Optional[float] = None
    flip: Optional[str] = None
    point_status: PointStatus = PointStatus.WARMUP
    oi_value: Optional[float] = None
    oi_delta: Optional[float] = None
    prev_macd_hist: Optional[float] = None
    ema_slope: float = 0.0


class PointBuilder:
    """
    Membangun Supertrend Point dari candle data.
    
    Reference: ST_LMS_CORE.js TRUTH.PointBuilder (lines 154-185)
    Reference: MASTER_SPECIFICATION.html S4 (Market Geometry)
    
    State Continuity:
        pc, atr, ema, e12, e26, sig, puf, plf, trend,
        ag, al, hs, ls, wp1, vp, mh1 — semua kontigu.
        Tidak bisa diparalelkan per-candle.
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.reset()
    
    def reset(self):
        """Reset semua state — untuk memulai ulang komputasi."""
        self.pc: Optional[float] = None
        self.atr_val: Optional[float] = None
        self.ema_val: Optional[float] = None
        self.e12: Optional[float] = None
        self.e26: Optional[float] = None
        self.sig: Optional[float] = None
        self.puf: Optional[float] = None
        self.plf: Optional[float] = None
        self.trend: int = 1  # 1=UP, -1=DOWN
        self.ag: Optional[float] = None
        self.al: Optional[float] = None
        self.hs: list[float] = []
        self.ls: list[float] = []
        self.wp1: Optional[float] = None
        self.vp: Optional[float] = None
        self.mh1: Optional[float] = None
        self._prev_close: Optional[float] = None
    
    def build(self, candle: Candle, oi_value: Optional[float] = None,
              oi_delta: Optional[float] = None) -> TruthPoint:
        """
        Bangun satu Supertrend Point dari satu candle.
        
        Args:
            candle: OHLCV data
            oi_value: Open Interest value (inherited from OI slot)
            oi_delta: OI change from previous slot
        
        Returns:
            TruthPoint dengan semua indikator
        """
        h, l, cl = candle.high, candle.low, candle.close
        pc = self.pc if self.pc is not None else cl
        
        # ── ATR (Average True Range) ──────────────────────────
        tr = max(h - l, abs(h - pc), abs(l - pc))
        if self.atr_val is None:
            self.atr_val = tr
        else:
            self.atr_val = self.atr_val + (tr - self.atr_val) / ATR_PERIOD
        
        # ── EMA ──────────────────────────────────────────────
        kf = 2.0 / (EMA_PERIOD + 1)
        if self.ema_val is None:
            self.ema_val = cl
        else:
            self.ema_val = self.ema_val + (cl - self.ema_val) * kf
        
        # ── EMA 12/26 (for MACD) ─────────────────────────────
        if self.e12 is None:
            self.e12 = cl
        else:
            self.e12 = self.e12 + (cl - self.e12) * (2.0 / 13)
        if self.e26 is None:
            self.e26 = cl
        else:
            self.e26 = self.e26 + (cl - self.e26) * (2.0 / 27)
        
        macd_val = self.e12 - self.e26
        if self.sig is None:
            self.sig = macd_val
        else:
            self.sig = self.sig + (macd_val - self.sig) * (2.0 / 10)
        macd_hist = macd_val - self.sig
        
        # ── Supertrend ───────────────────────────────────────
        hl2 = (h + l) / 2.0
        band = self.atr_val * ST_MULTIPLIER
        ub = hl2 + band
        lb = hl2 - band
        
        if self.puf is None:
            uf, lf = ub, lb
        else:
            uf = min(ub, self.puf) if cl <= self.puf else ub
            lf = max(lb, self.plf) if cl >= self.plf else lb
        
        # Flip detection
        flip = None
        if self.puf is not None and self.plf is not None:
            if self.trend == -1 and cl > self.puf:
                self.trend = 1
                flip = "TREND_FLIP_UP"
            elif self.trend == 1 and cl < self.plf:
                self.trend = -1
                flip = "TREND_FLIP_DOWN"
        
        st = lf if self.trend == 1 else uf
        color = "HIJAU" if cl > st else ("MERAH" if cl < st else ("HIJAU" if self.trend == 1 else "MERAH"))
        
        # ── RSI ──────────────────────────────────────────────
        rsi_val = None
        if pc is not None:
            diff = cl - pc
            g = diff if diff > 0 else 0.0
            lo = -diff if diff < 0 else 0.0
            if self.ag is None:
                self.ag, self.al = g, lo
            else:
                self.ag = (self.ag * (ATR_PERIOD - 1) + g) / ATR_PERIOD
                self.al = (self.al * (ATR_PERIOD - 1) + lo) / ATR_PERIOD
            if len(self.hs) > ATR_PERIOD:
                rs = 100.0 if self.al == 0 else self.ag / self.al
                rsi_val = 100.0 - 100.0 / (1.0 + rs)
        
        # ── Williams %R ──────────────────────────────────────
        self.hs.append(h)
        self.ls.append(l)
        wpr_val = None
        if len(self.hs) >= WPR_PERIOD:
            hh = max(self.hs[-WPR_PERIOD:])
            ll = min(self.ls[-WPR_PERIOD:])
            if hh != ll:
                wpr_val = -100.0 * (hh - cl) / (hh - ll)
        
        # ── W%R Velocity & Acceleration ──────────────────────
        vel_val = None
        acc_val = None
        if wpr_val is not None and self.wp1 is not None:
            vel_val = wpr_val - self.wp1
        if vel_val is not None and self.vp is not None:
            acc_val = vel_val - self.vp
        
        # ── Distance ─────────────────────────────────────────
        dist_val = abs(cl - st)
        dist_atr_val = dist_val / self.atr_val if self.atr_val and self.atr_val > 0 else 0.0
        
        # ── Volume Delta ─────────────────────────────────────
        vol_delta = 2.0 * candle.taker_buy_ratio - 1.0
        
        # ── EMA Slope ────────────────────────────────────────
        ema_slope = self.ema_val - (pc if pc is not None else self.ema_val)
        
        # ── Point Status ─────────────────────────────────────
        warmup = self.atr_val is None or self.ema_val is None
        point_status = PointStatus.WARMUP if warmup else PointStatus.VALID
        
        # ── Build TruthPoint ─────────────────────────────────
        tp = TruthPoint(
            ts=candle.time,
            close=cl,
            st=st,
            st_canon=canon(st, 2),
            st_dir=self.trend,
            st_color=color,
            atr=self.atr_val,
            ema=self.ema_val,
            ema12=self.e12,
            ema26=self.e26,
            macd=macd_val,
            macd_signal=self.sig,
            macd_hist=macd_hist,
            rsi=rsi_val,
            wpr=wpr_val,
            vel=vel_val,
            acc=acc_val,
            vol_delta=vol_delta,
            dist=dist_val,
            dist_atr=dist_atr_val,
            flip=flip,
            point_status=point_status,
            oi_value=oi_value,
            oi_delta=oi_delta,
            prev_macd_hist=self.mh1,
            ema_slope=ema_slope,
        )
        
        # ── Update state ─────────────────────────────────────
        self.pc = cl
        self.puf = uf
        self.plf = lf
        self.mh1 = macd_hist
        self.wp1 = wpr_val
        self.vp = vel_val
        self._prev_close = cl
        
        # Prune history arrays
        if len(self.hs) > WPR_PERIOD * 2:
            self.hs = self.hs[-WPR_PERIOD * 2:]
            self.ls = self.ls[-WPR_PERIOD * 2:]
        
        return tp


class TruthArtifact(BaseArtifact):
    """
    Memproduksi truth_snapshot immutable cards dari TruthPoint.
    
    Extends BaseArtifact. Satu card per SP.
    """
    
    def __init__(self):
        super().__init__("TRUTH")
    
    def produce(self, point: TruthPoint) -> Card:
        """Produksi satu truth_snapshot card dari satu SP."""
        if not self.validate_input(point):
            raise ValueError("Invalid TruthPoint")
        
        payload = {
            "ts": point.ts,
            "close": point.close,
            "st": point.st,
            "st_canon": point.st_canon,
            "st_dir": point.st_dir,
            "st_color": point.st_color,
            "atr": point.atr,
            "ema": point.ema,
            "ema12": point.ema12,
            "ema26": point.ema26,
            "macd": point.macd,
            "macd_signal": point.macd_signal,
            "macd_hist": point.macd_hist,
            "rsi": point.rsi,
            "wpr": point.wpr,
            "vel": point.vel,
            "acc": point.acc,
            "vol_delta": point.vol_delta,
            "dist": point.dist,
            "dist_atr": point.dist_atr,
            "flip": point.flip,
            "point_status": point.point_status.value,
            "oi_value": point.oi_value,
            "oi_delta": point.oi_delta,
            "ema_slope": point.ema_slope,
            "wib_iso": wib_iso(point.ts),
        }
        
        return self.make_card("truth_snapshot", payload, [], point.ts)
    
    def validate_input(self, point: TruthPoint) -> bool:
        return point.ts > 0 and point.close > 0
