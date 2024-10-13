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
    command = ["quast.py",f"./spades/scaffolds.fasta","-m","100","-r","/home/iu98/pneumo_page/reference/GCF_002076835.1_ASM207683v1_genomic.fna",
               "-g","/home/iu98/pneumo_page/reference/s.pneumoniae.gtf","-t","4",
               "-o",f"./quast"]
    subprocess.run(command, check=True)  

def run_prokka():
    command = ["prokka","-o","prokka","--force","--prefix","prokka","./spades/scaffolds.fasta"]
    subprocess.run(command, check=True)  

def run_MGE():
    if(os.path.exists("/tmp/mge_finder")):
        os.system("rm -r /tmp/mge_finder")
    if not(os.path.exists("./mge")):
        os.mkdir("./mge")
    command = ["mefinder","find","-c","./spades/scaffolds.fasta","--temp-dir","./mge/tmp","./mge/mge" ]
    subprocess.run(command, check=True)  

def run_cgMLST():
    if not(os.path.exists("./cgMLST")):
        os.mkdir("./cgMLST")
    command = ["cgMLST.py","-i","./spades/scaffolds.fasta","-s","spneumoniae"
                ,"-db","/home/iu98/pneumo_pipline/cgmlstfinder/cgmlstfinder_db","-o","./cgMLST"]
    subprocess.run(command, check=True)  

def run_poppunk():
    with open("path.txt","w") as f:
        f.write("S1\t./spades/scaffolds.fasta\n")
        f.close()
    command = ["poppunk_assign","--db","/home/iu98/toolkit/GPS_v6/GPS_v6","--distance","/home/iu98/toolkit/GPS_v6/GPS_v6.dists","--query","path.txt",
               "--output","poppunk","--external-clustering","/home/iu98/toolkit/GPS_v6/GPS_v6_external_clusters.csv","--threads","8"]
    subprocess.run(command, check=True)  

def run_virulencefinder():
    if not(os.path.exists("./virulence")):
        os.mkdir("./virulence")
    command = ["virulencefinder.py","-i","./spades/scaffolds.fasta","-d","s.pneumoniae"
                ,"-p","/home/iu98/pneumo_pipline/virulencefinder/virulencefinder_db","-x","-o","./virulence"]
    subprocess.run(command, check=True)  


def run_abricate():
    if not(os.path.exists("./AMR")):
        os.mkdir("./AMR")
    command = "abricate --db card ./spades/scaffolds.fasta > ./AMR/abricate_result.tsv"
    subprocess.run(command, check=True, shell=True)  


def run_MLST():
    if not(os.path.exists("./mlst")):
        os.mkdir("./mlst")
    command = "mlst -csv -nopath --scheme spneumoniae ./spades/scaffolds.fasta > ./mlst/mlst.csv"
    subprocess.run(command, check=True, shell=True)

def run_plasmidfinder():
    if not(os.path.exists("./plasmid")):
        os.mkdir("./plasmid")
    #command = f"plasmidfinder.py -i ./{file1} ./{file2} -p /home/iu98/toolkit/plasmidfinder_db -o ./plasmid > ./plasmid/result.json"
    command = f"abricate --csv --nopath --quiet --db plasmidfinder spades/scaffolds.fasta > plasmid/plasmid.csv"
    
    subprocess.run(command, check=True, shell=True) 

def run_pbpfinder():
    job_path=os.path.abspath(os.curdir)
    print(job_path)
    os.chdir("/home/iu98/pneumo_pipline/pbp_connectagen")
    command = ["cnpbp.sh","-s",f"{job_path}/spades/scaffolds.fasta","-n","pbp","-o",f"{job_path}/pbptyping"]
    subprocess.run(command, check=True) 
    os.chdir(job_path)
    with open("./pbptyping/pbp_final_result.tsv") as f:
        for line in f:
            if(line.startswith(">PBP_Category")):
                f1=open("./pbptyping/pbp_Category.txt","w")
                f1.write(line.lstrip(">"))
            elif(line.startswith(">Agent")):
                f1.close()
                f2=open(f"./pbptyping/pbp_agent.txt","w")
                f2.write(line.lstrip(">"))
                break
            else:
                f1.write(line)
        for line in f:
            f2.write(line)
        f2.close()

def run_seroba(file1,file2):
    print(os.path.abspath(os.path.curdir))
    #os.system(f"mv ./{file1} ./read_1.fq.gz")
    #os.system(f"mv ./{file2} ./read_2.fq.gz")
    command = ["seroba","runSerotyping", f"./{file1}",f"./{file2}","seroba"]
    subprocess.run(command, check=True) 
    #os.system(f"mv ./read_1.fq.gz ./{file1}")
    #os.system(f"mv ./read_2.fq.gz ./{file2}")
    

def run_blast():
    if not(os.path.exists("./blast")):
        os.mkdir("./blast")
    command = ["blastn","-query","./spades/scaffolds.fasta","-db","nt"
                ,"-outfmt",'6 qseqid sseqid scomnames length qstart qend sstart send evalue pident',"-out","./blast/blast_result.txt"]
    subprocess.run(command, check=True)  

def get_species(user_key,job_key):
    os.chdir("/home/iu98/pneumo_page")
    path_name="./user/"+user_key+"/"+job_key
    #print(path_name)
    path_name=str(path_name)
    os.chdir(path_name)
    try:
        kraken=pd.read_csv(("./kraken/result.bracken"),sep="\t",keep_default_na=False)[0:5]
        species=kraken.iloc[0,0]
        return species
    except:
        return None

def get_info(user_key,job_key):
    os.chdir("/home/iu98/pneumo_page")
    path_name="./user/"+user_key+"/"+job_key
    print(path_name)
    path_name=str(path_name)
    os.chdir(path_name)
    kraken=pd.read_csv(("./kraken/result.bracken"),sep="\t",keep_default_na=False)[0:5].applymap(str)
    species=kraken.iloc[0,0]
    
    quast=pd.read_csv(("./quast/transposed_report.tsv"),sep="\t",keep_default_na=False).applymap(str)
    quast=quast.loc[:,["# contigs","Largest contig","Total length","GC (%)","N50","N90"]]

    if species!="Streptococcus pneumoniae":
        return kraken, quast
    
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
    
    vir=pd.read_csv(("./virulence/results_tab.tsv"),sep="\t",keep_default_na=False).applymap(str)
    
    mlst=pd.read_csv("./mlst/mlst.csv",header=None).applymap(str)
    mlst.loc[1]=None
    mlst.iloc[1,2]=mlst.iloc[0,2]
    for i in range(3,len(mlst.columns)):
        print(mlst.iloc[0,i])
        mlst.iloc[1,i]=str(mlst.iloc[0,i]).split("(")[1].rstrip(")")
        mlst.iloc[0,i]=str(mlst.iloc[0,i]).split("(")[0]
    mlst=mlst.iloc[:,2:len(mlst.columns)]
    mlst_info=mlst.iloc[0,1:len(mlst.columns)].to_list()
    mlst_val=mlst.iloc[1,0:len(mlst.columns)].to_list()
    
    mge=pd.read_csv(("./mge/mge.csv"),skiprows=[0,1,2,3,4]).applymap(str)

    cgmlst=pd.read_csv(("./cgMLST/spneumoniae_summary.txt"),sep="\t").applymap(str)
    cgmlst.iloc[:,1:len(cgmlst.columns)]
    cgmlst=cgmlst[['cgST',"Total_number_of_loci","Number_of_called_alleles","%_Called_alleles","Allele_matches_in_cgST","%_Allele_matches"]]
    for col in cgmlst.columns:
        cgmlst.rename(columns={col:col.replace("_"," ")},inplace=True)
    
    kraken=pd.read_csv(("./kraken/result.bracken"),sep="\t",keep_default_na=False)[0:5].applymap(str)
    amr=pd.read_csv(("./AMR/abricate_result.tsv"),sep="\t",keep_default_na=False).applymap(str)
    amr=amr.loc[:,["SEQUENCE","START","END","STRAND","GENE","%COVERAGE","%IDENTITY","RESISTANCE"]]
    quast=pd.read_csv(("./quast/transposed_report.tsv"),sep="\t",keep_default_na=False).applymap(str)
    quast=quast.loc[:,["# contigs","Largest contig","Total length","GC (%)","N50","N90"]]
    prokka=pd.read_csv(("./prokka/prokka.tsv"),sep="\t",keep_default_na=False)[0:20].applymap(str)
    poppunk=pd.read_csv(("./poppunk/poppunk_external_clusters.csv"),keep_default_na=False,names=["sample","The Global Pneumococcal Sequencing Project Cluster"],header=0).applymap(str)
    poppunk=poppunk.loc[:,["The Global Pneumococcal Sequencing Project Cluster"]]
    plasmid=pd.read_csv(("./plasmid/plasmid.csv"),keep_default_na=False).applymap(str)
    plasmid=plasmid.loc[:,["SEQUENCE","START","END","STRAND","GENE","%COVERAGE","%IDENTITY","PRODUCT"]]
    
    pbp_category=pd.read_csv("./pbptyping/pbp_Category.txt",sep="\t")
    pbp_agent=pd.read_csv("./pbptyping/pbp_agent.txt",sep="\t")

    #with open("./plasmid/result.json") as j:
    #    data=j.read()
    #    plasmid=ast.literal_eval(data)
    #    plasmid=plasmid["plasmidfinder"]["results"]
    #blast=pd.read_excel(("./blast/blast_result_summary.xlsx"))
    #blast.columns = ['contig', 'top1', 'top2', 'top3', 'top4', 'top5']
    return species, quast, sero_bool, sero_txt, seroba, vir, mlst_info, mlst_val, mge, cgmlst, kraken, plasmid, amr, prokka, poppunk, pbp_category, pbp_agent

    
def run_pipeline(path_name,file1,file2,home_path="/home/iu98/pneumo_page"):
    os.chdir(path_name)
    print(path_name)
    os.system("ls -l | grep ^d | awk '{print $NF}' | xargs rm -rf\n")
    run_fastqc(file1,file2)
    #flag=read_qc(file1,file2)
    #if flag:
    #    run_trim(path_name,file1,file2)
    #    file1=file1.split(".")+"_trim.fastq.gz"
    #    file2=file2.split(".")+"_trim.fastq.gz"
    run_kraken2(file1,file2)
    kraken=pd.read_csv(("./kraken/result.bracken"),sep="\t",keep_default_na=False)[0:1]
    if kraken.loc[0,"name"]!="Streptococcus pneumoniae":
        run_spades(file1,file2)
        run_quast()
        return False
    #else:
    run_spades(file1,file2)
    run_quast()
    run_seroba(file1,file2)
    run_prokka()
    run_poppunk()
    run_MGE()
    run_cgMLST()
    run_MLST()
    run_virulencefinder()
    run_abricate()
    run_plasmidfinder()
    run_pbpfinder()
    print("All Done!")
    os.chdir(home_path)
    return True

def run_with_web(user_key,job_info):
    os.chdir("/home/iu98/pneumo_page")
    job_key=job_info["job_key"]
    try:
        path_name=os.path.join("./user/",str(user_key),str(job_key))
        file1=job_info["file1"]
        file2=job_info["file2"]

        db.update_db(user_key,job_key,"running")
        result=run_pipeline(path_name,file1,file2)
        if not result:
            os.chdir("/home/iu98/pneumo_page")
            db.update_db(user_key,job_key,"fail")    
    except Exception as e:
        print(e)
        os.chdir("/home/iu98/pneumo_page")
        db.update_db(user_key,job_key,"fail")
    else:
        os.chdir("/home/iu98/pneumo_page")
        db.update_db(user_key,job_key,"complete")


if __name__ == '__main__':
    user_key=sys.argv[1]
    job_key=sys.argv[2]
    file1=sys.argv[3]
    file2=sys.argv[4]
    job_info={}
    job_info["job_key"]=job_key
    job_info["file1"]=file1
    job_info["file2"]=file2
    print("Run S.pneumoniae analysis...")
    run_with_web(user_key,job_info)
    print("All Done!")