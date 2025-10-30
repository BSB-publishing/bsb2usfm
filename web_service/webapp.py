#!/usr/bin/env python3
"""
BSB2USFM Web Interface
A Flask web application that provides a simple UI for triggering BSB to USFM conversion.
"""

import os
import sys
import json
import threading
import queue
import time
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, Response, request, send_file
import subprocess
import glob
import zipfile
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Detect if running in production
IS_PRODUCTION = os.environ.get('RENDER') or os.environ.get('FLY_APP_NAME')
if IS_PRODUCTION:
    logger.info("Running in PRODUCTION mode")
else:
    logger.info("Running in DEVELOPMENT mode")

# Global state for tracking conversion progress
conversion_state = {
    'running': False,
    'progress': [],
    'status': 'idle',
    'start_time': None,
    'end_time': None,
    'error': None,
    'results': []
}
progress_queue = queue.Queue()
state_lock = threading.Lock()


def log_progress(message, level='info'):
    """Add a progress message to the queue"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = {
        'timestamp': timestamp,
        'message': message,
        'level': level
    }
    with state_lock:
        conversion_state['progress'].append(entry)
    progress_queue.put(entry)
    
    # Log to both stderr and Python logger
    print(f"[{timestamp}] [{level.upper()}] {message}", file=sys.stderr)
    if level == 'error':
        logger.error(message)
    elif level == 'warning':
        logger.warning(message)
    else:
        logger.info(message)


def run_conversion(args=None):
    """Run the BSB to USFM conversion in a background thread"""
    global conversion_state
    
    try:
        with state_lock:
            conversion_state['running'] = True
            conversion_state['status'] = 'running'
            conversion_state['start_time'] = datetime.now().isoformat()
            conversion_state['error'] = None
            conversion_state['progress'] = []
            conversion_state['results'] = []
        
        log_progress("Starting BSB to USFM conversion...")
        
        # Build command
        cmd = ['python3', 'bsb2usfm.py']
        
        # Add default output path if not specified
        if args is None:
            args = {}
        
        # Get format from args, default to 'usfm'
        format_ext = args.get('format', 'usfm')
        output_path = args.get('output', f'/app/output/%.{format_ext}')
        cmd.extend(['-o', output_path])
        
        # Add book filters if specified
        if 'books' in args and args['books']:
            for book in args['books']:
                cmd.extend(['-b', book])
        
        # Add interlinear flag if specified
        if args.get('interlinear', False):
            cmd.append('-I')
        
        # Add Strong's numbers if specified
        if args.get('strongs', False):
            cmd.append('-S')
        
        # Add placeholders if specified
        if args.get('placeholders', False):
            cmd.append('-P')
        
        # Add brackets if specified
        if args.get('brackets', False):
            cmd.append('-B')
        
        log_progress(f"Running command: {' '.join(cmd)}")
        
        # Run the conversion
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output
        for line in process.stdout:
            line = line.strip()
            if line:
                log_progress(line, 'info')
        
        # Wait for completion
        return_code = process.wait()
        
        if return_code != 0:
            raise Exception(f"Conversion failed with return code {return_code}")
        
        log_progress("Conversion completed successfully!")
        
        # List generated files based on format
        output_dir = '/app/output'
        format_ext = args.get('format', 'usfm')
        usfm_files = glob.glob(os.path.join(output_dir, f'*.{format_ext}'))
        
        if usfm_files:
            log_progress(f"Generated {len(usfm_files)} {format_ext.upper()} files:")
            results = []
            for filepath in sorted(usfm_files):
                filename = os.path.basename(filepath)
                size = os.path.getsize(filepath)
                results.append({
                    'filename': filename,
                    'size': size,
                    'path': filepath
                })
                log_progress(f"  - {filename} ({size} bytes)", 'success')
            
            with state_lock:
                conversion_state['results'] = results
        else:
            log_progress(f"No {format_ext.upper()} files were generated", 'warning')
        
        with state_lock:
            conversion_state['status'] = 'completed'
            conversion_state['end_time'] = datetime.now().isoformat()
        
    except Exception as e:
        error_msg = str(e)
        log_progress(f"Error: {error_msg}", 'error')
        with state_lock:
            conversion_state['status'] = 'error'
            conversion_state['error'] = error_msg
            conversion_state['end_time'] = datetime.now().isoformat()
    
    finally:
        with state_lock:
            conversion_state['running'] = False


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current conversion status"""
    with state_lock:
        return jsonify({
            'running': conversion_state['running'],
            'status': conversion_state['status'],
            'start_time': conversion_state['start_time'],
            'end_time': conversion_state['end_time'],
            'error': conversion_state['error'],
            'progress_count': len(conversion_state['progress']),
            'results': conversion_state['results']
        })


@app.route('/api/progress')
def get_progress():
    """Get full progress history"""
    with state_lock:
        return jsonify({
            'progress': conversion_state['progress'],
            'status': conversion_state['status']
        })


@app.route('/api/progress/stream')
def progress_stream():
    """Server-Sent Events stream for real-time progress updates"""
    def event_stream():
        # Send initial state
        with state_lock:
            for entry in conversion_state['progress']:
                yield f"data: {json.dumps(entry)}\n\n"
        
        # Stream new updates
        while True:
            try:
                # Wait for new progress with timeout
                entry = progress_queue.get(timeout=30)
                yield f"data: {json.dumps(entry)}\n\n"
                
                # Check if conversion is done
                with state_lock:
                    if not conversion_state['running'] and conversion_state['status'] in ['completed', 'error']:
                        # Send final status after a short delay
                        time.sleep(0.5)
                        yield f"data: {json.dumps({'type': 'complete', 'status': conversion_state['status']})}\n\n"
                        break
            except queue.Empty:
                # Send keepalive
                yield f": keepalive\n\n"
                
                # Check if we should stop streaming
                with state_lock:
                    if not conversion_state['running'] and conversion_state['status'] in ['completed', 'error']:
                        break
    
    return Response(event_stream(), mimetype='text/event-stream')


@app.route('/api/update', methods=['POST'])
def trigger_update():
    """Trigger the data update/conversion process"""
    with state_lock:
        if conversion_state['running']:
            return jsonify({
                'success': False,
                'error': 'Conversion is already running'
            }), 400
    
    # Get optional parameters from request
    args = {}
    if request.is_json:
        data = request.get_json()
        format_ext = data.get('format', 'usfm')
        args = {
            'format': format_ext,
            'output': data.get('output', f'/app/output/%.{format_ext}'),
            'books': data.get('books', []),
            'interlinear': data.get('interlinear', False),
            'strongs': data.get('strongs', False),
            'placeholders': data.get('placeholders', False),
            'brackets': data.get('brackets', False)
        }
    
    # Start conversion in background thread
    thread = threading.Thread(target=run_conversion, args=(args,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Conversion started'
    })


@app.route('/api/results')
def get_results():
    """Get list of generated USFM files"""
    output_dir = '/app/output'
    # Check all possible formats
    usfm_files = []
    for ext in ['usfm', 'usx', 'usj']:
        usfm_files.extend(glob.glob(os.path.join(output_dir, f'*.{ext}')))
    
    results = []
    for filepath in sorted(usfm_files):
        filename = os.path.basename(filepath)
        size = os.path.getsize(filepath)
        mtime = os.path.getmtime(filepath)
        results.append({
            'filename': filename,
            'size': size,
            'modified': datetime.fromtimestamp(mtime).isoformat()
        })
    
    return jsonify({
        'count': len(results),
        'files': results
    })


@app.route('/api/download')
def download_zip():
    """Download all generated USFM files as a zip archive"""
    output_dir = '/app/output'
    # Check all possible formats
    usfm_files = []
    detected_format = 'usfm'
    for ext in ['usfm', 'usx', 'usj']:
        files = glob.glob(os.path.join(output_dir, f'*.{ext}'))
        if files:
            detected_format = ext
            usfm_files.extend(files)
    
    if not usfm_files:
        return jsonify({
            'success': False,
            'error': 'No output files found'
        }), 404
    
    # Create zip file in memory
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filepath in sorted(usfm_files):
            filename = os.path.basename(filepath)
            zf.write(filepath, filename)
    
    # Seek to the beginning of the file
    memory_file.seek(0)
    
    # Generate filename with timestamp and format
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'bsb_{detected_format}_{timestamp}.zip'
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': 'production' if IS_PRODUCTION else 'development',
        'conversion_running': conversion_state.get('running', False)
    })


if __name__ == '__main__':
    # Ensure output directory exists
    output_dir = '/app/output'
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    
    # Get port from environment
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting web service on port {port}")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)