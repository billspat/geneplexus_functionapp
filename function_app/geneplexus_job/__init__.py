import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    jobid = req.params.get('jobid')
    if not jobid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            jobid = req_body.get('jobid')

    if jobid:
        return func.HttpResponse(
            f" This would have run the GenePlexus ML for job id '{jobid}'", 
            status_code=200
            )
    else:
        return func.HttpResponse(
             "This would have run the GenePlexus ML. Pass a jobid in the query string or in the request body to use it",
             status_code=200
        )
