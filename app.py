import os
import shutil
import zipfile
import tempfile
import platform
import re
import time
from pathlib import Path
from datetime import datetime
from io import BytesIO

from flask import (
    Flask, render_template, request, redirect, url_for,
    send_file, jsonify, flash, abort, session
)

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

ROOT_DIR = Path.home()

ALLOWED_EXTENSIONS = {
    'zip', 'txt', 'csv', 'json', 'md', 'py', 'js', 'html', 'db', 'env', 'sql', 'conf',
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf'
}

TEXT_EXTENSIONS = {'txt', 'md', 'json', 'csv', 'py', 'js', 'log', 'db', 'sql', 'html', 'conf'}
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def safe_path(relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute():
        abort(400, 'Absolute path not allowed')
    resolved = (ROOT_DIR / rel).resolve()
    if not str(resolved).startswith(str(ROOT_DIR.resolve())):
        abort(403, 'Path traversal blocked')
    return resolved


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r'[^\w\.\-\(\) ]', '_', name)
    return name


def format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def get_file_type(path: Path) -> str:
    if path.is_dir():
        return 'folder'
    ext = path.suffix.lower().lstrip('.')
    return ext if ext else 'file'


def list_items(directory: Path, sort_by='', sort_order='asc'):
    entries = []
    for entry in directory.iterdir():
        stat = entry.stat()
        entries.append({'entry': entry, 'stat': stat, 'is_dir': entry.is_dir()})

    if sort_by == 'modified':
        reverse = sort_order == 'desc'
        entries.sort(key=lambda x: x['stat'].st_mtime, reverse=reverse)
    else:
        entries.sort(key=lambda x: (not x['is_dir'], x['entry'].name.lower()))

    items = []
    for e in entries:
        entry = e['entry']
        stat = e['stat']
        ext = entry.suffix.lower().lstrip('.')
        items.append({
            'name': entry.name,
            'type': get_file_type(entry),
            'size': format_size(stat.st_size) if entry.is_file() else '-',
            'modified': format_time(stat.st_mtime),
            'is_dir': entry.is_dir(),
            'is_zip': entry.is_file() and entry.suffix.lower() == '.zip',
            'is_text': entry.is_file() and ext in TEXT_EXTENSIONS,
            'is_image': entry.is_file() and ext in IMAGE_EXTENSIONS,
            'is_html': entry.is_file() and ext == 'html',
        })
    return items


def get_cpu_percent():
    try:
        with open('/proc/stat') as f:
            line = f.readline()
        parts = list(map(int, line.strip().split()[1:]))
        total1 = sum(parts)
        idle1 = parts[3]
        time.sleep(0.15)
        with open('/proc/stat') as f:
            line = f.readline()
        parts = list(map(int, line.strip().split()[1:]))
        total2 = sum(parts)
        idle2 = parts[3]
        used = (total2 - total1) - (idle2 - idle1)
        total_delta = total2 - total1
        if total_delta == 0:
            return 0.0
        return round(used / total_delta * 100, 1)
    except Exception:
        return 0.0


def get_dashboard():
    usage = shutil.disk_usage(ROOT_DIR)
    total_files = 0
    total_dirs = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        try:
            total_dirs += len(dirs)
            total_files += len(files)
        except PermissionError:
            pass
    try:
        with open('/proc/meminfo') as f:
            meminfo = f.read()
        mem_total_kb = int(re.search(r'MemTotal:\s+(\d+)', meminfo).group(1))
        mem_available_kb = int(re.search(r'MemAvailable:\s+(\d+)', meminfo).group(1))
        mem_used_kb = mem_total_kb - mem_available_kb
        ram_percent = round(mem_used_kb / mem_total_kb * 100, 1)
        ram_total_gb = round(mem_total_kb / (1024 * 1024), 1)
        ram_used = format_size(mem_used_kb * 1024)
        ram_total = f"{ram_total_gb} GB"
    except Exception:
        ram_percent = 0.0
        ram_total = '0 GB'
        ram_used = '0 B'

    cpu_percent = get_cpu_percent()

    return {
        'hostname': platform.node(),
        'disk_total': format_size(usage.total),
        'disk_used': format_size(usage.used),
        'disk_free': format_size(usage.free),
        'disk_percent': round(usage.used / usage.total * 100, 1),
        'ram_used': ram_used,
        'ram_total': ram_total,
        'ram_percent': ram_percent,
        'cpu_percent': cpu_percent,
        'total_files': total_files,
        'total_folders': total_dirs,
    }


@app.route('/')
def index():
    raw_path = request.args.get('path', '')
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', '')
    sort_order = request.args.get('order', 'asc')
    error = request.args.get('error', '')
    success = request.args.get('success', '')

    if sort_by not in ('', 'modified'):
        sort_by = ''
    if sort_order not in ('asc', 'desc'):
        sort_order = 'asc'

    try:
        current_dir = safe_path(raw_path)
    except Exception:
        current_dir = ROOT_DIR
        raw_path = ''

    if not current_dir.exists():
        current_dir = ROOT_DIR
        raw_path = ''

    if not current_dir.is_dir():
        current_dir = current_dir.parent
        raw_path = str(current_dir.relative_to(ROOT_DIR)) if current_dir != ROOT_DIR else ''

    items = list_items(current_dir, sort_by, sort_order)

    if search:
        search_lower = search.lower()
        items = [it for it in items if search_lower in it['name'].lower()]

    rel = str(current_dir.relative_to(ROOT_DIR)) if current_dir != ROOT_DIR else ''
    parent_rel = str(Path(rel).parent) if rel else ''
    parent_path = '' if not rel else parent_rel

    breadcrumbs = []
    if rel:
        parts = Path(rel).parts
        acc = ''
        for p in parts:
            acc = f"{acc}/{p}" if acc else p
            breadcrumbs.append({'name': p, 'path': acc})
    else:
        breadcrumbs = []

    dashboard = get_dashboard()

    return render_template(
        'index.html',
        items=items,
        current_path=rel,
        parent_path=parent_path,
        breadcrumbs=breadcrumbs,
        dashboard=dashboard,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        error=error,
        success=success,
        root_name=ROOT_DIR.name,
    )


@app.route('/upload', methods=['POST'])
def upload():
    path = request.form.get('path', '')
    try:
        current_dir = safe_path(path)
    except Exception:
        abort(400)

    if 'files[]' not in request.files:
        return redirect(url_for('index', path=path, error='No file selected'))

    files = request.files.getlist('files[]')
    for f in files:
        if f.filename == '':
            continue
        safe_name = sanitize_filename(f.filename)
        if not safe_name:
            continue
        ext = safe_name.rsplit('.', 1)[-1].lower() if '.' in safe_name else ''
        if ext not in ALLOWED_EXTENSIONS:
            return redirect(url_for('index', path=path, error=f'Extension .{ext} not allowed'))
        f.save(str(current_dir / safe_name))

    return redirect(url_for('index', path=path, success='Upload successful'))


@app.route('/download/<path:relative>')
def download(relative):
    try:
        file_path = safe_path(relative)
    except Exception:
        abort(404)

    if not file_path.exists() or not file_path.is_file():
        abort(404)

    return send_file(str(file_path), as_attachment=True)


@app.route('/download-folder/<path:relative>')
def download_folder(relative):
    try:
        folder_path = safe_path(relative)
    except Exception:
        abort(404)

    if not folder_path.exists() or not folder_path.is_dir():
        abort(404)

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                abs_f = os.path.join(root, f)
                rel_f = os.path.relpath(abs_f, folder_path)
                zf.write(abs_f, rel_f)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{folder_path.name}.zip"
    )


@app.route('/extract', methods=['POST'])
def extract():
    path = request.form.get('path', '')
    zip_name = request.form.get('zip_name', '')
    try:
        current_dir = safe_path(path)
    except Exception:
        abort(400)

    if not zip_name:
        return redirect(url_for('index', path=path, error='No zip file specified'))

    safe_name = Path(zip_name).name
    zip_path = current_dir / safe_name

    if not zip_path.exists() or not zip_path.is_file():
        return redirect(url_for('index', path=path, error='ZIP file not found'))

    extract_dir = current_dir / zip_path.stem
    try:
        extract_dir.mkdir(exist_ok=True)
    except Exception:
        return redirect(url_for('index', path=path, error='Cannot create extract directory'))

    try:
        with zipfile.ZipFile(str(zip_path), 'r') as zf:
            for info in zf.infolist():
                dest_path = (extract_dir / info.filename).resolve()
                if not str(dest_path).startswith(str(extract_dir.resolve())):
                    shutil.rmtree(str(extract_dir), ignore_errors=True)
                    return redirect(url_for('index', path=path, error='ZIP slip detected - extraction blocked'))

                if info.filename.startswith('/') or '..' in info.filename:
                    shutil.rmtree(str(extract_dir), ignore_errors=True)
                    return redirect(url_for('index', path=path, error='Path traversal in ZIP blocked'))

            zf.extractall(str(extract_dir))
    except Exception as e:
        shutil.rmtree(str(extract_dir), ignore_errors=True)
        return redirect(url_for('index', path=path, error=f'Extraction failed: {str(e)}'))

    return redirect(url_for('index', path=path, success=f'Extracted to {zip_path.stem}/'))


@app.route('/create-folder', methods=['POST'])
def create_folder():
    path = request.form.get('path', '')
    folder_name = request.form.get('folder_name', '').strip()
    try:
        current_dir = safe_path(path)
    except Exception:
        abort(400)

    if not folder_name:
        return redirect(url_for('index', path=path, error='Folder name required'))

    safe_name = sanitize_filename(folder_name)
    if not safe_name:
        return redirect(url_for('index', path=path, error='Invalid folder name'))

    try:
        (current_dir / safe_name).mkdir(exist_ok=True)
    except Exception as e:
        return redirect(url_for('index', path=path, error=f'Cannot create folder: {str(e)}'))

    return redirect(url_for('index', path=path, success=f'Folder "{safe_name}" created'))


@app.route('/create-file', methods=['POST'])
def create_file():
    path = request.form.get('path', '')
    file_name = request.form.get('file_name', '').strip()
    try:
        current_dir = safe_path(path)
    except Exception:
        abort(400)

    if not file_name:
        return redirect(url_for('index', path=path, error='File name required'))

    safe_name = sanitize_filename(file_name)
    if not safe_name:
        return redirect(url_for('index', path=path, error='Invalid file name'))

    file_path = current_dir / safe_name
    if file_path.exists():
        return redirect(url_for('index', path=path, error=f'"{safe_name}" already exists'))

    try:
        file_path.touch()
    except Exception as e:
        return redirect(url_for('index', path=path, error=f'Cannot create file: {str(e)}'))

    return redirect(url_for('index', path=path, success=f'File "{safe_name}" created'))


@app.route('/delete', methods=['POST'])
def delete():
    path = request.form.get('path', '')
    item_name = request.form.get('item_name', '').strip()
    try:
        current_dir = safe_path(path)
    except Exception:
        abort(400)

    if not item_name:
        return redirect(url_for('index', path=path, error='No item specified'))

    safe_name = Path(item_name).name
    target = current_dir / safe_name

    if not target.exists():
        return redirect(url_for('index', path=path, error='Item not found'))

    try:
        if target.is_dir():
            shutil.rmtree(str(target))
        else:
            target.unlink()
    except Exception as e:
        return redirect(url_for('index', path=path, error=f'Cannot delete: {str(e)}'))

    return redirect(url_for('index', path=path, success=f'"{safe_name}" deleted'))


@app.route('/rename', methods=['POST'])
def rename():
    path = request.form.get('path', '')
    old_name = request.form.get('old_name', '').strip()
    new_name = request.form.get('new_name', '').strip()
    try:
        current_dir = safe_path(path)
    except Exception:
        abort(400)

    if not old_name or not new_name:
        return redirect(url_for('index', path=path, error='Both names required'))

    safe_old = Path(old_name).name
    safe_new = sanitize_filename(new_name)
    if not safe_new:
        return redirect(url_for('index', path=path, error='Invalid new name'))

    old_path = current_dir / safe_old
    new_path = current_dir / safe_new

    if not old_path.exists():
        return redirect(url_for('index', path=path, error='Original item not found'))
    if new_path.exists():
        return redirect(url_for('index', path=path, error='Target name already exists'))

    try:
        old_path.rename(new_path)
    except Exception as e:
        return redirect(url_for('index', path=path, error=f'Cannot rename: {str(e)}'))

    return redirect(url_for('index', path=path, success=f'Renamed to "{safe_new}"'))


@app.route('/preview/<path:relative>')
def preview(relative):
    try:
        file_path = safe_path(relative)
    except Exception:
        abort(404)

    if not file_path.exists() or not file_path.is_file():
        abort(404)

    ext = file_path.suffix.lower().lstrip('.')
    if ext not in TEXT_EXTENSIONS:
        abort(400, 'Preview not supported for this file type')

    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        content = 'Cannot read file content.'

    return render_template('preview.html', content=content, filename=file_path.name, ext=ext)


@app.route('/edit/<path:relative>', methods=['GET', 'POST'])
def edit(relative):
    try:
        file_path = safe_path(relative)
    except Exception:
        abort(404)

    if not file_path.exists() or not file_path.is_file():
        abort(404)

    ext = file_path.suffix.lower().lstrip('.')
    if ext not in TEXT_EXTENSIONS:
        abort(400, 'Editing not supported for this file type')

    if request.method == 'POST':
        content = request.form.get('content', '')
        try:
            file_path.write_text(content, encoding='utf-8')
        except Exception as e:
            parent_rel = str(file_path.parent.relative_to(ROOT_DIR)) if file_path.parent != ROOT_DIR else ''
            return redirect(url_for('index', path=parent_rel, error=f'Save failed: {str(e)}'))

        parent_rel = str(file_path.parent.relative_to(ROOT_DIR)) if file_path.parent != ROOT_DIR else ''
        return redirect(url_for('index', path=parent_rel, success=f'"{file_path.name}" saved'))

    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        content = 'Cannot read file content.'

    return render_template('editor.html', content=content, filename=file_path.name, ext=ext, relative=relative)


@app.route('/image/<path:relative>')
def image(relative):
    try:
        file_path = safe_path(relative)
    except Exception:
        abort(404)

    if not file_path.exists() or not file_path.is_file():
        abort(404)

    ext = file_path.suffix.lower().lstrip('.')
    if ext not in IMAGE_EXTENSIONS:
        abort(400)

    mimetypes = {
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'
    }

    return send_file(str(file_path), mimetype=mimetypes.get(ext, 'application/octet-stream'))


@app.route('/run-html/<path:relative>')
def run_html(relative):
    try:
        file_path = safe_path(relative)
    except Exception:
        abort(404)

    if not file_path.exists() or not file_path.is_file():
        abort(404)

    ext = file_path.suffix.lower().lstrip('.')
    if ext != 'html':
        abort(400, 'Not an HTML file')

    return send_file(str(file_path), mimetype='text/html')


@app.errorhandler(413)
def too_large(e):
    return render_template('index.html',
        error='File too large. Maximum is 500MB.',
        items=[], current_path='', parent_path='', breadcrumbs=[],
        dashboard=get_dashboard(), search='', success='', root_name=ROOT_DIR.name), 413


@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('index', error='Resource not found'))


@app.errorhandler(403)
def forbidden(e):
    return redirect(url_for('index', error='Access denied'))


@app.errorhandler(400)
def bad_request(e):
    return redirect(url_for('index', error=str(e)))


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=8081, debug=True)
