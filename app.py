from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)

UPLOAD_FOLDER = '~/pneumo_page/'
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
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save(file.filename)
            return '업로드 성공'
    return render_template('submit.html')


if __name__ == '__main__':
    app.run(debug=True)

