FROM python:3.13-slim

WORKDIR /app

COPY src/ ./src/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "src/Puente.py" ]