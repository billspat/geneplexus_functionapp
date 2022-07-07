# ProccessJob

import logging,os

import azure.functions as func
from ..utils import storage_helpers, processing
from .geneplexus_fn import run_job

def valid_job(jobid):
    #TODO put real code in gp module
    return True

def main(msg: func.QueueMessage) -> None:
    
    logging.info(f"job processor triggered")
    
    jobid = ""

    try:
        jobid = msg.get_body().decode('utf-8')

        logging.info(f"retrieved job from queue:  {jobid}")

        # Getting settings
        STORAGE_CONNECTION_STRING = os.getenv("QUEUECONNECTIONSTRING")
        STORAGE_CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME")
        TABLE_NAME = os.getenv("STORAGE_TABLE_NAME")
        JOBS_PATH = os.getenv("JOBS_PATH")
        DATA_PATH = os.getenv("DATA_PATH")

        # TODO replace with fn to check config
        if not JOBS_PATH:
            logging.error('JOBS_PATH is not set')
            return 

        if not os.path.exists(JOBS_PATH):
            logging.error('JOBS_PATH is not found')            
            return 

        if not DATA_PATH or not os.path.exists(DATA_PATH):
            err_msg = 'data path not found'
            logging.error(err_msg)
            return

        if jobid and valid_job(jobid):

            job_dir = os.path.join(JOBS_PATH, jobid)

            if not os.path.exists(job_dir):
                logging.error('invalid jobid param - job folder not found')
                storage_helpers.update_status(TABLE_NAME, jobid, '404', STORAGE_CONNECTION_STRING)
                return

            input_genes_file = os.path.join(job_dir, "input_genes.txt")

            if not os.path.exists(input_genes_file):
                err_msg = 'no input gene file in job folder'
                logging.error(err_msg)
                return
            else:
                logging.info("sending input genes file " + input_genes_file)
                
            storage_helpers.update_status(TABLE_NAME, jobid, 'running', STORAGE_CONNECTION_STRING)

            try:
                ### run 
                result = run_job(jobid, job_dir, DATA_PATH, input_genes_file, logging)
                if result:
                    logging.info(f"{jobid} complete")
                    storage_helpers.update_status(TABLE_NAME, jobid, 'complete', STORAGE_CONNECTION_STRING)
                else:
                    logging.info(f"{jobid} did not complete")
                    storage_helpers.update_status(TABLE_NAME, jobid, 'incomplete', STORAGE_CONNECTION_STRING)    
    
            except Exception as e:
                logging.info(f"{jobid} run error {e}")
                storage_helpers.update_status(TABLE_NAME, jobid, 'error', STORAGE_CONNECTION_STRING)

            # Saving processed file to storage
            # if processed_doc != None:
            #     # status processing
                
            #     new_file_name = f"{jobid}_output.txt"

            #     storage_helpers.upload_blob(STORAGE_CONTAINER_NAME, new_file_name, processed_doc, STORAGE_CONNECTION_STRING)
            #     # status done
            #     storage_helpers.update_status(TABLE_NAME, file_name, 'done', STORAGE_CONNECTION_STRING)
                
            
        
        else:
            logging.info(f"queue error: invalid or missing jobid: {jobid}")

    except Exception as e:
        logging.error(f"Queue Processor: error: {e}")