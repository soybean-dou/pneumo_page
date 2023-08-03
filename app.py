from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import db
import run_pipeline as rp
import asyncio

app = Flask(__name__)


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
        username=request.form['username']
        
        if not(os.path.exists("./user/"+username)):
            os.system("mkdir ./user/"+username)
            print("make ./user/"+username)
        
        if not(os.path.exists("./user/"+username+"/"+username+".db")):
            db.make_db(username)
            print("make "+username+".db")

        files = request.files.getlist("file")
        job_info={'username':username,
                    "jobname":request.form['jobname'],
                    "filename":"NULL",
                    "wgstype":request.form['wgstype']}
                
        if files:
            print(files)
            for f in files:
                f.save(os.path.join(("./user/"+username), secure_filename(f.filename)))
                
                if job_info['filename']=="NULL":
                    job_info['filename']=secure_filename(f.filename)

            db.insert_db(username,job_info)
            db_info=db.read_db(username)
            key=len(db_info)
            asyncio.run(rp.run_mapping(username,key))    
            data = {'result': 'success', 'state': 'running'}
            return jsonify(data)
        data = {'result': 'err'}
        return jsonify(data)
    data = {'result': 'err'}
    return jsonify(data)

@app.route('/result/<username>', methods=['GET','POST'])
def result(username):
    db_info=db.read_db(username)
    print(db_info)
    return render_template('result.html',rows=db_info)

if __name__ == '__main__':
    app.run(debug=True)

