from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

from pdf_processor.tasks import process_pdf_task
from pdf_processor.database import get_db_connection

app = FastAPI()

class ProcessRequest(BaseModel):
    start_id: int
    end_id: int
    source_table: str
    target_table: str

@app.post("/process-pdfs/")
def process_pdfs(request: ProcessRequest, background_tasks: BackgroundTasks):
    """
    API endpoint to start the PDF processing job.
    It fetches records from the database and creates a Celery task for each.
    """
    query = f"""
        SELECT id, decision_id, court_act_pdf_url
        FROM {request.source_table}
        WHERE id BETWEEN %s AND %s;
    """
    
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (request.start_id, request.end_id))
                records = cur.fetchall()
    except (psycopg2.Error, Exception) as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not records:
        raise HTTPException(status_code=404, detail="No records found in the given range.")

    tasks_dispatched = 0
    for record in records:
        if record.get("court_act_pdf_url"):
            # Dispatch the task to Celery
            process_pdf_task.delay(
                target_table=request.target_table,
                item_id=record['id'],
                decision_id=record['decision_id'],
                pdf_url=record['court_act_pdf_url']
            )
            tasks_dispatched += 1

    return {
        "message": f"PDF processing started for records between {request.start_id} and {request.end_id}.",
        "total_records_found": len(records),
        "tasks_dispatched": tasks_dispatched
    }

@app.get("/")
def read_root():
    return {"message": "PDF Processor API is running."}
