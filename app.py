from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = ''
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/submit')
def submit():
    return render_template('submit.html')

@app.route('/upload', methods=['GET','POST'])
def upload(username):
    os.system("mkdir "+username)
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            return render_template('submit.html')
    return render_template('submit.html')


if __name__ == '__main__':
    app.run(debug=True)

