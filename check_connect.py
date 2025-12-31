import boto3
import json
import psycopg2
from botocore.exceptions import ClientError

def get_secret(secret_name="rds!db-0140678e-d357-4cd3-ae5e-0ab28a111aee", region_name="eu-central-1"):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        raise e

    # Secrets Manager can return SecretString or SecretBinary
    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)  # Assuming the secret is JSON
    else:
        raise ValueError("Secret format not supported (expected SecretString with JSON)")

def test_db_connection():
    # Update your secret name here if different
    secret_name = "rds!db-0140678e-d357-4cd3-ae5e-0ab28a111aee"  # <-- Change if your secret has a different name
    region_name = "eu-central-1"

    try:
        # Retrieve credentials from Secrets Manager
        secret_dict = get_secret(secret_name, region_name)
        print("Secret successfully retrieved.", secret_dict)
        
        # Expected keys in the secret JSON
        host = secret_dict.get('host', 'database-1.c98m2g6e2a89.eu-central-1.rds.amazonaws.com')  # fallback to your endpoint
        port = secret_dict.get('port', 5432)
        dbname = 'lawcase_search'  # some secrets use 'database'
        username = secret_dict.get('username')
        password = secret_dict.get('password')

        if not all([host, dbname, username, password]):
            print("Missing required fields in secret (need: host, dbname/database, username, password)")
            return False

        print(f"Attempting to connect to PostgreSQL...")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Database: {dbname}")
        print(f"User: {username}")

        # Establish connection
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=username,
            password=password,
            connect_timeout=10,
            sslmode='require'  # RDS usually requires SSL
        )

        # Test the connection with a simple query
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print("Connection successful!")
        print(f"PostgreSQL version: {db_version[0]}")

        # Clean up
        cur.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        print("Connection failed (OperationalError):")
        print(e)
        return False
    except Exception as e:
        print("Unexpected error:")
        print(e)
        return False

# Run the test
if __name__ == "__main__":
    test_db_connection()