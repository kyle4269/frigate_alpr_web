import socket
import os

from flask import Flask, request, render_template_string, render_template, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from waitress import serve

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/lpr/dev/config/frigate_plate_recogizer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    return send_from_directory('/mnt/plates', filename)

@app.route('/menu')
def menu():
    return render_template_string('''
        <!doctype html>
        <html>
        <head>
            <title>Main Menu</title>
            <style>
                body {
                    font-size: 35px; /* Increase font size for the menu */
                }
                /* Add additional styling here as needed */
            </style>
        </head>
        <body>
            <h1>Main Menu</h1>
            <ul>
                <li><a href="/search_page">Search License Plates</a></li>
                <li><a href="/logs">View Logs</a></li>
            </ul>
        </body>
        </html>
    ''')

@app.route('/search_page', methods=['GET'])
def search_page():
    return render_template_string('''
        <!doctype html>
        <html>
        <head>
            <title>Plate Search</title>
            <style>
                body {
                    font-family: Arial, sans-serif; /* Change the font of the entire body */
                }

                h1 {
                    font-family: 'Georgia', serif; /* Specific font for the title */
                    font-size: 35px; /* Increase font size */
                    color: #333; /* Change the color */
                }


                input[type="text"] {
                    font-size: 25px; /* Increase font size */
                    width: 200px; /* Increase width */
                    padding: 10px; /* Add more padding */
                    margin: 10px 0; /* Add margin */
                }

                input[type="submit"] {
                    font-size: 25px; /* Increase font size */
                    padding: 10px 20px; /* Increase padding */
                    cursor: pointer; /* Change cursor on hover */
                }
            </style>
        </head>
        <body>
            <h1>Search License Plates</h1>
            <form action="/search" method="post">
                <input type="text" name="search_term" placeholder="Enter plate number...">
                <input type="submit" value="Search">
            </form>
        </body>
        </html>
    ''')

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

@app.route('/logs')
def logs():
    log_file_path = '/home/lpr/dev/config/frigate_plate_recogizer.log'
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
#    serve(app, host=ip_address, port=5555)
    # To debug app
    app.run(host=ip_address, port=5000, debug=True)
