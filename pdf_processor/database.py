import psycopg2
from pdf_processor.config import settings
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Generator to get a database connection."""
    conn = None
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        yield conn
    finally:
        if conn:
            conn.close()

def save_to_db(target_table: str, item_id: int, decision_id: str, plaintext: str):
    """Saves the extracted text to the target table."""
    # Use ON CONFLICT to handle cases where the record already exists
    sql = f"""
        INSERT INTO {target_table} (id, decision_id, pdf_plaintext)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
        decision_id = EXCLUDED.decision_id,
        pdf_plaintext = EXCLUDED.pdf_plaintext;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (item_id, decision_id, plaintext))
            conn.commit()
