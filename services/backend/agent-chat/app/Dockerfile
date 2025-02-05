# FROM python:3.12
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Run app.py when the container launches
# CMD ["python", "app.py"]
CMD if [ "$DEBUG" = "true" ] ; \
    then \
        python wsgi.py ; \
    else \
        gunicorn -b 0.0.0.0:5005 wsgi:app ; \
    fi
