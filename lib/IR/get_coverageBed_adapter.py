"""
@authors: Juan L. Trincado
@email: juanluis.trincado@upf.edu

get_coverageBed_adapter: this is an adapter, for running a job per sample in the slurm cluster

"""

import pandas as pd
from argparse import ArgumentParser, RawTextHelpFormatter
import logging, sys, os, re
from statsmodels.distributions.empirical_distribution import ECDF
import subprocess



# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def extract_number(id):
    '''
    Extract the number id. If there is not, return a 0:
    '''
    try:
        return int(id.split("_")[3])
    except:
        return 0

# def get_job_ids(list):
#     for x in list:



def get_coverageBed_adapter(input_path, gtf_path, coverage_path, output_path, name_user):

    try:
        logger.info("Starting execution")

        # input_path = sys.argv[1]
        # gtf_path = sys.argv[2]
        # coverage_path = sys.argv[3]
        # output_path = sys.argv[4]
        # temp_path = sys.argv[5]

        # input_path = "/projects_rg/SCLC_cohorts/cis_analysis/v5/SCLC_v5/tables/IR_significant_genes_filtered2.tab"
        # gtf_path = "/projects_rg/SCLC_cohorts/cis_analysis/v5/SCLC_v5/tables/random_introns.bed"
        # coverage_path = "/projects_rg/SCLC_cohorts/coverageBed/intron_retention/IR_v5"
        # output_path = "/projects_rg/SCLC_cohorts/cis_analysis/v5/SCLC_v5/tables/IR_significant_genes_filtered3.tab"
        # temp_path = "/users/genomics/juanluis/SCLC_cohorts/George/coverageBed/scripts"

        # Load the gtf file
        # logger.info("Loading gtf with the randomizations...")
        # gtf = pd.read_table(gtf_path, delimiter="\t")
        # gtf.columns = ['chr','start','end','id','strand','score']

        # Load the input file
        logger.info("Loading introns...")
        introns = pd.read_table(input_path, delimiter="\t")
        unique_introns = introns.drop_duplicates(['Sample_id'])
        unique_sample_ids = unique_introns.loc[:,"Sample_id"].tolist()
        dir_path = os.path.dirname(os.path.realpath(__file__))

        # Split the input_path and the gtf_path by sample
        dict_jobs = {}
        for sample in unique_sample_ids:
            # Format the sample
            # Only the samples ont from George or Peifer
            if(sample[0:2]=="SM" or sample[0]=="X"):
                continue
            # Remove T's and X's and replace _ by .
            sample_formatted = sample.replace("T","").replace("X","").replace(".","-")
            # command1="head -1 "+input_path+" > "+output_path+"/input.aux."+sample_formatted+".tab" +";grep \""+sample_formatted+"\" "+input_path+\
            #          " >> "+output_path+"/input.aux."+sample_formatted+".tab"
            command1 = "head -1 " + input_path + " > " + output_path + "/input.aux." + sample_formatted + ".tab" + ";" \
                        "awk '{if ($4==\"" + sample + "\") print }' " + input_path + " >> " + output_path + "/input.aux." \
                       + sample_formatted + ".tab"
            # print(command1)
            os.system(command1)
            sample_formatted = "CULO"
            # Create an auxiliary script
            command3 = "module load Python; python "+dir_path+"/get_coverageBed.py " \
                       + output_path+"/input.aux."+sample_formatted+".tab " + gtf_path + " " + coverage_path + " " + \
                       output_path + "/get_coverageBed_results." + sample_formatted + ".tab True"
            # print(command3)
            open_peptides_file = open(output_path + "/aux.sh", "w")
            open_peptides_file.write("#!/bin/sh\n")
            open_peptides_file.write("#SBATCH --partition=normal\n")
            open_peptides_file.write("#SBATCH --mem 10000\n")
            open_peptides_file.write("#SBATCH -e " + output_path + "/" + "get_coverageBed" + "_" + sample_formatted + ".err" + "\n")
            open_peptides_file.write("#SBATCH -o " + output_path + "/" + "get_coverageBed" + "_" + sample_formatted + ".out" + "\n")
            open_peptides_file.write(command3 + ";\n")
            open_peptides_file.close()
            command4 = "sbatch -J "+sample_formatted+"_coverageBed " + output_path + "/aux.sh; sleep 0.5;"
            # os.system(command4)
            job_message = subprocess.check_output(command4, shell=True)
            #Get the job id and store it
            job_id = (str(job_message).rstrip().split(" ")[-1])[:-3]
            dict_jobs[job_id] = 1
            logger.info("job_id run:" + str(job_id))

            break

        logger.info("Waiting for all the jobs to finished...")
        flag_exit = False
        while(not flag_exit):
            # Initialize the dictionary with the pending jobs in the cluster
            pending_jobs = {}
            logger.info("Sleeping 10 seconds...")
            os.system("sleep 10")
            p = subprocess.Popen(["squeue","-u", name_user], stdout=subprocess.PIPE)
            # out = p.stdout.read()
            # logger.info("Printing squeue: "+str(out))
            while True:
                logger.info("Entering second loop...")
                line = p.stdout.readline()
                logger.info("Line: "+str(line))
                if line != '':
                    #Get the id of the job
                    job_id_aux = (str(job_message).rstrip().split(" ")[-1])[:-3]
                    logger.info("job_id cluster:" + str(job_id_aux))
                    #Save the id of the jobs
                    pending_jobs[job_id_aux] = 1
                    #If there is any job on the cluster on dict_jobs, break the loop and wait for another 10 seconds
                    # to check the status of the jobs in the cluster
                    if(job_id_aux in dict_jobs):
                        break
                else:
                    #If we have reach the end of the status and there is no job pending, end the execution
                    flag_exit = True
                    break

        logger.info("All jobs finished.")


    except Exception as error:
        logger.error('ERROR: ' + repr(error))
        logger.error("Aborting execution")
        sys.exit(1)
