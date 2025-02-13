# Use an official Python image as base
FROM python:3.11

# Install dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./main.py /app/ \
     ./gvars.py /app/ \
     ./embedding.py /app/ \
     ./vectorindex.py /app/ \
     ./etl/extract.py /app/etl/ \
     ./etl/reader.py /app/etl/ \
     ./etl/transform_content.py /app/etl/ \
     ./etl/utils.py /app/etl/

# Run the application (adjust accordingly)
CMD ["python", "main.py"]
