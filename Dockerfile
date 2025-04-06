FROM python:3.11-slim

WORKDIR /app

COPY .env .env
COPY . .


RUN pip install requests
RUN pip install python-dotenv
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "pogoda.py"]
