#!/usr/bin/env python3.8

import os
import sys
from pathlib import Path
import pandas as pd
import db
import subprocess
import zipfile
import json
import ast

#import app

def run_fastqc(file1,file2):
    if not(os.path.exists("./fastqc")):
        os.mkdir("./fastqc")
    
    command = ["fastqc","-o",f"./fastqc","-f","fastq",f"./{file1}",f"./{file2}"]
    subprocess.run(command, check=True)  

def read_qc(file1,file2):
    prefix1=file1.split(".")[0]
    prefix2=file2.split(".")[0]

    qcfile1=f"{prefix1}_fastqc.zip"
    qcfile2=f"{prefix2}_fastqc.zip"
    
    command = ["unzip",f"./fastqc/{qcfile1}","-d",f"./fastqc/"]
    subprocess.run(command, check=True)
    with open(os.path.join("fastqc",f"{prefix1}_fastqc","fastqc_data.txt"),"r") as f:
        data=[]
        flag=False
        for line in f :
            if ">>Adapter Content" in line:
                flag=True
            if flag:
                data.append(line)
    
    for d in data:
        if d.startswith("#"):
            header=d.lstrip("#").split("\t")
            continue
        cont=d.split("\t")    

    command = ["unzip",f"./fastqc/{qcfile2}","-d",f"./fastqc/"]
    subprocess.run(command, check=True) 
    return False

def run_trim(file1,file2):
    env = os.environ.copy()
    trimmomatic=env["trimmomatic"]
    file1_name=file1.split(".")[0]
    file2_name=file2.split(".")[0]
    command = ["java","-jar",trimmomatic,"PE","-threads","8",f"./{file1}",f"./{file2}",
                f"./{file1_name}_trim.fastq.gz",f"./trim_R1_unpaired.fastq.gz",f"./{file2_name}_trim.fastq.gz",f"./trim_R2_unpaired.fastq.gz",
                "ILLUMINACLIP:/home/iu98/toolkit/Trimmomatic-0.39/adapters/TruSeq3-PE.fa:2:30:10:2:True","LEADING:3","TRAILING:3","MINLEN:36"]
    subprocess.run(command, check=True, env=env)  


def run_kraken2(file1,file2):
    if not(os.path.exists("./kraken")):
        os.mkdir("./kraken")
    command = f"kraken2 --paired --threads 8 --report ./kraken/result.kreport ./{file1} ./{file2} > ./kraken/kraken.txt"
    subprocess.run(command, check=True, shell=True)
    command = ["bracken","-d","/home/iu98/toolkit/kraken_db","-i",f"./kraken/result.kreport","-o",f"./kraken/result.bracken","-r","100"]
    subprocess.run(command, check=True)  

        
def run_spades(file1,file2):
    command = ["spades.py","-t","8","-1",f"./{file1}","-2",f"./{file2}","-o","./spades"]
    subprocess.run(command, check=True)  

def run_quast():
    command = ["quast.py",f"./spades/contigs.fasta","-r","/home/iu98/pneumo_page/reference/GCF_002076835.1_ASM207683v1_genomic.fna",
               "-g","/home/iu98/pneumo_page/reference/s.pneumoniae.gtf","-t","4",
               "-o",f"./quast"]
    subprocess.run(command, check=True)  

def run_prokka():
    command = ["prokka","-o","prokka","--prefix","prokka","./spades/contigs.fasta"]
    subprocess.run(command, check=True)  

def run_MGE():
    if(os.path.exists("/tmp/mge_finder")):
        os.system("rm -r /tmp/mge_finder")
    if not(os.path.exists("./mge")):
        os.mkdir("./mge")
    command = ["mefinder","find","-c","./spades/contigs.fasta","./mge/mge"]
    subprocess.run(command, check=True)  

def run_cgMLST():
    if not(os.path.exists("./cgMLST")):
        os.mkdir("./cgMLST")
    command = ["cgMLST.py","-i","./spades/contigs.fasta","-s","spneumoniae"
                ,"-db","/home/iu98/pneumo_pipline/cgmlstfinder/cgmlstfinder_db","-o","./cgMLST"]
    subprocess.run(command, check=True)  

def run_poppunk():
    with open("path.txt","w") as f:
        f.write("S1\t./spades/contigs.fasta\n")
        f.close()
    command = ["poppunk_assign","--db","/home/iu98/toolkit/GPS_v6/GPS_v6","--distance","/home/iu98/toolkit/GPS_v6/GPS_v6.dists","--query","path.txt",
               "--output","poppunk","--external-clustering","/home/iu98/toolkit/GPS_v6/GPS_v6_external_clusters.csv","--threads","8"]
    subprocess.run(command, check=True)  

def run_virulencefinder():
    if not(os.path.exists("./virulence")):
        os.mkdir("./virulence")
    command = ["virulencefinder.py","-i","./spades/contigs.fasta","-d","s.pneumoniae"
                ,"-p","/home/iu98/pneumo_pipline/virulencefinder/virulencefinder_db","-x","-o","./virulence"]
    subprocess.run(command, check=True)  


def run_abricate():
    if not(os.path.exists("./AMR")):
        os.mkdir("./AMR")
    command = "abricate ./spades/contigs.fasta > ./AMR/abricate_result.tsv"
    subprocess.run(command, check=True, shell=True)  


def run_MLST(file1,file2):
    if not(os.path.exists("./mlst")):
        os.mkdir("./mlst")
    command = "mlst -csv -nopath --scheme spneumoniae ./spades/scaffolds.fasta > ./mlst/mlst.csv"
    subprocess.run(command, check=True, shell=True)

def run_plasmidfinder(file1,file2):
    if not(os.path.exists("./plasmid")):
        os.mkdir("./plasmid")
    command = f"plasmidfinder.py -i ./{file1} ./{file2} -p /home/iu98/toolkit/plasmidfinder_db -o ./plasmid > ./plasmid/result.json"
    subprocess.run(command, check=True, shell=True) 

def run_seroba(file1,file2):
    os.system(f"mv ./{file1} ./read_1.fq.gz")
    os.system(f"mv ./{file2} ./read_2.fq.gz")
    command = ["seroba","runSerotyping","/home/iu98/pneumo_pipline/seroba/database",
                "./read_1.fq.gz","./read_2.fq.gz","seroba"]
    subprocess.run(command, check=True) 
    os.system(f"mv ./read_1.fq.gz ./{file1}")
    os.system(f"mv ./read_2.fq.gz ./{file2}")
    

def run_blast():
    if not(os.path.exists("./blast")):
        os.mkdir("./blast")
    command = ["blastn","-query","./spades/contigs.fasta","-db","nt"
                ,"-outfmt",'6 qseqid sseqid scomnames length qstart qend sstart send evalue pident',"-out","./blast/blast_result.txt"]
    subprocess.run(command, check=True)  
       

def get_info(user_key,job_key):
    path_name="./user/"+user_key+"/"+job_key
    print(path_name)
    path_name=str(path_name)
    os.chdir(path_name)
    sero_txt=[]
    if os.path.exists("./seroba/detailed_serogroup_info.txt"):
        with open("./seroba/detailed_serogroup_info.txt","r") as f:
            for i in range(0,3):
                line=f.readline().rstrip("\n")
                line=line.replace("\t"," ")
                sero_txt.append(line)
        seroba=pd.read_csv(("./seroba/detailed_serogroup_info.txt"),sep="\t",skiprows=[0,1,2])
        sero_bool=True
    else :
        sero_txt.append(open("./seroba/pred.tsv").read().split("\t")[1])
        sero_bool=False
        seroba=False
    vir=pd.read_csv(("./virulence/results_tab.tsv"),sep="\t")
    mlst=pd.read_csv("./mlst/mlst.csv",header=None)
    mlst.loc[1]=None
    mlst.iloc[1,2]=mlst.iloc[0,2]
    for i in range(3,len(mlst.columns)):
        print(mlst.iloc[0,i])
        mlst.iloc[1,i]=str(mlst.iloc[0,i]).split("(")[1].rstrip(")")
        mlst.iloc[0,i]=str(mlst.iloc[0,i]).split("(")[0]
    mlst=mlst.iloc[:,2:len(mlst.columns)]
    mge=pd.read_csv(("./mge/mge.csv"),skiprows=[0,1,2,3,4])
    cgmlst=pd.read_csv(("./cgMLST/spneumoniae_summary.txt"),sep="\t")
    kraken=pd.read_csv(("./kraken/result.bracken"),sep="\t",keep_default_na=False)[0:5]
    amr=pd.read_csv(("./AMR/abricate_result.tsv"),sep="\t",keep_default_na=False)
    quast=os.path.abspath("./quast/report.html")
    prokka=pd.read_csv(("./prokka/prokka.tsv"),sep="\t",keep_default_na=False)[0:20]
    poppunk=pd.read_csv(("./poppunk/poppunk_clusters.csv"))
    with open("./plasmid/result.json") as j:
        data=j.read()
        plasmid=ast.literal_eval(data)
        plasmid=plasmid["plasmidfinder"]["results"]
    #blast=pd.read_excel(("./blast/blast_result_summary.xlsx"))
    #blast.columns = ['contig', 'top1', 'top2', 'top3', 'top4', 'top5']
    return sero_bool, sero_txt, seroba, vir, mlst, mge, cgmlst, kraken, plasmid, amr, quast, prokka, poppunk

    
def run_pipeline(path_name,file1,file2):
    os.chdir(path_name)
    run_fastqc(file1,file2)
    #flag=read_qc(file1,file2)
    #if flag:
    #    run_trim(path_name,file1,file2)
    #    file1=file1.split(".")+"_trim.fastq.gz"
    #    file2=file2.split(".")+"_trim.fastq.gz"
    run_kraken2(file1,file2)
    run_spades(file1,file2)
    run_quast()
    run_prokka()
    run_poppunk()
    run_MGE()
    run_cgMLST()
    run_virulencefinder()
    run_abricate()
    run_MLST(file1,file2)
    run_plasmidfinder(file1,file2)
    run_seroba(file1,file2)
    return True

if __name__ == '__main__':
    path=sys.argv[1]
    file1=sys.argv[2]
    file2=sys.argv[3]
    run_pipeline(path,file1,file2)