FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
