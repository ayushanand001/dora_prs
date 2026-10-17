FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py dora_metrics.py generate_mock_data.py ./
COPY data/ ./data/
EXPOSE 8501
# Streamlit health endpoint used by K8s probes
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
