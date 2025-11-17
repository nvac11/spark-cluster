FROM apache/spark:3.5.1

USER root

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install pyspark + deps
RUN pip3 install pyspark pandas numpy

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy app
WORKDIR /app
COPY app.py /app/app.py

ENTRYPOINT ["/entrypoint.sh"]
