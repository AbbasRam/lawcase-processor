# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for PyMuPDF (fitz)
# This is important for handling various image formats within PDFs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY ./pdf_processor/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY ./pdf_processor /app/pdf_processor

# The command to run the API will be specified in docker-compose.yml
# The command to run the Celery worker will be specified in docker-compose.yml

