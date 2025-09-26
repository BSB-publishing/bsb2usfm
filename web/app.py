#!/usr/bin/env python3

import os
import sys
import tempfile
import zipfile
import logging
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import subprocess
from subprocess import TimeoutExpired
import shutil
import glob

# Add the parent directory to the path so we can import bsb2usfm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.environ.get('OUTPUT_FOLDER', 'outputs')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure logging
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    app.logger.setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Detect if running on Render free tier
IS_RENDER_FREE = os.environ.get('RENDER_SERVICE_TYPE') == 'web' and os.environ.get('RENDER_SERVICE_PLAN', 'free') == 'free'

app.logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
app.logger.info(f"Output folder: {app.config['OUTPUT_FOLDER']}")
app.logger.info(f"Max file size: {app.config['MAX_CONTENT_LENGTH']} bytes")
if IS_RENDER_FREE:
    app.logger.info("Running on Render free tier - using conservative resource settings")

# Cleanup configuration (configurable via environment variables)
# Use more conservative defaults for Render free tier
default_storage_mb = 15 if IS_RENDER_FREE else 100
default_file_age = 1800 if IS_RENDER_FREE else 3600  # 30 min vs 1 hour
default_interval = 180 if IS_RENDER_FREE else 300    # 3 min vs 5 min

CLEANUP_INTERVAL = int(os.environ.get('CLEANUP_INTERVAL', default_interval))
MAX_FILE_AGE = int(os.environ.get('MAX_FILE_AGE', default_file_age))
MAX_TOTAL_SIZE = int(os.environ.get('MAX_STORAGE_MB', default_storage_mb)) * 1024 * 1024
CLEANUP_AFTER_DOWNLOAD = int(os.environ.get('CLEANUP_DELAY', 15 if IS_RENDER_FREE else 30))

ALLOWED_EXTENSIONS = {'csv', 'tsv', 'xml'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_book_codes():
    """Return list of available book codes"""
    return [
        'GEN', 'EXO', 'LEV', 'NUM', 'DEU', 'JOS', 'JDG', 'RUT',
        '1SA', '2SA', '1KI', '2KI', '1CH', '2CH', 'EZR',
        'NEH', 'EST', 'JOB', 'PSA', 'PRO', 'ECC', 'SNG',
        'ISA', 'JER', 'LAM', 'EZK', 'DAN', 'HOS', 'JOL', 'AMO',
        'OBA', 'JON', 'MIC', 'NAM', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL',
        'MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', '1CO', '2CO',
        'GAL', 'EPH', 'PHP', 'COL', '1TH', '2TH',
        '1TI', '2TI', 'TIT', 'PHM', 'HEB', 'JAS', '1PE', '2PE',
        '1JN', '2JN', '3JN', 'JUD', 'REV'
    ]

def cleanup_old_files():
    """Remove files older than MAX_FILE_AGE and enforce size limits"""
    try:
        current_time = time.time()
        total_size = 0
        file_list = []

        # Scan both upload and output directories
        for directory in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
            if not os.path.exists(directory):
                continue

            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file == '.gitkeep':  # Skip .gitkeep files
                        continue

                    file_path = os.path.join(root, file)
                    try:
                        file_stat = os.stat(file_path)
                        file_age = current_time - file_stat.st_mtime
                        file_size = file_stat.st_size

                        file_list.append({
                            'path': file_path,
                            'age': file_age,
                            'size': file_size,
                            'mtime': file_stat.st_mtime
                        })
                        total_size += file_size

                    except (OSError, IOError):
                        continue

        files_removed = 0
        size_freed = 0

        # Remove files older than MAX_FILE_AGE
        for file_info in file_list[:]:
            if file_info['age'] > MAX_FILE_AGE:
                try:
                    os.remove(file_info['path'])
                    files_removed += 1
                    size_freed += file_info['size']
                    total_size -= file_info['size']
                    file_list.remove(file_info)
                    app.logger.info(f"Removed old file: {file_info['path']}")
                except (OSError, IOError) as e:
                    app.logger.warning(f"Failed to remove old file {file_info['path']}: {e}")

        # If total size exceeds limit, remove oldest files first
        if total_size > MAX_TOTAL_SIZE:
            file_list.sort(key=lambda x: x['mtime'])  # Sort by modification time (oldest first)

            for file_info in file_list:
                if total_size <= MAX_TOTAL_SIZE:
                    break

                try:
                    os.remove(file_info['path'])
                    files_removed += 1
                    size_freed += file_info['size']
                    total_size -= file_info['size']
                    app.logger.info(f"Removed file for size limit: {file_info['path']}")
                except (OSError, IOError) as e:
                    app.logger.warning(f"Failed to remove file {file_info['path']}: {e}")

        # Clean up empty directories (except the base directories)
        for directory in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
            if not os.path.exists(directory):
                continue

            for root, dirs, files in os.walk(directory, topdown=False):
                # Don't remove the base upload/output directories themselves
                if root == directory:
                    continue

                try:
                    # Only remove if directory is empty (except for .gitkeep)
                    remaining_files = [f for f in os.listdir(root) if f != '.gitkeep']
                    if not remaining_files and not os.listdir(root):
                        os.rmdir(root)
                        app.logger.info(f"Removed empty directory: {root}")
                except (OSError, IOError):
                    pass  # Directory not empty or other issue, skip

        if files_removed > 0:
            app.logger.info(f"Cleanup completed: removed {files_removed} files, freed {size_freed/1024/1024:.1f}MB")

        return files_removed, size_freed

    except Exception as e:
        app.logger.error(f"Error during cleanup: {e}")
        return 0, 0

def cleanup_thread():
    """Background thread to periodically clean up old files"""
    while True:
        time.sleep(CLEANUP_INTERVAL)
        cleanup_old_files()

def cleanup_job_files(job_id):
    """Clean up files for a specific job immediately after download"""
    try:
        job_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], job_id)
        job_output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)

        files_removed = 0

        for directory in [job_upload_dir, job_output_dir]:
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    files_removed += 1
                    app.logger.info(f"Cleaned up job directory: {directory}")
                except (OSError, IOError) as e:
                    app.logger.warning(f"Failed to remove job directory {directory}: {e}")

        return files_removed > 0

    except Exception as e:
        app.logger.error(f"Error cleaning up job {job_id}: {e}")
        return False

@app.route('/')
def index():
    # Trigger immediate cleanup on cold start (Render free tier)
    if IS_RENDER_FREE:
        threading.Thread(target=cleanup_old_files, daemon=True).start()
    return render_template('index.html', book_codes=get_book_codes())

@app.route('/convert', methods=['POST'])
def convert_files():
    job_id = None
    try:
        # Pre-conversion cleanup for free tier
        if IS_RENDER_FREE:
            cleanup_old_files()

        # Create a unique directory for this conversion
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        job_id = f"conversion_{timestamp}"
        job_dir = os.path.join(app.config['UPLOAD_FOLDER'], job_id)
        os.makedirs(job_dir, exist_ok=True)

        app.logger.info(f"Starting conversion job {job_id}")

        # Use the fixed BSB tables file
        bsb_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'bsb_tables.csv')
        if not os.path.exists(bsb_filepath):
            app.logger.error(f"BSB tables file not found at: {bsb_filepath}")
            flash('BSB tables file not found. Please ensure data/bsb_tables.csv exists.')
            return redirect(url_for('index'))

        # Handle optional files
        fnotes_filepath = None
        if 'fnotes' in request.files and request.files['fnotes'].filename:
            fnotes_file = request.files['fnotes']
            if allowed_file(fnotes_file.filename):
                fnotes_filename = secure_filename(fnotes_file.filename)
                fnotes_filepath = os.path.join(job_dir, fnotes_filename)
                fnotes_file.save(fnotes_filepath)

        names_filepath = None
        if 'names' in request.files and request.files['names'].filename:
            names_file = request.files['names']
            if allowed_file(names_file.filename):
                names_filename = secure_filename(names_file.filename)
                names_filepath = os.path.join(job_dir, names_filename)
                names_file.save(names_filepath)

        # Get form parameters
        output_template = request.form.get('output_template', 'output_%.usfm')
        selected_books = request.form.getlist('books')

        app.logger.info(f"Conversion parameters - Books: {selected_books}, Template: {output_template}")

        # Create output directory
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
        os.makedirs(output_dir, exist_ok=True)

        # Build the command
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bsb2usfm.py')
        output_path = os.path.join(output_dir, output_template)

        # Use absolute paths to avoid issues
        script_path = os.path.abspath(script_path)
        bsb_filepath = os.path.abspath(bsb_filepath)
        output_path = os.path.abspath(output_path)

        # Build command with virtual environment python
        venv_python = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv', 'bin', 'python3')
        if os.path.exists(venv_python):
            python_cmd = venv_python
        else:
            python_cmd = 'python3'

        cmd = [python_cmd, script_path, bsb_filepath, '-o', output_path]

        if fnotes_filepath:
            cmd.extend(['-f', os.path.abspath(fnotes_filepath)])

        if names_filepath:
            cmd.extend(['-n', os.path.abspath(names_filepath)])

        if selected_books:
            for book in selected_books:
                cmd.extend(['-b', book])

        # Run the conversion
        app.logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True,
                              cwd=os.path.dirname(script_path), timeout=300)

        # Schedule cleanup of old files during conversion (more aggressive on free tier)
        if IS_RENDER_FREE:
            # Immediate cleanup on free tier (no background thread)
            cleanup_old_files()
        else:
            # Background cleanup on paid tiers
            threading.Thread(target=cleanup_old_files, daemon=True).start()

        if result.returncode == 0:
            # Check for generated files
            output_files = glob.glob(os.path.join(output_dir, '*.usfm'))
            app.logger.info(f"Conversion successful. Generated {len(output_files)} files")

            if output_files:
                # Create a zip file with all output files
                zip_path = os.path.join(output_dir, f'{job_id}_output.zip')
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file_path in output_files:
                        if os.path.isfile(file_path):
                            zipf.write(file_path, os.path.basename(file_path))

                flash('Conversion completed successfully!')
                return render_template('result.html',
                                     job_id=job_id,
                                     output_files=output_files,
                                     stdout=result.stdout,
                                     stderr=result.stderr)
            else:
                app.logger.warning("Conversion completed but no output files were generated")
                flash('Conversion completed but no output files were generated')
                return render_template('result.html',
                                     job_id=job_id,
                                     stdout=result.stdout,
                                     stderr=result.stderr,
                                     error=True)
        else:
            app.logger.error(f"Conversion failed with return code {result.returncode}")
            app.logger.error(f"STDERR: {result.stderr}")
            flash(f'Conversion failed with return code {result.returncode}')
            return render_template('result.html',
                                 job_id=job_id,
                                 stdout=result.stdout,
                                 stderr=result.stderr,
                                 error=True)

    except TimeoutExpired:
        app.logger.error(f"Conversion job {job_id} timed out after 5 minutes")
        flash('Conversion timed out after 5 minutes. Try converting fewer books.')
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error during conversion job {job_id}: {str(e)}", exc_info=True)
        flash(f'Error during conversion: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download/<job_id>')
def download_result(job_id):
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
    zip_path = os.path.join(output_dir, f'{job_id}_output.zip')

    if os.path.exists(zip_path):
        def cleanup_after_download():
            """Clean up files after a short delay to ensure download completes"""
            time.sleep(CLEANUP_AFTER_DOWNLOAD)  # Wait for download to complete
            cleanup_job_files(job_id)

        # Schedule cleanup after download (only create thread if not free tier)
        if IS_RENDER_FREE:
            # On free tier, clean up immediately after a shorter delay
            time.sleep(5)  # Quick delay then immediate cleanup
            cleanup_job_files(job_id)
        else:
            threading.Thread(target=cleanup_after_download, daemon=True).start()

        return send_file(zip_path, as_attachment=True, download_name=f'{job_id}_usfm_files.zip')
    else:
        flash('Output file not found')
        return redirect(url_for('index'))

@app.route('/download_single/<job_id>/<filename>')
def download_single_file(job_id, filename):
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
    file_path = os.path.join(output_dir, secure_filename(filename))

    if os.path.exists(file_path) and filename.endswith('.usfm'):
        def cleanup_after_download():
            """Clean up job files after single file download"""
            time.sleep(CLEANUP_AFTER_DOWNLOAD)  # Wait for download to complete
            cleanup_job_files(job_id)

        # Schedule cleanup after download (only create thread if not free tier)
        if IS_RENDER_FREE:
            # On free tier, clean up immediately after a shorter delay
            time.sleep(5)  # Quick delay then immediate cleanup
            cleanup_job_files(job_id)
        else:
            threading.Thread(target=cleanup_after_download, daemon=True).start()

        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('index'))

@app.route('/api/books')
def api_books():
    """API endpoint to get available book codes"""
    return jsonify(get_book_codes())

@app.route('/admin/cleanup', methods=['POST'])
def manual_cleanup():
    """Manual cleanup endpoint for administrators"""
    try:
        # Simple authentication check - require a cleanup token
        cleanup_token = request.headers.get('X-Cleanup-Token') or request.form.get('cleanup_token')
        expected_token = os.environ.get('CLEANUP_TOKEN')

        if not expected_token:
            return jsonify({"error": "Cleanup not configured"}), 501

        if cleanup_token != expected_token:
            return jsonify({"error": "Unauthorized"}), 401

        files_removed, size_freed = cleanup_old_files()

        return jsonify({
            "status": "success",
            "files_removed": files_removed,
            "size_freed_mb": round(size_freed / 1024 / 1024, 2),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        app.logger.error(f"Manual cleanup failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/admin/status')
def admin_status():
    """Get detailed system status for administrators"""
    try:
        # Simple authentication check
        status_token = request.headers.get('X-Status-Token') or request.args.get('status_token')
        expected_token = os.environ.get('CLEANUP_TOKEN')  # Reuse same token

        if expected_token and status_token != expected_token:
            return jsonify({"error": "Unauthorized"}), 401

        # Calculate detailed disk usage
        upload_size = 0
        upload_files = 0
        output_size = 0
        output_files = 0

        for directory, size_var, count_var in [
            (app.config['UPLOAD_FOLDER'], 'upload_size', 'upload_files'),
            (app.config['OUTPUT_FOLDER'], 'output_size', 'output_files')
        ]:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file != '.gitkeep':
                            try:
                                file_path = os.path.join(root, file)
                                file_size = os.path.getsize(file_path)
                                if 'upload' in directory:
                                    upload_size += file_size
                                    upload_files += 1
                                else:
                                    output_size += file_size
                                    output_files += 1
                            except (OSError, IOError):
                                pass

        total_size = upload_size + output_size
        total_files = upload_files + output_files

        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "disk_usage": {
                "total_files": total_files,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "upload_files": upload_files,
                "upload_size_mb": round(upload_size / 1024 / 1024, 2),
                "output_files": output_files,
                "output_size_mb": round(output_size / 1024 / 1024, 2),
                "size_limit_mb": round(MAX_TOTAL_SIZE / 1024 / 1024, 2),
                "usage_percent": round((total_size / MAX_TOTAL_SIZE) * 100, 1) if MAX_TOTAL_SIZE > 0 else 0
            },
            "cleanup_config": {
                "cleanup_interval_seconds": CLEANUP_INTERVAL,
                "max_file_age_seconds": MAX_FILE_AGE,
                "cleanup_after_download_seconds": CLEANUP_AFTER_DOWNLOAD
            }
        })

    except Exception as e:
        app.logger.error(f"Status check failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring services"""
    try:
        # Check if critical files exist
        bsb_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'bsb_tables.csv')
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bsb2usfm.py')

        # Calculate disk usage
        total_size = 0
        file_count = 0
        for directory in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file != '.gitkeep':
                            try:
                                file_path = os.path.join(root, file)
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                            except (OSError, IOError):
                                pass

        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "bsb_tables_exists": os.path.exists(bsb_filepath),
                "conversion_script_exists": os.path.exists(script_path),
                "upload_dir_writable": os.access(app.config['UPLOAD_FOLDER'], os.W_OK),
                "output_dir_writable": os.access(app.config['OUTPUT_FOLDER'], os.W_OK)
            },
            "disk_usage": {
                "total_files": file_count,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "size_limit_mb": round(MAX_TOTAL_SIZE / 1024 / 1024, 2),
                "usage_percent": round((total_size / MAX_TOTAL_SIZE) * 100, 1) if MAX_TOTAL_SIZE > 0 else 0
            }
        }

        # Add free tier specific info
        if IS_RENDER_FREE:
            health_status["render_free_tier"] = {
                "aggressive_cleanup": True,
                "memory_limit_mb": 512,
                "storage_limit_mb": round(MAX_TOTAL_SIZE / 1024 / 1024, 1),
                "cleanup_interval_seconds": CLEANUP_INTERVAL
            }

        # If any critical check fails, mark as unhealthy
        if not all(health_status["checks"].values()):
            health_status["status"] = "unhealthy"
            return jsonify(health_status), 503

        return jsonify(health_status)
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 503

# Error handlers for production
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {str(error)}")
    flash('An internal error occurred. Please try again.')
    return render_template('index.html'), 500

@app.errorhandler(413)
def too_large(error):
    flash('File too large. Maximum file size is 16MB.')
    return render_template('index.html'), 413

# Start background cleanup thread (only on paid tiers to save memory)
if not IS_RENDER_FREE:
    cleanup_background_thread = threading.Thread(target=cleanup_thread, daemon=True)
    cleanup_background_thread.start()
    app.logger.info(f"Background cleanup thread started - Interval: {CLEANUP_INTERVAL}s, Max age: {MAX_FILE_AGE}s, Max size: {MAX_TOTAL_SIZE/1024/1024}MB")
else:
    app.logger.info("Free tier: background cleanup disabled, using immediate cleanup instead")
    app.logger.info("Free tier optimizations enabled: aggressive cleanup, reduced limits, minimal threads")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.logger.info(f"Starting application on port {port}, debug={debug}")
    app.run(debug=debug, host='0.0.0.0', port=port)
