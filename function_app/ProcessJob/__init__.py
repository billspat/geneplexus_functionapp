# ProccessJob

import logging,os

import azure.functions as func
from ..utils import storage_helpers, processing

def old_main(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))


    file_name = msg.get_body().decode('utf-8')
    logging.info(f"Processing queue item: {file_name}…") 
    STORAGE_CONNECTION_STRING = os.getenv("QUEUECONNECTIONSTRING")
    STORAGE_CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME")
    
    file_path = storage_helpers.download_blob(STORAGE_CONTAINER_NAME, file_name, STORAGE_CONNECTION_STRING)

    processing.process_doc(file_path)


def main(msg: func.QueueMessage) -> None:
    
    logging.info(f"job processor triggered")
    
    file_name = ""

    try:

        file_name = msg.get_body().decode('utf-8')
        logging.info(f"Queue Processor:  {file_name}")

        # Getting settings
        STORAGE_CONNECTION_STRING = os.getenv("QUEUECONNECTIONSTRING")
        STORAGE_CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME")
        TABLE_NAME = os.getenv("STORAGE_TABLE_NAME")

        storage_helpers.update_status(TABLE_NAME, file_name, 'new', STORAGE_CONNECTION_STRING)

        # Getting file from storage
        file_path = storage_helpers.download_blob(STORAGE_CONTAINER_NAME, file_name, STORAGE_CONNECTION_STRING)

        if file_path != None:
            # Processing file
            processed_doc = processing.process_doc(file_path)
            # Saving processed file to storage
            if processed_doc != None:
                # status processing
                storage_helpers.update_status(TABLE_NAME, file_name, 'processing', STORAGE_CONNECTION_STRING)
                new_file_name = 'processed_' + file_name
                storage_helpers.upload_blob(STORAGE_CONTAINER_NAME, new_file_name, processed_doc, STORAGE_CONNECTION_STRING)
                # status done
                storage_helpers.update_status(TABLE_NAME, file_name, 'done', STORAGE_CONNECTION_STRING)
                # Deleting local copy
                os.remove(file_path)
                logging.info(f"Done processing {file_name}.")
        
        else:
            logging.info(f"Queue Processor: error during processing")

    except Exception as e:
        logging.error(f"Queue Processor: error getting file name from msg: {e}")