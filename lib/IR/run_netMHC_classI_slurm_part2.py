"""
@authors: Juan L. Trincado
@email: juanluis.trincado@upf.edu

run_netMHC-4.0: run netMHC-4.0 on each sample
"""

import pandas as pd
from argparse import ArgumentParser, RawTextHelpFormatter
import logging, sys, os, re
import subprocess
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

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


def run_netMHC_classI_slurm_part2(input_list_path, HLAclass_path, HLAtypes_path, input_sequence_pieces_path, output_netMHC_path,
                                  output_peptides_path,output_peptides_all_path,output_peptides_path2, output_peptides_all_path2,
                                  output_list_path,netMHC_path):
    try:
        logger.info("Starting execution")

        # input_list_path = sys.argv[1]
        # HLAclass_path = sys.argv[2]
        # HLAtypes_path = sys.argv[3]
        # input_sequence_pieces_path = sys.argv[4]
        # output_netMHC_path = sys.argv[5]
        # output_peptides_path = sys.argv[6]
        # output_peptides_all_path = sys.argv[7]
        # output_peptides_path2 = sys.argv[8]
        # output_peptides_all_path2 = sys.argv[9]
        # output_list_path = sys.argv[10]
        # netMHC_path = sys.argv[11]
        #
        # input_list_path = "/projects_rg/SCLC_cohorts/cis_analysis/v5/SCLC_v5/tables_v2/IR_ORF_filtered_peptide_change.tab"
        # HLAclass_path = "/projects_rg/SCLC_cohorts/tables/PHLAT_summary_ClassI_all_samples.out"
        # HLAtypes_path = "/projects_rg/SCLC_cohorts/tables/NetMHC-4.0_HLA_types_accepted.tab"
        # input_sequence_pieces_path = "/projects_rg/SCLC_cohorts/cis_analysis/v5/SCLC_v5/tables_v2/RI_fasta_files"
        # output_netMHC_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_files"
        # output_peptides_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_3.tab"
        # output_peptides_all_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_3_all.tab"
        # output_peptides_path2 = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_2.tab"
        # output_peptides_all_path2 = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_2_all.tab"
        # output_list_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_junctions_ORF_filtered_neoantigens.tab"
        # netMHC_path = "/users/genomics/juanluis/Software/netMHC-4.0/netMHC"

        # input_list_path = "/projects_rg/SCLC_cohorts/Smart/IR_v2/IR_ORF_filtered_peptide_change.tab"
        # HLAclass_path = "/projects_rg/SCLC_cohorts/Smart/PHLAT/PHLAT_summary_ClassI.out"
        # HLAtypes_path = "/projects_rg/SCLC_cohorts/tables/NetMHC-4.0_HLA_types_accepted.tab"
        # input_sequence_pieces_path = "/projects_rg/SCLC_cohorts/Smart/IR_v2/RI_fasta_files"
        # output_netMHC_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_files"
        # output_peptides_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_3.tab"
        # output_peptides_all_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_3_all.tab"
        # output_peptides_path2 = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_2.tab"
        # output_peptides_all_path2 = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_neoantigens_type_2_all.tab"
        # output_list_path = "/users/genomics/juanluis/SCLC_cohorts/cis_analysis/netMHC-4.0_IR/IR_NetMHC-4.0_junctions_ORF_filtered_neoantigens.tab"
        # netMHC_path = "/users/genomics/juanluis/Software/netMHC-4.0/netMHC"


        # Load the list of accepted HLA types
        logger.info("Load the list of accepted HLA types")
        HLA_accepted_types = set()
        with open(HLAtypes_path) as f:
            for line in f:
                tokens = line.rstrip()
                HLA_accepted_types.add(tokens)

        # Assign to each sample their corresponding HLA types according to the results with seq2HLA
        logger.info("Assigning the prediction for the HLA types to each sample")
        HLA_samples = {}
        with open(HLAclass_path) as f:
            next(f)
            cont = 0
            for line in f:
                cont += 1
                tokens = line.rstrip().split("\t")
                # Check if the HLA_types are significant and if that type exists
                aux = "HLA-" + tokens[1].replace("'", "").replace("*", "").replace(":", "")
                # A1 class
                if (float(tokens[2]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[3].replace("'", "").replace("*", "").replace(":", "")
                # A2 class
                if (float(tokens[4]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[5].replace("'", "").replace("*", "").replace(":", "")
                # B1 class
                if (float(tokens[6]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[7].replace("'", "").replace("*", "").replace(":", "")
                # B2 class
                if (float(tokens[8]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[9].replace("'", "").replace("*", "").replace(":", "")
                # C1 class
                if (float(tokens[10]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)
                aux = "HLA-" + tokens[11].replace("'", "").replace("*", "").replace(":", "")
                # C2 class
                if (float(tokens[12]) <= 0.05 and aux in HLA_accepted_types):
                    if (tokens[0] not in HLA_samples):
                        HLA_samples[tokens[0]] = [aux]
                    else:
                        if (aux not in HLA_samples[tokens[0]]):
                            HLA_samples[tokens[0]].append(aux)

        # Go over the input file, running netMHC
        logger.info("Processing samples for running netMHC")
        open_peptides_file = open(output_peptides_path, "w")
        open_peptides_file.write("Exonization\tSample_ID\tHLA_type\tPredicted_neoantigen\tBinding_affinity\n")
        open_peptides_file2 = open(output_peptides_path2, "w")
        open_peptides_file2.write("Exonization\tSample_ID\tHLA_type\tPredicted_neoantigen\tBinding_affinity\n")
        open_peptides_all_file = open(output_peptides_all_path, "w")
        open_peptides_all_file.write("Exonization\tSample_ID\tHLA_type\tPredicted_neoantigen\tBinding_affinity\n")
        open_peptides_all_file2 = open(output_peptides_all_path2, "w")
        open_peptides_all_file2.write("Exonization\tSample_ID\tHLA_type\tPredicted_neoantigen\tBinding_affinity\n")
        status_neoantigen = []
        cont = 0
        with open(input_list_path) as f:
            next(f)
            for line in f:
                cont += 1
                # if(cont==3):
                #     break
                logger.info("Index: " + str(cont))
                tokens1 = line.rstrip().split("\t")
                index = tokens1[0]
                exonization = tokens1[1]
                sample = tokens1[4].rstrip()
                #Format the sample
                sample = sample.replace("X","").replace(".","-")
                results_by_exon = []
                # Get the HLA types associated. Run netMHC for each HLA type
                if (sample in HLA_samples):
                    HLA_types = HLA_samples[sample]
                    cont2 = 0
                    for x in HLA_types:
                        logger.info("HLA-type: " + x)
                        cont2 += 1
                        # command = netMHC_path + " -a " + x + " -l 8,9,10,11 " + input_sequence_pieces_path + "/" + index + \
                        #           ".fa > " + output_netMHC_path + "/" + index + "_" + x + ".out"
                        # os.system(command)
                        # Load the results
                        flag1, flag2, flag3 = False, False, False
                        # Two structures: one for all the peptides predicted and other for only the ones with good afinity
                        ref_binders, ex_binders, ref_good_binders, ex_good_binders = {}, {}, {}, {}
                        cont3 = 0
                        with open(output_netMHC_path + "/" + index + "_" + x + ".out") as f:
                            for line in f:
                                cont3 += 1
                                # 000
                                if (not flag1 and not flag2 and not flag3 and
                                            line.rstrip() == "-----------------------------------------------------------------------------------"):
                                    flag1 = True
                                # 100
                                elif (flag1 and not flag2 and not flag3 and
                                              line.rstrip() == "-----------------------------------------------------------------------------------"):
                                    flag2 = True
                                # 110 and not line ---
                                elif (flag1 and flag2 and not flag3 and not
                                    line.rstrip() == "-----------------------------------------------------------------------------------"):
                                    # Get first the pos and then the rest of the line
                                    tokens2 = line.split()
                                    bind_affinity = float(tokens2[12].strip())
                                    peptide = tokens2[2].strip()
                                    identity = tokens2[10].strip()
                                    # Save the peptide
                                    if (identity[0] == "r"):
                                        if (peptide not in ref_binders):
                                            ref_binders[peptide] = bind_affinity
                                        else:
                                            # raise Exception("Repeated peptide "+peptide+" in ref_binders")
                                            pass
                                    else:
                                        if (peptide not in ex_binders):
                                            ex_binders[peptide] = bind_affinity
                                        else:
                                            # raise Exception("Repeated peptide "+peptide+" in ex_binders")
                                            pass
                                    # Save the peptide if the affinity is lower than 500nm
                                    if (bind_affinity < 500):
                                        if (identity[0] == "r"):
                                            if (peptide not in ref_good_binders):
                                                ref_good_binders[peptide] = bind_affinity
                                            else:
                                                # raise Exception("Repeated peptide "+peptide+" in ref_binders")
                                                pass
                                        else:
                                            if (peptide not in ex_good_binders):
                                                ex_good_binders[peptide] = bind_affinity
                                            else:
                                                # raise Exception("Repeated peptide "+peptide+" in ex_binders")
                                                pass
                                # 110 and line ---
                                elif (flag1 and flag2 and not flag3 and
                                              line.rstrip() == "-----------------------------------------------------------------------------------"):
                                    flag3 = True
                                # 111
                                elif (flag1 and flag2 and flag3 and
                                              line.rstrip() == "-----------------------------------------------------------------------------------"):
                                    flag1 = False
                                # 011
                                elif (not flag1 and flag2 and flag3 and
                                              line.rstrip() == "-----------------------------------------------------------------------------------"):
                                    flag2 = False
                                # 001
                                elif (not flag1 and not flag2 and flag3 and
                                              line.rstrip() == "-----------------------------------------------------------------------------------"):
                                    # Start again the normal lines (110)
                                    flag1 = True
                                    flag2 = True
                                    flag3 = False
                                else:
                                    pass

                                    # Report all the peptides in ex_binder that are not in ref_binder
                                    # All the peptides that are in both will be not taken intop account

                                    # In addition, we will return in the list of the exonizations (per HLA-type) if:
                                    # 1. no neoantigens in ref nor ex
                                    # 2. neoantigens in ref but no in ex
                                    # 3. neoantigens in ex but no in ref
                                    # 4. neoantigens in both

                        flag_neoantigens_ref, flag_neoantigens_ex = False, False
                        for element, values in ref_good_binders.items():
                            if (element not in ex_binders):
                                flag_neoantigens_ref = True
                                # Save this to the output
                                open_peptides_file2.write(
                                    exonization + "\t" + sample + "\t" + x + "\t" + element + "\t" +
                                    str(values) + "\n")
                        for element, values in ex_good_binders.items():
                            if (element not in ref_binders):
                                flag_neoantigens_ex = True
                                # Save this to the output
                                open_peptides_file.write(
                                    exonization + "\t" + sample + "\t" + x + "\t" + element + "\t" +
                                    str(values) + "\n")

                        # Save all the peptides in another file
                        for element, values in ref_binders.items():
                            open_peptides_all_file2.write(
                                exonization + "\t" + sample + "\t" + x + "\t" + element + "\t" +
                                str(values) + "\n")

                        for element, values in ex_binders.items():
                            open_peptides_all_file.write(
                                exonization + "\t" + sample + "\t" + x + "\t" + element + "\t" +
                                str(values) + "\n")

                        if (not flag_neoantigens_ref and not flag_neoantigens_ex):
                            results_by_exon.append((x, "1"))
                        elif (flag_neoantigens_ref and not flag_neoantigens_ex):
                            results_by_exon.append((x, "2"))
                        elif (not flag_neoantigens_ref and flag_neoantigens_ex):
                            results_by_exon.append((x, "3"))
                        else:
                            results_by_exon.append((x, "4"))

                else:
                    pass

                # Save the list of results by exon
                status_neoantigen.append(results_by_exon)

        open_peptides_file.close()
        open_peptides_file2.close()
        open_peptides_all_file.close()
        open_peptides_all_file2.close()
        logger.info("Saved " + output_peptides_path)
        logger.info("Saved " + output_peptides_path2)
        logger.info("Saved " + output_peptides_all_path)
        logger.info("Saved " + output_peptides_all_path2)

        # Assign the status_neoantigen to the list of the exonizations
        exonizations = pd.read_table(input_list_path, delimiter="\t")
        exonizations["status_neoantigen"] = status_neoantigen
        exonizations.to_csv(output_list_path, sep="\t", index=False)
        logger.info("Saved " + output_list_path)

        logger.info("Done. Exiting program.")

    except Exception as error:
        logger.error('ERROR: ' + repr(error))
        logger.error("Aborting execution")
        sys.exit(1)
