FROM python:3.10-slim

WORKDIR /app

COPY app.py .
COPY templates templates
COPY requirements.txt .

RUN pip install -r requirements.txt

# Log files will be mounted from host
VOLUME /logs

EXPOSE 9090

CMD ["python", "app.py"]
