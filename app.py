import socket
import os
import time

from flask import Flask, request, render_template_string, render_template, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import desc
from waitress import serve

# Config
from config import DevConfig, ProdConfig

app = Flask(__name__)

# Change to ProdConfig or DevConfig
app.config.from_object(ProdConfig)

SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_TRACK_MODIFICATIONS = app.config['SQLALCHEMY_TRACK_MODIFICATIONS']
SECRET_KEY = app.config['SECRET_KEY']
IMAGE_MNT_LOCATION = app.config['IMAGE_MNT_LOCATION']

db = SQLAlchemy(app)

class Plates(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Corrected syntax here
    detection_time = db.Column(db.String, nullable=False)
    score = db.Column(db.Float, nullable=False)
    plate_number = db.Column(db.String, nullable=False)
    frigate_event = db.Column(db.String, nullable=True)
    camera_name = db.Column(db.String, nullable=True)
    has_image = db.Column(db.String, nullable=True)

@app.route('/')
def index():
    # Redirect to the menu page instead of directly to the search page
    return redirect(url_for('menu'))

# Assuming /mnt/plates is the directory where images are stored
@app.route('/plates/<filename>')
def serve_plate_image(filename):
#    return send_from_directory('/mnt/plates', filename)
    return send_from_directory(app.config['IMAGE_MNT_LOCATION'], filename)

@app.route('/menu')
def menu():
    log_file_path = app.config['LOG_FILE_PATH']
    try:
        with open(log_file_path, 'r') as file:
            all_logs = file.readlines()
            error_logs = [log for log in all_logs if "ERROR" in log][-5:]  # Adjust the slice as needed
            error_logs = error_logs[::-1]  # Reverse for chronological order
    except Exception as e:
        error_logs = [f"Error reading log file: {e}"]
    error_log_html = '<br>'.join(error_logs)

    # Retrieve the last 5 detected license plates
    results = Plates.query.order_by(desc(Plates.detection_time)).limit(5).all()

    error_log_html = '<br>'.join(error_logs)
    return render_template('main.html', error_log_html=error_log_html, results=results)

@app.route('/search_page', methods=['GET'])
def search_page():
    return render_template('search_page.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']

    search_term = search_term.replace('*', '%')

    if not search_term.startswith('%'):
        search_term = '%' + search_term
    if not search_term.endswith('%'):
        search_term += '%'

    results = Plates.query.filter(Plates.plate_number.like(f'%{search_term}%')).order_by(Plates.detection_time.desc()).all()
    return render_template('search_results.html', results=results)

@app.route('/allplates')
def all_plates():
    directory = app.config['IMAGE_MNT_LOCATION']
    total_size = 0
    file_count = 0
    try:
        # List all files in the directory
        files = os.listdir(directory)
        # Filter and calculate file count and total size
        image_files = []
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(directory, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
                mod_time = os.path.getmtime(file_path)
                image_files.append((file, mod_time))
        # Sort the list by modification time in descending order
        image_files.sort(key=lambda x: x[1], reverse=True)
        image_files = [(file, time.ctime(mod_time)) for file, mod_time in image_files]
    except Exception as e:
        image_files = [f"Error accessing directory: {e}", '']
        total_size = 0
        file_count = 0

    return render_template('allplates.html', image_files=image_files, total_size=total_size, file_count=file_count)

@app.route('/logs')
def all_logs():
    log_file_path = app.config['LOG_FILE_PATH']
    try:
        with open(log_file_path, 'r') as file:
            # Read the last 50 lines of the log file
            logs = file.readlines()[-50:]
            logs = logs[::-1]
    except Exception as e:
        logs = [f"Error reading log file: {e}"]
    log_html = '<br>'.join(logs)
    return render_template('logs.html', log_html=log_html)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    ip_address = get_ip()
    serve(app, host=ip_address, port=5555)
    # To debug app
#    app.run(host=ip_address, port=5000, debug=True)
