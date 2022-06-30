import logging
import time


def get_doc_content(path):
    with open(path, 'r') as f:
        content = f.read()    
    return content

def process_doc(path):
    try:
        content = get_doc_content(path)
        new_content = content[::-1]
        logging.info(f"Processed {path} with content:\n{new_content}")
        logging.info(f"processing of {path}, sleeping...")
        time.sleep(15)

        return new_content
    except Exception as e:
        logging.error(f"Error processing document.")
    return None