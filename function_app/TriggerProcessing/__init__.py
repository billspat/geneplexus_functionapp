
#triggerprocessing: take input from http and enqueue items in a list, triggering the processing of those items
# TODO: rename to enqueue_job since it does't trigger anything, it just puts it on the queue.  

import logging
import azure.functions as func

# queue processing version, gets a list of documents to process
def main(req: func.HttpRequest, msg: func.Out[func.QueueMessage]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # documentList param is either a single element or an array msg.set(["Element1", "Element2", ...])
    try:
        req_body = req.get_json()
        document_list = req_body.get('documentList')
    except ValueError:
        return func.HttpResponse(
             "Please pass a documentList parameter in the request body",
             status_code=400
        )
    
    if document_list:

        logging.info(f"enqueuing {document_list}.")
        
        try:
            
            msg.set(document_list)
            logging.info(f"msg queueed {document_list}.")
            return func.HttpResponse(
                "Processing started.",
                status_code=200
            )

        except Exception as e:
            logging.info(f"error when enqueuing {document_list}.")
            return func.HttpResponse(
                f"Error: {e}",
                status_code=500
            )
