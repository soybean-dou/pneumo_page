import os
import pathlib
import requests
from flask import Flask, redirect, request, url_for, jsonify, render_template, abort, session
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

import multiprocessing
import pandas as pd
import numpy as np
import sqlite3

import db
import run_pipeline as rp

app = Flask(__name__)
app.debug = True

app.secret_key = "minory"  #it is necessary to set a password when dealing with OAuth 2.0
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  #this is to set our environment to https because OAuth 2.0 only supports https environments

flow = Flow.from_client_secrets_file(  
    client_secrets_file="client_secret.json",
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],  
    redirect_uri="https://lysine.minholee.net:25000/callback"
)

@app.route("/login")  #the page where the user can login
def login():
    authorization_url, state = flow.authorization_url()  #asking the flow class for the authorization (login) url
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")  #this is the page that will handle the callback process meaning process after the authorization
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  #state does not match!

    credentials = flow.credentials
    CLIENT_ID = flow.client_config["client_id"]
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=CLIENT_ID
    )

    id_info["user_key"]=id_info["sub"]
    session["user_info"]= id_info
    session["user_key"]= id_info["sub"]
    session["email"]=id_info.get("email")
    session["name"] = id_info.get("name")
    print(id_info)
    db.insert_user(id_info)
    return redirect("/")  #the final page where the authorized users will end up


@app.route("/logout")  #the logout page and function
def logout():
    print("logout")
    session.clear()
    return redirect("/")

def protected():
    user_info = session.get('user_info')
    if user_info:
        return user_info["user_key"]
    return False

@app.route('/')
def index():
    if protected()!=False:
        print("login")
        return render_template('index.html',login=True,user_key=session["user_key"])
    else:
        print("logout")
        return render_template('index.html',login=False)

@app.route('/about')
def about():
    if protected()!=False:
        print("login")
        return render_template('about.html',login=True,username=session["user_key"])
    else:
        print("logout")
        return render_template('about.html',login=False)

@app.route('/submit')
def submit():
    if protected()!=False:
        print("login")
        return render_template('submit.html',login=True,user_key=session["user_key"])
    else:
        print("logout")
        return render_template('submit.html',login=False)

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        user_info={
            "user_key":session["user_key"],
            "username":session["name"]
            }
        print(request.form)
        jobname=request.form.get('jobname')
        
        db_info=db.read_db(user_info['user_key'])
        job_key=len(db_info)+1

        if not(os.path.exists("./user/"+str(user_info['user_key'])+"/"+str(job_key))):
            os.system("mkdir ./user/"+str(user_info['user_key'])+"/"+str(job_key))
            print("make ./user/"+str(user_info['user_key'])+"/"+str(job_key))
        else :
            return False
        
        files =  request.files.getlist("file[]")
        job_info={'user_key':user_info['user_key'],
                    "jobname":jobname,
                    "job_key":job_key,
                    "file1":"NULL",
                    "file2":"NULL"
                }
                
        if files:
            print(files)
            for i in range(len(files)):
                f=files[i]
                f.save(os.path.join(("./user/"+str(user_info['user_key'])),str(job_key), secure_filename(f.filename)))
                
                if job_info[f'file{i}']=="NULL":
                    job_info[f'file{i}']=secure_filename(f.filename)

            db.insert_job(user_info,job_info)
            db_info=db.read_db(user_info['user_key'])
            job_key=len(db_info)

            process = multiprocessing.Process(target=rp.main, args=(user_info['user_key'], job_info))
            process.start()
            
            data = {'result': 'success'} 
            return redirect(f"/result/{str(user_info['user_key'])}")
            
        data = {'result': 'err'}
        return jsonify(data)
    data = {'result': 'err'}
    return jsonify(data)

@app.route('/result/')
def result_first():
    if protected()!=False:
        return redirect(f"/result/{session['user_key']}")
    else:
        return redirect("/") 

@app.route('/result/<user_key>')
def result(user_key):
    db_info=db.read_db(user_key)
    #print(db_info)
    return render_template('result.html',rows=db_info)

@app.route('/result/<user_key>/<job_key>')
def detail(user_key,job_key):
    db_info,cols=db.read_db_row(user_key,job_key)
    data_df = pd.DataFrame.from_records(data=db_info, columns=cols)
    print(data_df)
    jobname=str(data_df.at[0,"jobname"])
    seroba, vir, mlst, mge, cgmlst, kmer, blast=rp.get_info(user_key,job_key,jobname)
    mge=mge.drop(["contig","start","end"],axis=1)
    #if request.method == 'GET':
    #    rp.get_info(username,key,jobname)
    return render_template('detail.html',
                           key=job_key, rows=db_info, seroba=seroba, vir=vir, mlst=mlst, mge=mge, cgmlst=cgmlst, kmer=kmer, blast=blast)

@app.route('/mypage')
def mypage():
    return render_template('mypage.html',username=session["name"],email=session["email"])

if __name__ == '__main__':
    app.run(debug=True)
    
