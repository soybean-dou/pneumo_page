#!/usr/bin/python

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import requests
import xml.etree.ElementTree as ET
import time
from Bio import Entrez, SeqIO


path_name=sys.argv[1]
file_all=os.listdir(path_name)
file_list=[file for file in file_all if os.path.isdir(path_name+"/"+file)]

file_list.sort()

blast_all=list()
species_list=list()

sub_blast=pd.DataFrame
blast_summary=pd.DataFrame
blast_result=pd.read_csv((path_name+path_name+"/blast/blast_result.txt"),sep='\t', header=None)
blast_result.columns =["qseqid","sseqid", "scomnames", "length", "qstart", "qend", "sstart", "send", "evalue", "pident"]

node_index=np.unique(blast_result["qseqid"], return_index=True)[1]
node_name=[]
for i in sorted(node_index):
    node_name.append(blast_result.iloc[i].qseqid)

species_list.append(pd.DataFrame(index=node_name, columns=[1,2,3,4,5]))

for i in range(len(node_name)):
    sub_blast=blast_result[blast_result["qseqid"]==node_name[i]].copy()
    sub_blast=sub_blast.sort_values(by="bitscore",ascending=False)
    sub_blast=sub_blast[:5]
    if(i==0):
        blast_summary=sub_blast.copy()
    else:
        blast_summary=pd.concat([blast_summary,sub_blast],sort=False)
    
blast_all.append(blast_summary)
    


before_node=""
row_num=0
col_num=0
for j in range(len(blast_all[0])):
    if j==0:
        before_node=blast_all[i].iloc[j].qseqid
    node = blast_all[i].iloc[j].qseqid
    id = blast_all[i].iloc[j].sseqid.split("|")[1]
    #r=requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id="+id+"&rettype=native&retmode=xml")
    Entrez.email="iu98@naver.com"
    handle=Entrez.efetch(db="nuccore",id=id, rettype="native", retmode="xml")
    recode=handle.read()
    handle.close()
    root=ET.fromstring(recode)

    name_list=root.findall(".//OrgName/*")
    name=""
    serovar=""
    strain=""
    species=""
    for n in range(len(name_list)):
        name+=name_list[n].text+" "

    if name=="Streptococcus pneumoniae ":
        species+=name
        serovar=root.find(".//OrgMod/OrgMod_subtype[@value='serovar']")
        if serovar is not None:
            serovar=serovar.text
            species+=" "+serovar
        strain=root.find(".//OrgMod/OrgMod_subtype[@value='strain']")
        if strain is not None:
            strain=strain.text
            species+=" "+strain
    else:
        species=name
    if before_node!=node:
        print(before_node+" complete!")
        row_num+=1
        col_num=0
        species_list[i].iloc[row_num,col_num]=species
        col_num+=1
        before_node=node
    else:
        species_list[i].iloc[row_num,col_num]=species
        col_num+=1 
        before_node=node


sheet=pd.ExcelWriter('blast_result_summary.xlsx',engine='xlsxwriter')
for i in range(len(species_list)):
    species_list[i].to_excel(sheet,sheet_name=file_list[i])
sheet.close()