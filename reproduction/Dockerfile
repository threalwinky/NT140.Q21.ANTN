FROM python:3.11-slim

WORKDIR /app

COPY reproduction/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY reproduction/src/ ./reproduction/src/
COPY SISTAR/model/ ./SISTAR/model/
COPY datasets/cicids2017/ ./datasets/cicids2017/

CMD ["python", "reproduction/src/run_reproduction.py"]
