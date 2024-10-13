import os
import pathlib
import requests
from flask import Flask, redirect, request, url_for, jsonify, render_template, abort, session, send_file, flash
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import sys

import multiprocessing
import pandas as pd
import numpy as np
import sqlite3
import jsonpickle
import logging
import db
import run_pipeline as rp

logging.basicConfig(filename="logs/pneuspage.log",level=logging.DEBUG)

app = Flask(__name__)
app.debug = True

app.secret_key = "minory"  #it is necessary to set a password when dealing with OAuth 2.0
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  #this is to set our environment to https because OAuth 2.0 only supports https environments

flow = Flow.from_client_secrets_file(  
    client_secrets_file="client_secret.json",
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],  
    redirect_uri="https://pneuspage.minholee.net/callback"
)

@app.route("/login")  #the page where the user can login
def login():
    if protected():
        is_logined=True
    else:
        is_logined=False 
    return render_template('login.html',login=is_logined)

@app.route("/login/google")  #the page where the user can login
def login_with_google():
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
    if not db.is_joined(id_info["user_key"]):
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
        os.chdir("/home/iu98/pneumo_page")
        user_info={
            "user_key":session["user_key"],
            "username":session["name"]
            }
        print(request.form)
        jobname=request.form.get('jobname')
        
        job_key=db.read_job_num(user_info['user_key'])
        print("job key :",job_key)

        #print("./user/"+str(user_info['user_key'])+"/"+str(job_key))
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
            print("job key :",job_info["job_key"])

            #process = multiprocessing.Process(target=run_with_web, args=(user_info['user_key'], job_info))

            run_slurm(user_info["user_key"],job_info)
            #process.start()
            data = {'result': 'success'} 
            return redirect(f"/result/{str(user_info['user_key'])}")
        else:
            flash("your file is invalid!")    
            return redirect(f"/submit")
    return redirect(f"/submit")

@app.route('/uploadMulti', methods=['POST'])
def upload_multi():
    if request.method == 'POST':
        os.chdir("/home/iu98/pneumo_page")
        user_info={
            "user_key":session["user_key"],
            "username":session["name"]
            }
        
        if not os.path.exists("./user/"+str(user_info['user_key'])+"/multi"):
            os.system("mkdir ./user/"+str(user_info['user_key'])+"/multi")
            print("make ./user/"+str(user_info['user_key'])+"/multi")

        tsv =  request.files["file"]
        tsv.save(os.path.join(("./user/"+str(user_info['user_key'])),"multi",secure_filename(tsv.filename)))
        
        file_list=pd.read_table(os.path.join(("./user/"+str(user_info['user_key'])),"multi",secure_filename(tsv.filename)),sep="\t",names=["jobs","read1","read2"])
        print(file_list)
        raws =  request.files.getlist("file[]")
        raw_list=[]

        if raws:
            #파일이 모두 유효한 것들인지 확인
            for i in range(len(raws)):
                f=raws[i]
                print(list(file_list["read1"]))
                if f.filename in list(file_list["read1"]):
                    raw_list.append(f.filename)
                elif f.filename in list(file_list["read2"]):
                    raw_list.append(f.filename)
                else:
                    flash("Your file is invalid!") 
                    return redirect(f"/submit")
        else:
            flash("Your file is invalid!")    
            return redirect(f"/submit")

        job_key=db.read_job_num(user_info['user_key'])
        print("job key :",job_key)
        
        for i in range(len(file_list["jobs"])):
            print("job key :",job_key)
            job_info={'user_key':user_info['user_key'],
                    "jobname":file_list.iloc[i,0],
                    "job_key":job_key,
                    "file1":file_list.iloc[i,1],
                    "file2":file_list.iloc[i,2]
                }
            if not os.path.exists("./user/"+str(user_info['user_key'])+"/"+str(job_key)):
                os.system("mkdir ./user/"+str(user_info['user_key'])+"/"+str(job_key))
                print("make ./user/"+str(user_info['user_key'])+"/"+str(job_key))
            else :
                data = {'result': 'err'}
                return jsonpickle.encode(data)
            
            #if raws:
            idx=raw_list.index(job_info["file1"])
            f=raws[idx]
            f.save(os.path.join(("./user/"+str(user_info['user_key'])),str(job_key), secure_filename(f.filename)))

            idx=raw_list.index(job_info["file2"])
            f=raws[idx]
            f.save(os.path.join(("./user/"+str(user_info['user_key'])),str(job_key), secure_filename(f.filename)))
            
            for j in range(2):
                if job_info[f'file{str(j+1)}']=="NULL":
                    job_info[f'file{str(j+1)}']=secure_filename(f.filename)

            db.insert_job(user_info,job_info)
            run_slurm(user_info["user_key"],job_info)
            job_key+=1
                #data = {'result': 'success'} 
            #else:
            #    data = {'result': 'err'}
            #    return jsonpickle.encode(data)
            
        return redirect(f"/result/{str(user_info['user_key'])}")
    else:
        flash("your file is invalid!")    
        return redirect(f"/submit")



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
        if(str(user_key)!=session['user_key'] and session['user_key']!="105794308045478426283"):
            flash("You do not have permission!")
            return redirect(f"/result/{session['user_key']}")
        db_info=db.read_user_job(user_key)
        db_df=pd.DataFrame.from_records(data = db_info,columns=["user_id","user_name","job_id","job_name","input_file","states","date"])
        db_df["species"]=""
        job_id=db_df["job_id"]
        for i in job_id:
            db_df.loc[db_df["job_id"]==i,"species"]=rp.get_species(user_key,str(i))
        return render_template('result.html',rows=db_df, login=True,user_id=user_key)
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
    species=rp.get_species(user_key,job_key)
   
    if species!="Streptococcus pneumoniae":
        kraken, quast=rp.get_info(user_key,job_key)
        return render_template('detail.html', login=is_logined, kraken=kraken, species=species, key=job_key, user_id=user_key, files=files, rows=db_info, quast=quast)
    
    species, quast, sero_bool, sero_txt, seroba, vir, mlst_info, mlst_val, mge, cgmlst, kraken, plasmid, amr, prokka, poppunk, pbp_category, pbp_agent=rp.get_info(user_key,job_key)
    print(species, quast)
    if "stop" in mge.columns :
        mge.rename(columns={"stop":"end"},inplace=True)
    
    mge=mge.drop(columns=["contig","start","end"],axis=1)
    #pl_key1=[]
    #pl_key2=[]
    #pl_pd=[]
    #for key1 in plasmid.keys():
    #    for key2 in plasmid[key1].keys():
    #        if plasmid[key1][key2] != "No hit found":
    #            pl_key1.append(key1)
    #            pl_key2.append(key2)
    #            pl_pd.append(pd.DataFrame(plasmid[key1][key2]))
    #if request.method == 'GET':
    #    rp.get_info(username,key,jobname)
    return render_template('detail.html', login=is_logined, species=species,
                           key=job_key, user_id=user_key, files=files, rows=db_info, sero_txt=sero_txt, seroba=seroba, vir=vir, mlst_info=mlst_info, mlst_val=mlst_val, 
                           mge=mge, cgmlst=cgmlst, kraken=kraken,
                           plasmid=plasmid, amr=amr, quast=quast, prokka=prokka, poppunk=poppunk, sero_bool=sero_bool, pbp_category=pbp_category, pbp_agent=pbp_agent)

@app.route('/result/<user_key>/<job_key>/fastqc/<file_name>/download')
def fastqc_download(user_key,job_key,file_name):
    os.chdir("/home/iu98/pneumo_page")
    file_name=file_name.split(".")[0]+"_fastqc.html"
    path=os.path.join("./user",user_key,str(job_key),"fastqc",file_name)
    return send_file(path, as_attachment=True)

@app.route('/result/<user_key>/<job_key>/assembled_fasta/download')
def assembled_fasta_download(user_key,job_key):
    os.chdir("/home/iu98/pneumo_page")
    path=os.path.join("./user",user_key,str(job_key),"spades","scaffolds.fasta")
    return send_file(path, as_attachment=True)

@app.route('/result/<user_key>/<job_key>/gene_anot/download')
def gene_annot_download(user_key,job_key):
    os.chdir("/home/iu98/pneumo_page")
    path=os.path.join("./user",user_key,str(job_key),"prokka","prokka.tsv")
    return send_file(path, as_attachment=True)

@app.route('/submit/tsv/download')
def ex_tsv_download():
    path=os.path.join(".","sample","file_list.tsv")
    return send_file(path, as_attachment=True)

@app.route('/submit/forward/download')
def ex_forward_download():
    path=os.path.join(".","sample","ERR11640752_1.fastq.gz")
    return send_file(path, as_attachment=True)

@app.route('/submit/reverse/download')
def ex_reverse_download():
    path=os.path.join(".","sample","ERR11640752_2.fastq.gz")
    return send_file(path, as_attachment=True)
    

@app.route('/mypage')
def mypage():
    os.chdir("/home/iu98/pneumo_page")
    date=db.read_user_db(session['user_key'])
    return render_template('mypage.html',username=session["name"],email=session["email"],join_date=date["date"])


def run_slurm(user_key,job_info):
    with open("./user/"+str(user_key)+"/"+str(job_info["job_key"])+"/sbatch.sh","w") as f:
        f.write("#!/bin/sh\n\n#SBATCH -J pne_"+str(job_info["job_key"])+"\n#SBATCH --cpus-per-task=4\n#SBATCH --mem 70G\n#SBATCH -p lys\n#SBATCH -o "+str(job_info["job_key"])+".out\n#SBATCH -e "+str(job_info["job_key"])+".err\n\n")
        f.write(f"python /home/iu98/pneumo_page/run_pipeline.py {str(user_key)} {str(job_info['job_key'])} {job_info['file1']} {job_info['file2']}")
    os.chdir("./user/"+str(user_key)+"/"+str(job_info["job_key"]))
    os.system(f"sbatch sbatch.sh")
    os.chdir("/home/iu98/pneumo_page")

@app.route('/result/<user_key>/<job_key>/delete')
def delete_job(user_key,job_key):
    os.chdir("/home/iu98/pneumo_page")
    os.system("rm -r ./user/"+str(user_key)+"/"+str(job_key))
    db.delete_user_job(user_key,job_key)
    return redirect(f"/result/{session['user_key']}")

if __name__ == '__main__':
    sys.stdout = open('log.txt','a')
    app.run(debug=True)
    
