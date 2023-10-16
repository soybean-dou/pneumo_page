#!/usr/bin/env python3.8

import os
import sys
from pathlib import Path
import pandas as pd
import db
import subprocess
#import app

def run_fastqc(path_name,file1,file2):
    command = ["fastqc","-o",f"{path_name}/fastqc","-f","fastq",f"{path_name}/{file1}",f"{path_name}/{file2}"]
    subprocess.run(command, check=True)  

def read_qc(path_name,file1,file2):
    return False

def run_trim(path_name,file1,file2):
    env = os.environ.copy()
    trimmomatic=env["trimmomatic"]
    file1_name=file1.split(".")[0]
    file2_name=file2.split(".")[0]
    command = ["java","-jar",trimmomatic,"PE","-threads","8",f"{path_name}/{file1}",f"{path_name}/{file2}",
                f"{path_name}/{file1_name}_trim.fastq.gz",f"{path_name}/trim_R1_unpaired.fastq.gz",f"{path_name}/{file2_name}_trim.fastq.gz",f"{path_name}/trim_R2_unpaired.fastq.gz",
                "ILLUMINACLIP:/home/iu98/toolkit/Trimmomatic-0.39/adapters/TruSeq3-PE.fa:2:30:10:2:True","LEADING:3","TRAILING:3","MINLEN:36"]
    subprocess.run(command, check=True, env=env)  


def run_kraken2(path_name,file1,file2):
    if not(os.path.exists(path_name+"/kraken")):
        os.mkdir(path_name+"/kraken")
    command = f"kraken2 --paired --threads 8 --report {path_name}/kraken/result.kreport {path_name}/{file1} {path_name}/{file2} > {path_name}/kraken/kraken.txt"
    subprocess.run(command, check=True, shell=True)
    command = ["bracken","-d","$KRAKEN2_DEFAULT_DB","-i",f"{path_name}/kraken/result.kreport","-o",f"{path_name}/kraken/result.bracken","-r","100"]
    subprocess.run(command, check=True)  

        
def run_spades(path_name,file1,file2):
    command = ["spades.py","-1",f"{path_name}/{file1}","-2",f"{path_name}/{file2}","-o",path_name+"/spades"]
    subprocess.run(command, check=True)  

def run_MGE(path_name):
    if not(os.path.exists(path_name+"/mge")):
        os.mkdir(path_name+"/mge")
    command = ["mobileElementFinder.py","find","-c",path_name+"/spades/contigs.fasta",path_name+"/mge/"]
    subprocess.run(command, check=True)  
    os.system(f"mv {path_name}/mge*.* {path_name}/mge")


def run_cgMLST(path_name):
    if not(os.path.exists(path_name+"/cgMLST")):
        os.mkdir(path_name+"/cgMLST")
    command = ["cgMLST.py","-i",path_name+"/spades/contigs.fasta","-s","spneumoniae"
                ,"-db","/home/iu98/pneumo_pipline/cgmlstfinder/cgmlstfinder_db","-o",path_name+"/cgMLST"]
    subprocess.run(command, check=True)  


def run_virulencefinder(path_name):
    if not(os.path.exists(path_name+"/virulence")):
        os.mkdir(path_name+"/virulence")
    command = ["virulencefinder.py","-i",path_name+"/spades/contigs.fasta","-d","s.pneumoniae"
                ,"-p","/home/iu98/pneumo_pipline/virulencefinder/virulencefinder_db","-x","-o",path_name+"/virulence"]
    subprocess.run(command, check=True)  


def run_abricate(path_name):
    if not(os.path.exists(path_name+"/AMR")):
        os.mkdir(path_name+"/AMR")
    command = ["abricate",f"{path_name}/spades/contigs.fasta",">",f"{path_name}/AMR/abricate_result.tsv"]
    subprocess.run(command, check=True)  


def run_MLST(path_name,file1,file2):
    if not(os.path.exists(path_name+"/mlst")):
        os.mkdir(path_name+"/mlst")
    command = ["mlst.py","-i",path_name+"/"+file1,path_name+"/"+file2,
                "-s","spneumoniae","-p","/home/iu98/pneumo_pipline/mlst/mlst_db","-x","-o",path_name+"/mlst"]
    subprocess.run(command, check=True)  



def run_seroba(path_name,file1,file2):
    if not(os.path.exists(path_name+"/seroba")):
        os.mkdir(path_name+"/seroba")

    command = ["seroba","runSerotyping","/home/iu98/pneumo_pipline/seroba/database",
                path_name+"/"+file1,path_name+"/"+file2,"seroba"]
    subprocess.run(command, check=True) 
    os.system("mv seroba "+path_name) 


def run_blast(path_name):
    if not(os.path.exists(path_name+"/blast")):
        os.mkdir(path_name+"/blast")
    command = ["blastn","-query",path_name+"/spades/contigs.fasta","-db","nt"
                ,"-outfmt",'6 qseqid sseqid scomnames length qstart qend sstart send evalue pident',"-out",path_name+"/blast/blast_result.txt"]
    subprocess.run(command, check=True)  
       

def get_info(user_key,job_key):
    path_name="./user/"+user_key+"/"+job_key
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

    



def run_with_web(user_key,job_info):
    flag=False
    job_key=job_info["job_key"]
    try:
        path_name=os.path.join("./user/",str(user_key),str(job_key))
        file1=job_info["file1"]
        file2=job_info["file2"]

        db.update_db(user_key,job_key,"running")
        run_pipeline(path_name,file1,file2)
    except:
        db.update_db(user_key,job_key,"fail")


def run_pipeline(path_name,file1,file2):
    run_fastqc(path_name,file1,file2)
    flag=read_qc(path_name,file1,file2)
    if flag:
        run_trim(path_name,file1,file2)
        file1=file1.split(".")+"_trim.fastq.gz"
        file2=file2.split(".")+"_trim.fastq.gz"
    run_kraken2(path_name,file1,file2)
    run_spades(path_name,file1,file2)
    run_MGE(path_name)
    run_cgMLST(path_name)
    run_virulencefinder(path_name)
    run_abricate(path_name)
    run_MLST(path_name,file1,file2)
    run_seroba(path_name,file1,file2)

if __name__ == '__main__':
    path=sys.argv[1]
    file1=sys.argv[2]
    file2=sys.argv[3]
    run_pipeline(path,file1,file2)