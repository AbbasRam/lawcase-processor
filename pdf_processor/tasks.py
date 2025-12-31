import requests
import fitz  # PyMuPDF
from celery.utils.log import get_task_logger
from pdf_processor.celery_app import celery_app
from pdf_processor.database import save_to_db, get_db_connection

logger = get_task_logger(__name__)

@celery_app.task(bind=True, autoretry_for=(requests.exceptions.RequestException,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def process_pdf_task(self, target_table: str, item_id: int, decision_id: str, pdf_url: str):
    """
    Celery task to download a PDF, convert it to text, and save it to the database.
    """
    logger.info(f"Processing item_id: {item_id} with URL: {pdf_url}")

    try:
        # 1. Fetch the PDF
        response = requests.get(pdf_url, timeout=60)
        response.raise_for_status()

        # 2. Convert PDF to plaintext
        plaintext = ""
        with fitz.open(stream=response.content, filetype="pdf") as doc:
            for page in doc:
                plaintext += page.get_text()

        if not plaintext.strip():
            logger.warning(f"No text extracted from PDF for item_id: {item_id}")
            return f"No text extracted for item_id: {item_id}"

        # 3. Save to the new composite table
        save_to_db(target_table, item_id, decision_id, plaintext)
        logger.info(f"Successfully processed and saved item_id: {item_id}")
        return f"Successfully processed item_id: {item_id}"

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error downloading {pdf_url} for item_id {item_id}: {e}")
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(f"Failed to process PDF for item_id {item_id}. Error: {e}", exc_info=True)
        # We don't retry on non-network errors to avoid poison pills.
        return f"Failed to process item_id: {item_id}, Error: {str(e)}"
