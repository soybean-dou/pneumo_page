#!/usr/bin/env python3.8

import os
import sys
import argparse
from copy import deepcopy
import time
import subprocess
import inspect
import csv

#FastQC results save
def FastQC():
    command = ['fastqc', '-t', '10', '-o', fastqc_out_dir1, inputread1, inputread2]
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    subprocess.call(command)

#Adapter trimming - cutadapt
def Cutadapt():
    command = ['cutadapt', '-a', AdapterseqFwd, '-A', AdapterseqRev,
            '-o', cuttedR1, '-p', cuttedR2, inputread1, inputread2]
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    subprocess.call(command)

#    command = ['cutadapt', '-a', 3adapter,
#            '-o', cuttedR2, inputread2]
#    subprocess.call(command)
#
#
#    commnad = ['cutadapt', '-g', 5adapter,
#            '-o', cuttedR1, inputread1]
#    subprocess.call(command)

#Quality control - sickle
def Sickle():
    command = ['sickle', 'pe',
            '-f', cuttedR1,
            '-r', cuttedR2,
            '-t', 'sanger',
            '-o', trimmedR1,
            '-p', trimmedR2,
            '-s', trimmedSingle,
            '-q', str(QS),
            '-l', str(trimmedlength)]
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    subprocess.call(command)

def adapt_FastQC():
    command = ['fastqc', '-t', '10', '-o', fastqc_out_dir2, trimmedR1, trimmedR2]
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    subprocess.call(command)

def REF_Indexing():
    command = ['bwa-mem2', 'index', Human_Ref_seq]
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    subprocess.call(command)

    command = ['bwa-mem2', 'index', Custom_Ref_seq]
    subprocess.call(command)

def Human_Alignment():
    #command = ['bwa-mem2', 'mem', '-t', '10', Human_Ref_seq, trimmedR1, trimmedR2, '>', aligned_sam]
    #command = ['bwa-mem2', 'mem', '-t', '10', Human_Ref_seq, trimmedR1, trimmedR2]
    cmd = 'bwa-mem2 mem -t 10 ' + Human_Ref_seq + ' ' + trimmedR1 + ' ' + trimmedR2 + ' > ' + aligned_sam
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    #subprocess.call(command)
    os.system(cmd)

    # Sam to Bam converting

    #command = ['samtools', 'view', '-S', '-b', aligned_sam, '>', aligned_bam]
    #command = ['samtools', 'view', '-S', '-b', aligned_sam]
    #subprocess.call(command, stdout = open(aligned_bam, 'w'))
    cmd = 'samtools view -S -b ' + aligned_sam + ' > ' + aligned_bam
    print('\n',cmd, '\n')
    os.system(cmd)
    # -n 옵션을 사용하지 않고 qualimap 용 sorted bam file을 만듦
    command = ['samtools', 'sort', aligned_bam, '-o', sorted_aligned_bam]
    print('\n',command, '\n')
    subprocess.call(command)

def Human_Align_QC():
    command = ['qualimap', '--java-mem-size=32G', 'bamqc', '-bam', sorted_aligned_bam, '-outdir', qualimap_results_human, '-outformat ', 'pdf']
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    subprocess.call(command)

def Extract_Unmapped():
    #command = ['samtools', 'view', '-b', '-f', '4', aligned_sam, '>', unmapped_bam]
    #command = ['samtools', 'view', '-b', '-f', '4', aligned_sam]
    cmd = 'samtools view -b -f 4 ' + aligned_sam + ' > ' + unmapped_bam
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    #subprocess.call(command, stdout = open(unmapped_bam, 'w'))
    os.system(cmd)
    

    command = ['samtools', 'sort', '-n', unmapped_bam, '-o', unmapped_sorted_bam]
    command = ['samtools', 'sort', unmapped_bam, '-o', p_unmapped_sorted_bam]

    print('\n',command, '\n')
    subprocess.call(command)

    command = ['bedtools', 'bamtofastq', '-i', unmapped_sorted_bam, '-fq', unmapped_R1, '-fq2', unmapped_R2]
    subprocess.call(command)

def Custom_Ref_Alignment():
    #command = ['bwa-mem2', 'mem', '-t', '10', Custom_Ref_seq, unmapped_R1, unmapped_R2, '>', custom_aligned_sam]
    cmd = 'bwa-mem2 mem -t 10 ' + Custom_Ref_seq + ' ' + unmapped_R1 + ' ' + unmapped_R2 + ' > ' + custom_aligned_sam
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    #subprocess.call(command)
    os.system(cmd)
    #command = ['samtools', 'view', '-b', custom_aligned_sam, '>', custom_aligned_bam]
    cmd = 'samtools view -b ' + custom_aligned_sam + ' > ' + custom_aligned_bam
    print('\n',cmd, '\n')
    #subprocess.call(command)
    os.system(cmd)
    # -n 옵션을 사용하지 않고 qualimap 용 sorted bam file을 만듦
    command = ['samtools', 'sort', custom_aligned_bam, '-o', sorted_custom_aligned_bam]
    print('\n',command, '\n')
    subprocess.call(command)
    
def Custom_Align_QC():
    command = ['qualimap', '--java-mem-size=32G', 'bamqc', '-bam', sorted_custom_aligned_bam, '-outdir', qualimap_results_custom, '-outformat', 'pdf']
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    subprocess.call(command)

#PICARD의 경우 파라미터 I=input.bam 식으로 쓰인것만 보여 이 부분 에러시 참고
def Duplicate_mark():
    #command = ['java', '-jar', 'picard.jar', 'MarkDuplicates', 'I=', unmapped_sorted_bam, 'O=', marked_duplicates_bam, 'M=', marked_duplicates_metrics]
    command = ['java', '-jar', 'picard.jar', 'MarkDuplicates', '-I', sorted_custom_aligned_bam, '-O', marked_duplicates_bam, '-M', marked_duplicates_metrics]
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    subprocess.call(command)

def Make_VCF():
    command = ['bcftools', 'mpileup', '--count-orphans', '--no-BAQ', '--min-MQ', '30', '--min-BQ', '30', '--max-depth', '1000000', '-Ov',
            '--annotate', 'FORMAT/AD,FORMAT/ADF,FORMAT/ADR,FORMAT/DP,FORMAT/SP,INFO/AD,INFO/ADF,INFO/ADR',
            '-f', Custom_Ref_seq, marked_duplicates_bam, '--output', custom_vcf_file]
    #cmd = 'bcftools mpileup --count-orphans --no-BAQ --min_MQ 30 --min-BQ 30 --max-depth 100000 -Ov --annotate FORMAT/AD,FOR'
    
    cmd = 'bcftools +fill-tags ' + custom_vcf_file + ' -- -t VAF > ' + VAF_added_vcf_file
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    #print('\n', command, '\n')
    subprocess.call(command)
    print('\n', cmd, '\n')
    os.system(cmd)
    
    #command = ['bcftools', 'view', '-i', '\"MIN(FMT/DP)>100 & FORMAT/VAF>=0.1\"', '-Ov', '--output', filtered_vcf_file, custom_vcf_file]
    #subprocess.call(command)
    
    #cmd = 'samtools mpileup -uf ' + Custom_Ref_seq + ' ' + marked_duplicates_bam + ' | bcftools call -m -v -o ' + custom_vcf_file
    #work_name = inspect.stack()[0][3]
    #print("[{}] {}".format(time.ctime(), work_name))
    #print('\n', cmd, '\n')
    #os.system(cmd)

    #cmd = 'bcftools view -i "MIN(FMT/DP)>100 & (FORMAT/AD)/(FORMAT/DP)>=0.1" -Ov --output-file ' + filtered_vcf_file + ' ' + custom_vcf_file
    cmd = 'bcftools view -i "MIN(FMT/DP)>100 & (FORMAT/VAF)>=0.1" -Ov --output-file ' + filtered_vcf_file + ' ' + VAF_added_vcf_file
    print('\n', cmd, '\n')
    os.system(cmd)

def Annotate_Variation():
    #command = ['java', '-jar', './snpEff/snpEff.jar', 'Streptococcus_pneumoniae_gcf_002076835', filtered_vcf_file, '>', ref_filtered_vcf_file]
    #cmd = 'java -jar ./snpEff/snpEff.jar Streptococcus_pneumoniae_gcf_002076835 ' + filtered_vcf_file + ' > ' + ref_filtered_vcf_file
    cmd = 'java -jar ./snpEff/snpEff.jar GCF_002076835.1 ' + filtered_vcf_file + ' > ' + ref_filtered_vcf_file
    work_name = inspect.stack()[0][3]
    print("[{}] {}".format(time.ctime(), work_name))
    #subprocess.call(command)
    os.system(cmd)


def main():

    FastQC()
    Cutadapt()
    Sickle()
    adapt_FastQC()
    REF_Indexing()
    Human_Alignment()
    Human_Align_QC()
    Extract_Unmapped()
    Custom_Ref_Alignment()
    Custom_Align_QC()
    Duplicate_mark()
    Make_VCF()
    Annotate_Variation()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = "Pre-processing for Pneumoniae analysis Using FastQC, Cutadapt, Sickle",
            epilog = "Parameter 1: read1, 2: read2, 3: QS, 4: Trimmed Length, 5: Foward Adapter sequence, 6: Reverse ADAPTET sequence,\n7: Human reference genome, 8: Custom reference genome, 9: Output DIR")
    parser.add_argument("Input_Read1", type = lambda x: (os.path.abspath(os.path.expanduser(x))))
    parser.add_argument("Input_Read2", type = lambda x: (os.path.abspath(os.path.expanduser(x))))
    parser.add_argument("Quality_Score", type = int)
    parser.add_argument("Trimmed_Length", type = int)
#    parser.add_argument("Adapter position", type = int)
    parser.add_argument("Foward_Adapter_sequence", type = str)
    parser.add_argument("Reverse_Adapter_sequence", type = str)
    parser.add_argument("Human_Ref_sequence", type = lambda x: (os.path.abspath(os.path.expanduser(x))))
    parser.add_argument("Custom_Ref_sequence", type = lambda x: (os.path.abspath(os.path.expanduser(x))))
    parser.add_argument("Output_Dir", type = lambda x: (os.path.abspath(os.path.expanduser(x))))

    args = parser.parse_args()

    # Parameter space
    inputread1 = args.Input_Read1
    inputread2 = args.Input_Read2
    QS = args.Quality_Score
    trimmedlength = args.Trimmed_Length
    AdapterseqFwd = args.Foward_Adapter_sequence
    AdapterseqRev = args.Reverse_Adapter_sequence
    Human_Ref_seq = args.Human_Ref_sequence
    Custom_Ref_seq = args.Custom_Ref_sequence

    # Path space

    cpath = os.getcwd()
    result_dir = args.Output_Dir
    workpath = os.path.join(result_dir, "workpath")
    working_time = time.ctime().replace(' ', '-').replace(':', '-')
    for directory in [result_dir, workpath]:
        if not os.path.isdir(directory):
            os.mkdir(directory)

    fastqc_out_dir1 = os.path.join(workpath, "first_fastqc_output")
    fastqc_out_dir2 = os.path.join(workpath, "adapt_fastqc_output")
    for directory in [fastqc_out_dir1, fastqc_out_dir2]:
        if not os.path.isdir(directory):
            os.mkdir(directory)

    cuttedR1 = os.path.join(workpath, "cutted_Read1.fastq")
    cuttedR2 = os.path.join(workpath, "cutted_Read2.fastq")
    trimmedR1 = os.path.join(workpath, "trimmed_Read1.fastq")
    trimmedR2 = os.path.join(workpath, "trimmed_Read2.fastq")
    trimmedSingle = os.path.join(workpath, "trimmed_Single.fastq")

    aligned_sam = os.path.join(workpath, "aligned_paired.sam")
    aligned_bam = os.path.join(workpath, "aligned_paired.bam")
    sorted_aligned_bam = os.path.join(workpath, "sorted_aligned.bam")
    unmapped_bam = os.path.join(workpath, "unmapped.bam")
    unmapped_sorted_bam = os.path.join(workpath, "unmapped_sorted.bam")
    p_unmapped_sorted_bam = os.path.join(workpath, "p_unmapped_sorted.bam")

    unmapped_R1 = os.path.join(workpath, "unmapped_R1.fastq")
    unmapped_R2 = os.path.join(workpath, "unmapped_R2.fastq")
    custom_aligned_sam = os.path.join(workpath, "custom_aligned.sam")
    custom_aligned_bam = os.path.join(workpath, "custom_aligned.bam")
    sorted_custom_aligned_bam = os.path.join(workpath, "sorted_custom_aligned.bam")
    qualimap_results_human = os.path.join(workpath, "qualimap_results_human")
    qualimap_results_custom = os.path.join(workpath, "qualimap_results_custom")

    marked_duplicates_bam = os.path.join(workpath, "marked_duplicates.bam")
    marked_duplicates_metrics = os.path.join(workpath, "marked_dup_metrics.txt")

    custom_vcf_file = os.path.join(workpath, "custom_vcf_file.vcf")
    VAF_added_vcf_file = os.path.join(workpath, "VAF_added_vcf_file.vcf")
    filtered_vcf_file = os.path.join(workpath, "filtered_vcf_file.vcf")
    ref_filtered_vcf_file = os.path.join(workpath, "ref_filtered_vcf_file.vcf")
    
    main()
























