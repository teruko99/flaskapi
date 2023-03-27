# Dockerfile
FROM python:3.9-slim-buster
# atualiza o sistema e instala as dependências
RUN apt-get update && apt-get -y upgrade && apt-get -y install wget gnupg2 && \
    wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add - && \
    echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list && \
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - && \
    echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list && \
    apt-get update && \
    apt-get -y install mongodb-org elasticsearch && \
    pip install flask pymongo elasticsearch
# cria diretórios para os dados do MongoDB e Elasticsearch
RUN mkdir -p /data/db && \
    mkdir -p /usr/share/elasticsearch/data && \
    chown -R elasticsearch:elasticsearch /usr/share/elasticsearch
ENV MONGO_URI mongodb://mongodb:27017
ENV ELASTICSEARCH_URL http://elasticsearch:9200
# copia o código da API Flask
COPY . /app
WORKDIR /app
COPY requirements.txt .
COPY app.py .
# Instale as dependências Python
RUN pip install -r requirements.txt
# expõe as portas para a API Flask, MongoDB e Elasticsearch
EXPOSE 5000
EXPOSE 27017
EXPOSE 9200
# inicia os serviços do MongoDB e Elasticsearch
CMD service mongod start && service elasticsearch start && python3 app.py