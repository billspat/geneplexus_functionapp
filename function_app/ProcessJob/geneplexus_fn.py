import logging
import os, sys, json

from geneplexus import geneplexus
from geneplexus.util import read_gene_list

import pandas as pd
from pprint import pprint

#TODO  sanitize jobid

def run_job(jobid, job_dir, data_path, input_genes_file, logging, 
    net_type='BioGRID',
    features='Embedding',
    GSC='GO'
    ):
 
    logging.info("reading input_genes_file " + input_genes_file)
    try:
        gene_list = read_gene_list(input_genes_file)
        gene_count = str(len(gene_list))
        logging.info(f"read {gene_count} genes")
        logging.info(str(gene_list))

    except Exception as e:
        err_msg = "reading input genes error: " + str(e)
        logging.error(err_msg)
        raise

    try:   
        logging.info('starting gp model run')
        df_probs, df_GO, df_dis, avgps, df_edgelist, df_convert_out, positive_genes = run_model(data_path, gene_list, net_type, features, GSC)

        graph = make_graph(df_edgelist, df_probs)

        logging.info('gp model complete')

    except Exception as e:
        err_msg = "run_model error: " + str(e)
        logging.error(err_msg)
        raise

    try:
        input_count = df_convert_out.shape[0]
    except Exception as e:
        err_msg = "df_convert_out error: " + str(e)
        logging.error(err_msg)
        raise

    try:
        print("saving output")
        job_info = save_output(job_dir, jobid, net_type, features, GSC, avgps, input_count, positive_genes, df_probs, df_GO, df_dis, df_convert_out, graph, df_edgelist)
        logging.info("job completed and output saved")

    except Exception as e:
        err_msg = "saving model error: " + str(e) 
        logging.error(err_msg)
        raise

    return True



def run_model(data_path, convert_IDs, net_type='String',features='Embedding', GSC='GO'):
    gp = geneplexus.GenePlexus(data_path, net_type, features, GSC)
    gp.load_genes(convert_IDs)
    mdl_weights, df_probs, avgps = gp.fit_and_predict()
    df_sim_go, df_sim_dis, weights_go, weights_dis = gp.make_sim_dfs()
    df_edgelist, isolated_genes, df_edge_sym, isolated_genes_sym = gp.make_small_edgelist()
    df_convert_out, positive_genes = gp.alter_validation_df()
    return df_probs, df_sim_go, df_sim_dis, avgps, df_edgelist, df_convert_out, positive_genes

def make_graph(df_edge, df_probs, max_num_genes = 50):
    df_edge.fillna(0)
    df_edge.columns = ['source', 'target', 'weight']
    nodes = df_probs[0:max_num_genes]
    nodes.rename(columns={'Entrez': 'id', 'Class-Label': 'Class'}, inplace=True)
    nodes = nodes.astype({'id': int})

    graph = {}
    graph["nodes"] = nodes.to_dict(orient='records')
    graph["links"] = df_edge.to_dict(orient='records')

    return graph

def save_df_output(job_dir, jobname, output_name, output_df):
    """ save data frames from model runs in a consistent way"""
    output_filename = construct_output_filename(jobname, output_name, '.tsv')
    output_filepath=construct_output_filepath(job_dir, jobname, output_filename)
    output_df.to_csv(path_or_buf = output_filepath, sep = '\t', index = False, line_terminator = '\n')
    return(output_filename)

def save_txt_output(job_dir, jobname, output_name, output_content):
    """ save any data from job, output name must have the extension"""
    output_filename = construct_output_filename(jobname, output_name)
    output_filepath = construct_output_filepath(job_dir, jobname, output_filename)
    try:
        with open(output_filepath, 'w') as outfile:
            outfile.writelines(output_content)
        return(output_filename)
    except Exception as e:
        return("")       

    

def save_graph_output(job_dir, jobname, graph):
    """save the data that makes up the network graph to output folder, in JSON format.  
    the 'graph' is a dict of dicts (node, edges), so just save as json"""
    graph_file = construct_output_filename(jobname, 'graph', 'json')
    graph_file_path = construct_output_filepath(job_dir, jobname, graph_file)
    with open(graph_file_path, 'w') as gf:
        json.dump(graph, gf)

    return(graph_file)

def save_output(job_dir, jobname, net_type, features, GSC, avgps, input_count, positive_genes, 
    df_probs, df_GO, df_dis, df_convert_out_subset, graph, df_edgelist):

    # TODO : send outputs to save as a dictionary keyed on name.e.g. {'df_probs', df_probs, etc } 
    #        so this module can be more generic.   possibly also add format per item, or use same format for all (JSON or CSV)
    # save all data frames to files in standard format
    df_probs_file = save_df_output(job_dir, jobname, 'df_probs', df_probs)
    df_GO_file = save_df_output(job_dir, jobname, 'df_GO',df_GO )
    df_convert_out_subset_file = save_df_output(job_dir, jobname, 'df_convert_out_subset', df_convert_out_subset)
    df_dis_file = save_df_output(job_dir, jobname, 'df_dis',df_dis)
    df_edgelist_file = save_df_output(job_dir, jobname, 'df_edgelist', df_edgelist )
    
    # the 'graph' is a dict of dicts (node, edges), so save in different format
    graph_file = save_graph_output(job_dir, jobname, graph)

    # HACK  the app jobs module looks for this file to determine if the job is complete. 
    # TODO remove this after jobs module/class is refactored
    results_file_content = f"<html><body><p>{jobname}</p></html>"
    results_file_name = f"{jobname}_results.txt"
    save_txt_output(job_dir, jobname, results_file_name, results_file_content )

    # copy the results file names into this dictionary (without path) 
    job_info = {
        'jobname': jobname,
        'net_type': net_type,
        'features': features,
        'GSC': GSC,
        'avgps': avgps, 
        'input_count': input_count, 
        'positive_genes': positive_genes,
        'df_probs_file': df_probs_file, 
        'df_GO_file': df_GO_file, 
        'df_dis_file': df_dis_file, 
        'df_convert_out_subset_file': df_convert_out_subset_file, 
        'graph_file':  graph_file,
        'df_edgelist_file' : df_edgelist_file
        }

    print(job_info, file=sys.stderr)
    
    job_info_path = construct_output_filepath(job_dir, jobname, 'job_info', ext = 'json')
    print(f"saving job info to {job_info_path} ",file=sys.stderr)   
    with open(job_info_path, 'w') as jf:
        json.dump(job_info, jf)

    return(job_info)

def construct_output_filename(jobname, output_name, ext = ''):
    """ consistently create output file name from path and job name"""
    # note that when opening a new db files with shelve, it will automatically add .db, so don't add it here"
    if( ext and ext[0] != '.'):
        ext = '.' + ext

    output_file = jobname + '_' +  output_name +  ext
    return(output_file)

def construct_output_filepath(job_dir, jobname, output_name, ext = ''):
    """ consistently create output file name from path and job name"""
    # note that when opening a new db files with shelve, it will automatically add .db, so don't add it here"
    if( ext and ext[0] != '.'):
        ext = '.' + ext

    # note this is not currenlty using the job name!  
    #  this is because for the job runner, the full output path for this one job is provided (with the jobname already in it)
    output_file_path = os.path.join(job_dir, output_name +  ext)
    return(output_file_path)

