

import logging
import azure.functions as func


### original template function
# def main(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     name = req.params.get('name')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('name')

#     if name:
#         return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
#     else:
#         return func.HttpResponse(
#              "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
#              status_code=200
#         )


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

        try:
            msg.set(document_list)
            return func.HttpResponse(
                "Processing started.",
                status_code=200
            )

        except Exception as e:
            return func.HttpResponse(
                f"Error: {e}",
                status_code=500
            )
