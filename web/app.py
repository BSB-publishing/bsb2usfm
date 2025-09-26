#!/usr/bin/env python3

import os
import sys
import tempfile
import zipfile
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import subprocess
from subprocess import TimeoutExpired
import shutil
import glob

# Add the parent directory to the path so we can import bsb2usfm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

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

@app.route('/')
def index():
    return render_template('index.html', book_codes=get_book_codes())

@app.route('/convert', methods=['POST'])
def convert_files():
    try:
        # Create a unique directory for this conversion
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        job_id = f"conversion_{timestamp}"
        job_dir = os.path.join(app.config['UPLOAD_FOLDER'], job_id)
        os.makedirs(job_dir, exist_ok=True)

        # Use the fixed BSB tables file
        bsb_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'bsb_tables.csv')
        if not os.path.exists(bsb_filepath):
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
        result = subprocess.run(cmd, capture_output=True, text=True,
                              cwd=os.path.dirname(script_path), timeout=300)

        if result.returncode == 0:
            # Check for generated files
            output_files = glob.glob(os.path.join(output_dir, '*.usfm'))

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
                flash('Conversion completed but no output files were generated')
                return render_template('result.html',
                                     job_id=job_id,
                                     stdout=result.stdout,
                                     stderr=result.stderr,
                                     error=True)
        else:
            flash(f'Conversion failed with return code {result.returncode}')
            return render_template('result.html',
                                 job_id=job_id,
                                 stdout=result.stdout,
                                 stderr=result.stderr,
                                 error=True)

    except TimeoutExpired:
        flash('Conversion timed out after 5 minutes. Try converting fewer books.')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error during conversion: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download/<job_id>')
def download_result(job_id):
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
    zip_path = os.path.join(output_dir, f'{job_id}_output.zip')

    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name=f'{job_id}_usfm_files.zip')
    else:
        flash('Output file not found')
        return redirect(url_for('index'))

@app.route('/download_single/<job_id>/<filename>')
def download_single_file(job_id, filename):
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
    file_path = os.path.join(output_dir, secure_filename(filename))

    if os.path.exists(file_path) and filename.endswith('.usfm'):
        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('index'))

@app.route('/api/books')
def api_books():
    """API endpoint to get available book codes"""
    return jsonify(get_book_codes())

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
