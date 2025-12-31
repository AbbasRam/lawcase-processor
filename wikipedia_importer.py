# #!/usr/bin/env python3
# """
# Wikipedia JSON to PostgreSQL Importer with Multiprocessing
# Processes Wikipedia JSON files from directories (AA, AB, AC, etc.) and inserts into database
# """

# import json
# import os
# import psycopg2
# import psycopg2.extras
# from multiprocessing import Pool, cpu_count
# import logging
# from pathlib import Path
# import sys
# from typing import List, Tuple

# # Database configuration
# DB_CONFIG = {
#     'host': 'database-1.c98m2g6e2a89.eu-central-1.rds.amazonaws.com',
#     'port': 5432,
#     'database': 'lawcase_search',
#     'user': 'postgres',
#     'password': '6d?q?$j3]vjg[t1li[sGKKQHYN[!'
# }

# # Setup logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# def get_db_connection():
#     """Create database connection"""
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         conn.autocommit = False
#         return conn
#     except Exception as e:
#         logger.error(f"Database connection failed: {e}")
#         return None

# def process_json_file(file_path: str) -> List[Tuple[str, str]]:
#     """Process a single JSON file with one JSON object per line"""
#     records = []
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 line = line.strip()
#                 if line:
#                     data = json.loads(line)
#                     title = data.get('title', '').strip()
#                     content = data.get('text', data.get('content', '')).strip()
#                     if title and content:
#                         records.append((title, content))
                
#     except Exception as e:
#         logger.error(f"Error processing file {file_path}: {e}")
    
#     return records

# def insert_batch_to_db(records: List[Tuple[str, str]], process_id: int):
#     """Insert a batch of records to database"""
#     if not records:
#         return 0
        
#     conn = get_db_connection()
#     if not conn:
#         return 0
        
#     try:
#         cursor = conn.cursor()
        
#         # Use execute_values for efficient batch insert
#         psycopg2.extras.execute_values(
#             cursor,
#             "INSERT INTO wiki_data (title, content) VALUES %s ON CONFLICT DO NOTHING",
#             records,
#             template=None,
#             page_size=1000
#         )
        
#         conn.commit()
#         inserted_count = cursor.rowcount
#         logger.info(f"Process {process_id}: Inserted {inserted_count} records")
        
#         cursor.close()
#         conn.close()
        
#         return inserted_count
        
#     except Exception as e:
#         logger.error(f"Process {process_id}: Database insert error: {e}")
#         if conn:
#             conn.rollback()
#             conn.close()
#         return 0

# def process_directory_worker(args: Tuple[str, str, int]) -> int:
#     """Worker function to process a directory of JSON files"""
#     directory_path, base_path, process_id = args
    
#     logger.info(f"Process {process_id}: Processing directory {directory_path}")
    
#     full_dir_path = os.path.join(base_path, directory_path)
#     if not os.path.exists(full_dir_path):
#         logger.warning(f"Process {process_id}: Directory {full_dir_path} not found")
#         return 0
    
#     all_records = []
#     file_count = 0
    
#     # List all files in directory for debugging
#     all_files = os.listdir(full_dir_path)
#     logger.info(f"Process {process_id}: Found {len(all_files)} files in {directory_path}")
    
#     # Process all files (not just .json)
#     for filename in all_files:
#         file_path = os.path.join(full_dir_path, filename)
#         if os.path.isfile(file_path):
#             try:
#                 records = process_json_file(file_path)
#                 all_records.extend(records)
#                 file_count += 1
                
#                 if file_count <= 3:  # Log first few files for debugging
#                     logger.info(f"Process {process_id}: Processed {filename}, got {len(records)} records")
                
#                 # Insert in batches to avoid memory issues
#                 if len(all_records) >= 5000:
#                     inserted = insert_batch_to_db(all_records, process_id)
#                     all_records = []
#             except Exception as e:
#                 logger.error(f"Process {process_id}: Error processing {filename}: {e}")
    
#     # Insert remaining records
#     if all_records:
#         inserted = insert_batch_to_db(all_records, process_id)
    
#     logger.info(f"Process {process_id}: Completed directory {directory_path} - {file_count} files processed")
#     return file_count

# def get_wikipedia_directories(base_path: str) -> List[str]:
#     """Get list of Wikipedia directories (AA, AB, AC, etc.)"""
#     directories = []
    
#     if not os.path.exists(base_path):
#         logger.error(f"Base path {base_path} does not exist")
#         return directories
    
#     for item in os.listdir(base_path):
#         item_path = os.path.join(base_path, item)
#         if os.path.isdir(item_path) and len(item) == 2 and item.isupper():
#             directories.append(item)
    
#     directories.sort()
#     logger.info(f"Found {len(directories)} Wikipedia directories: {directories}")
#     return directories

# def main():
#     """Main function to orchestrate the Wikipedia import process"""
#     if len(sys.argv) != 2:
#         print("Usage: python wikipedia_importer.py <path_to_wikipedia_directories>")
#         print("Example: python wikipedia_importer.py /path/to/wikipedia/extracted")
#         sys.exit(1)
    
#     base_path = sys.argv[1]
    
#     # Test database connection
#     logger.info("Testing database connection...")
#     conn = get_db_connection()
#     if not conn:
#         logger.error("Cannot connect to database. Please check your configuration.")
#         sys.exit(1)
#     conn.close()
#     logger.info("Database connection successful")
    
#     # Get Wikipedia directories
#     directories = get_wikipedia_directories(base_path)
#     if not directories:
#         logger.error("No Wikipedia directories found")
#         sys.exit(1)
    
#     # Prepare arguments for multiprocessing
#     num_processes = min(cpu_count(), len(directories))
#     logger.info(f"Using {num_processes} processes for {len(directories)} directories")
    
#     # Create arguments for worker processes
#     worker_args = [(dir_name, base_path, i) for i, dir_name in enumerate(directories)]
    
#     # Process directories using multiprocessing
#     try:
#         with Pool(processes=num_processes) as pool:
#             results = pool.map(process_directory_worker, worker_args)
        
#         total_files = sum(results)
#         logger.info(f"Import completed! Processed {total_files} files from {len(directories)} directories")
        
#     except KeyboardInterrupt:
#         logger.info("Import interrupted by user")
#     except Exception as e:
#         logger.error(f"Import failed: {e}")

# if __name__ == "__main__":
#     main()