"""
@authors: Juan L. Trincado
@email: juanluis.trincado@upf.edu

get_coverageBed_adapter: this is an adapter, for running a job per sample in the slurm cluster

"""

import pandas as pd
from argparse import ArgumentParser, RawTextHelpFormatter
import logging, sys, os, re
from statsmodels.distributions.empirical_distribution import ECDF


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


def get_coverageBed_adapter(input_path, gtf_path, coverage_path, output_path):

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
        for sample in unique_sample_ids:
            # Format the sample
            # Only the samples ont from George or Peifer
            if(sample[0:2]=="S0" or sample[0]=="X"):
                continue
            # Remove T's and X's and replace _ by .
            sample_formatted = sample.replace("T","").replace("X","").replace(".","-")
            # Create an auxiliary script
            command3 = "module load Python; python "+dir_path+"/get_coverageBed.py " \
                       + output_path+"/input.aux."+sample_formatted+".tab " + gtf_path + " " + coverage_path + " " + \
                       output_path + "/get_coverageBed_results." + sample_formatted + ".tab"
            print(command3)
            open_peptides_file = open(output_path + "/aux.sh", "w")
            open_peptides_file.write("#!/bin/sh\n")
            open_peptides_file.write("#SBATCH --partition=normal\n")
            open_peptides_file.write("#SBATCH --mem 10000\n")
            open_peptides_file.write("#SBATCH -e " + output_path + "/" + "get_coverageBed" + "_" + sample_formatted + ".err" + "\n")
            open_peptides_file.write("#SBATCH -o " + output_path + "/" + "get_coverageBed" + "_" + sample_formatted + ".out" + "\n")
            open_peptides_file.write(command3 + ";\n")
            open_peptides_file.close()
            command4 = "sbatch -J "+sample_formatted+"_coverageBed " + output_path + "/aux.sh; sleep 0.5"
            os.system(command4)

        logger.info("Done. When all jobs finished, pool all results into single file")

    except Exception as error:
        logger.error('ERROR: ' + repr(error))
        logger.error("Aborting execution")
        sys.exit(1)