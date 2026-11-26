FROM apache/airflow:2.10.4-python3.11

COPY Requirements.txt /tmp/Requirements.txt
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.4/constraints-3.11.txt" \
    -r /tmp/Requirements.txt