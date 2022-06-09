from ast import Str
import logging
import os, json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    job_info= {}
    
    job_info['data_path'] = data_path = "/geneplexus_files"
    if os.path.exists(data_path):
        job_info['data_pata_exists'] = True
        job_info['data_path_files'] = os.listdir(data_path)
    else:
        job_info['data_pata_exists'] = False
    
    job_info['rootdir'] = os.listdir("/")
    job_info['cwd'] = os.getcwd()
    job_info['cwd_files'] = os.listdir(job_info['cwd'])

    
    jobid = req.params.get('jobid')
    if not jobid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            jobid = req_body.get('jobid')
    
    if jobid:
        job_info['jobid'] = jobid
       
    return func.HttpResponse(
        json.dumps(job_info),
        status_code=200
    )
