import os
import pathlib
import requests
from flask import Flask, redirect, request, url_for, jsonify, render_template, abort, session, send_file
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
import jsonpickle


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

@app.route('/doc')
def about():
    if protected()!=False:
        print("login")
        return render_template('doc.html',login=True,user_key=session["user_key"])
    else:
        print("logout")
        return render_template('doc.html',login=False)

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
        print(job_key)
        print("./user/"+str(user_info['user_key'])+"/"+str(job_key))
        if not os.path.exists("./user/"+str(user_info['user_key'])+"/"+str(job_key)):
            os.system("mkdir ./user/"+str(user_info['user_key'])+"/"+str(job_key))
            print("make ./user/"+str(user_info['user_key'])+"/"+str(job_key))
        else :


            data = {'result': 'err'}
            return jsonpickle.encode(data)
        
        print("read files...")
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
                
                if job_info[f'file{str(i+1)}']=="NULL":
                    job_info[f'file{str(i+1)}']=secure_filename(f.filename)

            db.insert_job(user_info,job_info)
            db_info=db.read_db(user_info['user_key'])
            job_key=len(db_info)

            process = multiprocessing.Process(target=run_with_web, args=(user_info['user_key'], job_info))
            process.start()

            data = {'result': 'success'} 
            return redirect(f"/result/{str(user_info['user_key'])}")
            
        data = {'result': 'err'}
        return jsonpickle.encode(data)
    data = {'result': 'err'}
    return jsonpickle.encode(data)

@app.route('/result/')
def result_first():
    if protected()!=False:
        return redirect(f"/result/{session['user_key']}")
    else:
        return redirect("/") 

@app.route('/result/<user_key>')
def result(user_key):
    os.chdir("/home/iu98/pneumo_page")
    if protected()!=False:
        db_info=db.read_db(user_key)
    #print(db_info)
        return render_template('result.html',rows=db_info, login=True,user_id=user_key)
    else:
        return redirect("/") 
    

@app.route('/result/<user_key>/<job_key>')
def detail(user_key,job_key):
    if protected()!=False:
        is_logined=True
    print(is_logined)
    os.chdir("/home/iu98/pneumo_page")
    db_info,cols=db.read_db_row(user_key,job_key)
    data_df = pd.DataFrame.from_records(data=db_info, columns=cols)
    files=data_df["input"][0].split("|")
    sero_txt, seroba, vir, mlst, mge, cgmlst, kraken, plasmid, amr, quast, prokka, poppunk=rp.get_info(user_key,job_key)
    mge=mge.drop(["contig","start","end"],axis=1)
    pl_key1=[]
    pl_key2=[]
    pl_pd=[]
    for key1 in plasmid.keys():
        for key2 in plasmid[key1].keys():
            if plasmid[key1][key2] != "No hit found":
                pl_key1.append(key1)
                pl_key2.append(key2)
                pl_pd.append(pd.DataFrame(plasmid[key1][key2]))
    #if request.method == 'GET':
    #    rp.get_info(username,key,jobname)
    return render_template('detail.html', login=is_logined,
                           key=job_key, user_id=user_key, files=files, rows=db_info, sero_txt=sero_txt, seroba=seroba, vir=vir, mlst=mlst, mge=mge, cgmlst=cgmlst, kraken=kraken,
                           pl_key1=pl_key1, pl_key2=pl_key2, pl_pd=pl_pd, amr=amr, quast=quast, prokka=prokka, poppunk=poppunk)

@app.route('/result/<user_key>/<job_key>/fastqc/<file_name>/download')
def fastqc_download(user_key,job_key,file_name):
    os.chdir("/home/iu98/pneumo_page")
    file_name=file_name.split(".")[0]+"_fastqc.html"
    path=os.path.join("./user",user_key,str(job_key),"fastqc",file_name)
    return send_file(path, as_attachment=True)
    

@app.route('/mypage')
def mypage():
    os.chdir("/home/iu98/pneumo_page")
    date=db.read_user_db(session['user_key'])
    return render_template('mypage.html',username=session["name"],email=session["email"],join_date=date["date"])


def run_with_web(user_key,job_info):
    job_key=job_info["job_key"]
    try:
        path_name=os.path.join("./user/",str(user_key),str(job_key))
        file1=job_info["file1"]
        file2=job_info["file2"]

        db.update_db(user_key,job_key,"running")
        rp.run_pipeline(path_name,file1,file2)
    except:
        os.chdir("/home/iu98/pneumo_page")
        db.update_db(user_key,job_key,"fail")
    else:
        os.chdir("/home/iu98/pneumo_page")
        db.update_db(user_key,job_key,"complete")

if __name__ == '__main__':
    app.run(debug=True)
    
