#!/usr/bin/env python3.8

import os
import sys
from pathlib import Path
import db
import subprocess

async def run_mapping(username,key):
    path_name="./user/"+username
    file_all=os.listdir(path_name)
    file_list=[file for file in file_all if file.endswith(".fastq.gz")]
    file_list.sort()

    qc=30
    trim=50
    for i in range(0,len(file_list),2):
        try:
            db.update_db(username,key,"running")
            command = ['non_adapt_pre-processing.py', "./user/"+username+"/"+file_list[i] , "./user/"+username+"/"+file_list[i+1], str(qc), str(trim),
                       "./reference/GRCh38_latest_genomic.fna", "./reference/GCF_002076835.1_ASM207683v1_genomic.fna","user/"+username+"/"]
            subprocess.call(command)
        except:
            db.update_db(username,key,"fail")
            return False                
    
