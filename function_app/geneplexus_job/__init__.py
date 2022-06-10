from ast import Str
import logging
import os, sys, json
import azure.functions as func


from geneplexus import geneplexus
import pandas as pd
from pprint import pprint

input_genes = ["CCNO",
    "CENPF",
    "LRRC56",
    "ODAD3",
    "DNAAF1",
    "DNAAF6",
    "DNAAF4",
    "DNAH5",
    "DNAH9",
    "CFAP221",
    "RSPH9",
    "FOXJ1",
    "LRRC6",
    "GAS2L2",
    "DNAH1",
    "GAS8",
    "DNAI1",
    "STK36",
    "MCIDAS",
    "RSPH4A",
    "DNAAF3",
    "DNAJB13",
    "CCDC103",
    "NME8",
    "ZMYND10",
    "HYDIN",
    "DNAAF5",
    "CCDC40",
    "ODAD2",
    "DNAAF2",
    "IFT122",
    "INPP5E",
    "CFAP298",
    "DNAI2",
    "SPAG1",
    "SPEF2",
    "ODAD4",
    "DNAL1",
    "RSPH3",
    "OFD1",
    "CFAP300",
    "CCDC65",
    "DNAH11",
    "RSPH1",
    "DRC1",
    "ODAD1",
    ]


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    # configuration
    mount_point = os.getenv("GeneplexusFilesPath") # "/Users/billspat/tmp/geneplexus_data"
    if not mount_point:
        logging.error('GeneplexusFilesPath is not set')

        return func.HttpResponse(
            "GeneplexusFilesPath is not set",
            status_code=500
        )

    data_dir = "data_backend3"
    job_dir  = "jobs"

    # request params
    jobid = req.params.get('jobid')
    if not jobid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            jobid = req_body.get('jobid')
    
    if not jobid:
        logging.error('no jobid parameter passed')
        return func.HttpResponse(
        "Job id parameter required, aborting",
        status_code=400
    )

    #TODO  sanitize jobid
    output_path = os.path.join(mount_point, job_dir, jobid)

    if not os.path.exists(output_path):
        logging.error('invalid jobid param - job folder not found')
        return func.HttpResponse(
            "Invalid JobID",
            status_code=404
        )


    # check for support data needed
    data_path = os.path.join(mount_point, data_dir)

    if not os.path.exists(data_path):
        logging.error('data path does not exist')

        return func.HttpResponse(
            "Data not found",
            status_code=500
        )
 
    # dummy params
    net_type='STRING'
    features='Embedding'
    GSC='GO'

    try:   
        logging.info('starting gp model run')
        df_probs, df_GO, df_dis, avgps, df_edgelist, df_convert_out, positive_genes = run_model(data_path, input_genes, net_type, features, GSC)
        graph = make_graph(df_edgelist, df_probs)

    except Exception as e:
        err_msg = "run_model error: " + str(e)
        logging.error(err_msg)

        return func.HttpResponse(
                err_msg,
                status_code=500
            )
        print("job complete")
    try:
        input_count = df_convert_out.shape[0]
    except Exception as e:
        err_msg = "df_convert_out error: " + str(e)
        logging.error(err_msg)

        return func.HttpResponse(
                err_msg,
                status_code=500
            )
    try:
        print("saving output")
        job_info = save_output(output_path, jobid, net_type, features, GSC, avgps, input_count, positive_genes, df_probs, df_GO, df_dis, df_convert_out, graph, df_edgelist)
        logging.info("job completed and output saved")
        return func.HttpResponse(
                json.dumps(job_info),
                status_code=200
            )
    except Exception as e:
        err_msg = "saving model error: " + str(e) 
        logging.error(err_msg)
        return func.HttpResponse(
                err_msg,
                status_code=500
            )



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
def save_df_output(output_path, jobname, output_name, output_df):
    """ save data frames from model runs in a consistent way"""
    output_filename = construct_output_filename(jobname, output_name, '.tsv')
    output_filepath=construct_output_filepath(output_path, jobname, output_filename)
    output_df.to_csv(path_or_buf = output_filepath, sep = '\t', index = False, line_terminator = '\n')
    return(output_filename)

def save_graph_output(output_path, jobname, graph):
    """save the data that makes up the network graph to output folder, in JSON format.  
    the 'graph' is a dict of dicts (node, edges), so just save as json"""
    graph_file = construct_output_filename(jobname, 'graph', 'json')
    graph_file_path = construct_output_filepath(output_path, jobname, graph_file)
    with open(graph_file_path, 'w') as gf:
        json.dump(graph, gf)

    return(graph_file)

def save_output(output_path, jobname, net_type, features, GSC, avgps, input_count, positive_genes, 
    df_probs, df_GO, df_dis, df_convert_out_subset, graph, df_edgelist):

    # TODO : send outputs to save as a dictionary keyed on name.e.g. {'df_probs', df_probs, etc } 
    #        so this module can be more generic.   possibly also add format per item, or use same format for all (JSON or CSV)
    # save all data frames to files in standard format
    df_probs_file = save_df_output(output_path, jobname, 'df_probs', df_probs)
    df_GO_file = save_df_output(output_path, jobname, 'df_GO',df_GO )
    df_convert_out_subset_file = save_df_output(output_path, jobname, 'df_convert_out_subset', df_convert_out_subset)
    df_dis_file = save_df_output(output_path, jobname, 'df_dis',df_dis)
    df_edgelist_file = save_df_output(output_path, jobname, 'df_edgelist', df_edgelist )
    
    # the 'graph' is a dict of dicts (node, edges), so save in different format
    graph_file = save_graph_output(output_path, jobname, graph)

  

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
    
    job_info_path = construct_output_filepath(output_path, jobname, 'job_info', ext = 'json')
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

def construct_output_filepath(output_path, jobname, output_name, ext = ''):
    """ consistently create output file name from path and job name"""
    # note that when opening a new db files with shelve, it will automatically add .db, so don't add it here"
    if( ext and ext[0] != '.'):
        ext = '.' + ext

    # note this is not currenlty using the job name!  
    #  this is because for the job runner, the full output path for this one job is provided (with the jobname already in it)
    output_file_path = os.path.join(output_path, output_name +  ext)
    return(output_file_path)

