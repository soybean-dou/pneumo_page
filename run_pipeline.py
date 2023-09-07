#!/usr/bin/env python3.8

import os
import sys
from pathlib import Path
import pandas as pd
import db
import subprocess
import app

# def run_mapping(user_key,job_key,jobname):
#     path_name=os.path.join("./user/",user_key,job_key)
#     db.update_db(user_key,job_key,"running")
#     file_all=os.listdir(path_name)
#     file_list=[file for file in file_all if file.endswith(".fastq.gz")]
#     file_list.sort()

#     qc=30
#     trim=50
#     for i in range(0,len(file_list),2):
#         try:
#             db.update_db(user_key,job_key,"running")
#             command = ['non_adapt_pre-processing.py', path_name+"/"+file_list[i] , path_name+"/"+file_list[i+1], str(qc), str(trim),
#                        "./reference/GRCh38_latest_genomic.fna", "./reference/GCF_002076835.1_ASM207683v1_genomic.fna","./user/"+user_key, jobname]
#             subprocess.run(command, check=True)

#         except:
#             db.update_db(user_key,user_key,"fail")
#             print("mapping error!")                
    

def run_fastqc(user_key,job_info):
    job_key=job_info["job_key"]
    path_name=os.path.join("./user/",str(user_key),str(job_key))
    os.mkdir(path_name+"/fastqc")
    try:
        db.update_db(user_key,job_key,"running")
        command = ["fastqc","-o",f"{path_name}/fastqc","-f","fastq",f"{path_name}/{job_info['file1']}",f"{path_name}/{job_info['file2']}"]
        subprocess.run(command, check=True)  
    except:
        db.update_db(user_key,job_key,"fail")
        print("fastqc error!")

def run_trim(user_key,job_info):
    job_key=job_info["job_key"]
    path_name=os.path.join("./user/",str(user_key),str(job_key))
    os.mkdir(path_name+"/fastqc")
    try:
        db.update_db(user_key,job_key,"running")
        command = ["java","-jar","$trimmomatic","PE",f"{path_name}/{job_info['file1']}",f"{path_name}/{job_info['file2']}",
                   "trim_R1.fastq.gz","trim_R1_unpaired.fastq.gz","trim_R2.fastq.gz","trim_R2_unpaired.fastq.gz"]
        subprocess.run(command, check=True)  
    except:
        db.update_db(user_key,job_key,"fail")
        print("fastqc error!")

def run_spades(user_key,job_key,jobname):
    path_name=os.path.join("./user/",user_key,jobname)
    db.update_db(user_key,job_key,"running")

    try:
        command = ["spades.py","-1",path_name+"/workpath/unmapped_R1.fastq","-2",path_name+"/workpath/unmapped_R2.fastq","-o",path_name+"/spades"]
        subprocess.run(command, check=True)  
    except:
        db.update_db(user_key,job_key,"fail")
        print("spades error!")

def run_spades(user_key,job_key,jobname):
    path_name=os.path.join("./user/",user_key,jobname)
    db.update_db(user_key,job_key,"running")

    try:
        command = ["spades.py","-1",path_name+"/workpath/unmapped_R1.fastq","-2",path_name+"/workpath/unmapped_R2.fastq","-o",path_name+"/spades"]
        subprocess.run(command, check=True)  
    except:
        db.update_db(user_key,job_key,"fail")
        print("spades error!")


def run_MGE(user_key,job_key,jobname):
    path_name="./user/"+user_key+"/"+jobname
    db.update_db(user_key,job_key,"running")

    if not(os.path.exists(path_name+"/mge")):
        os.mkdir(path_name+"/mge")
    try:
        command = ["mobileElementFinder.py","find","-c",path_name+"/spades/scaffolds.fasta",path_name+"/mge/"]
        subprocess.run(command, check=True)  
        os.system("mv mge*.* mge")
    except:
        db.update_db(user_key,job_key,"fail")
        print("MGE error!")

def run_cgMLST(user_key,job_key,jobname):
    path_name="./user/"+user_key+"/"+jobname
    db.update_db(user_key,job_key,"running")

    if not(os.path.exists(path_name+"/cgMLST")):
        os.mkdir(path_name+"/cgMLST")
    try:
        command = ["cgMLST.py","-i",path_name+"/spades/scaffolds.fasta","-s","spneumoniae"
                   ,"-db","/home/iu98/pneumo_pipline/cgmlstfinder/cgmlstfind_db","-o",path_name+"/cgMLST"]
        subprocess.run(command, check=True)  
    except:
        db.update_db(user_key,job_key,"fail")
        print("cgMLST error!")

def run_virulencefinder(user_key,job_key,jobname):
    path_name="./user/"+user_key+"/"+jobname
    db.update_db(user_key,job_key,"running")

    if not(os.path.exists(path_name+"/virulence")):
        os.mkdir(path_name+"/virulence")
    try:
        command = ["virulencefinder.py","-i",path_name+"/spades/scaffolds.fasta","-d","s.pneumoniae"
                   ,"-p","/home/iu98/pneumo_pipline/virulencefinder/virulencefinder_db","-x","-o",path_name+"/virulence"]
        subprocess.run(command, check=True)  
    except:
        db.update_db(user_key,job_key,"fail")
        print("virulence error!")

def run_resfinder(user_key,job_key,jobname):
    path_name="./user/"+user_key+"/"+jobname
    db.update_db(user_key,job_key,"running")

    if not(os.path.exists(path_name+"/resfinder")):
        os.mkdir(path_name+"/resfinder")
    try:
        command = ["python","-m","resfinder","-ifq",path_name]
        subprocess.run(command, check=True)  
    except:
        db.update_db(user_key,job_key,"fail")
        print("resfinder error!")

def run_MLST(user_key,job_key,jobname):
    path_name="./user/"+user_key+"/"+jobname
    db.update_db(user_key,job_key,"running")

    if not(os.path.exists(path_name+"/mlst")):
        os.mkdir(path_name+"/mlst")
    try:
        command = ["mlst.py","-i",path_name+"/workpath/unmapped_R1.fastq",path_name+"/workpath/unmapped_R2.fastq",
                   "-s","spneumoniae","-p","/home/iu98/pneumo_pipline/mlst/mlst_db","-x","-o",path_name+"/mlst"]
        subprocess.run(command, check=True)  
    except:
        db.update_db(user_key,job_key,"fail")
        print("MLST error!")

def run_K(user_key,job_key,jobname):
    path_name="./user/"+user_key+"/"+jobname
    db.update_db(user_key,job_key,"running")

    if not(os.path.exists(path_name+"/kmerfinder")):
        os.mkdir(path_name+"/kmerfinder")
    try:
        command = ["kmerfinder.py","-i",path_name+"/workpath/unmapped_R1.fastq",path_name+"/workpath/unmapped_R2.fastq",
                   "-db", "/home/iu98/pneumo_pipline/kmerfinder/kmerfinder_db/bacteria/",
                   "-tax","/home/iu98/pneumo_pipline/kmerfinder/kmerfinder_db/bacteria/bacteria.tax",
                   "-o",path_name+"/kmerfinder"]
        subprocess.run(command, check=True)
          
    except:
        db.update_db(user_key,job_key,"fail")
        print("kmerfinder error!")

def run_seroba(user_key,job_key,jobname):
    path_name="./user/"+user_key+"/"+jobname
    db.update_db(user_key,job_key,"running")

    if not(os.path.exists(path_name+"/seroba")):
        os.mkdir(path_name+"/seroba")
    try:
        command = ["seroba","runSerotyping","/home/iu98/pneumo_pipline/seroba/database",
                   path_name+"/workpath/unmapped_R1.fastq",path_name+"/workpath/unmapped_R2.fastq","seroba"]
        subprocess.run(command, check=True) 
        os.system("mv seroba "+path_name) 
    except:
        db.update_db(user_key,job_key,"fail")
        print("seroba error!")

def run_blast(user_key,job_key,jobname):
    path_name="./user/"+user_key+"/"+jobname
    db.update_db(user_key,job_key,"running")

    if not(os.path.exists(path_name+"/blast")):
        os.mkdir(path_name+"/blast")
    try:
        command = ["blastn","-query",path_name+"/spades/scaffolds.fasta","-db","nt"
                   ,"-outfmt",'6 qseqid sseqid scomnames length qstart qend sstart send evalue pident',"-out",path_name+"/blast/blast_result.txt"]
        subprocess.run(command, check=True)  
    except:
        db.update_db(user_key,job_key,"fail")
        print("blast error!")        

def get_info(user_key,job_key,jobname):
    path_name="./user/"+user_key+"/"+jobname
    path_name=str(path_name)
    seroba=pd.read_csv((path_name+"/seroba/pred.tsv"),sep="\t",header=None)
    seroba=seroba.at[0,1]
    vir=pd.read_csv((path_name+"/virulence/results_tab.tsv"),sep="\t")
    mlst=pd.read_csv((path_name+"/mlst/results_tab.tsv"),sep="\t")
    mge=pd.read_csv((path_name+"/mge/mge.csv"))
    cgmlst=pd.read_csv((path_name+"/cgMLST/results_tab.tsv"),sep="\t")
    kmer=pd.read_csv((path_name+"/kmerfinder/results.txt"),sep="\t")
    blast=pd.read_excel((path_name+"/blast/blast_result_summary.xlsx"))
    blast.columns = ['contig', 'top1', 'top2', 'top3', 'top4', 'top5']
    return seroba, vir, mlst, mge, cgmlst, kmer, blast

    



def main(user_key,job_info):
    run_fastqc(user_key,job_info)
    run_spades(user_key,job_key,jobname)
    run_MGE(user_key,job_key,jobname)
    run_cgMLST(user_key,job_key,jobname)
    run_virulencefinder(user_key,job_key,jobname)
    run_MLST(user_key,job_key,jobname)
    #run_resfinder(user_key,job_key,jobname)
    run_seroba(user_key,job_key,jobname)
    run_blast(user_key,job_key,jobname)
    db.update_db(user_key,job_key,"complete")
    app.result(user_key)