from elasticsearch import Elasticsearch
from pymongo import MongoClient

import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#client = MongoClient('mongodb://cool-rats-stay-189-62-149-27.loca.lt/')
client = MongoClient('192.168.0.6', 27017)
#client = MongoClient('localhost', 27017)
db = client['mydb']
users_collection = db['users']

#Configuração do Elasticsearch
#ELASTIC_PASSWORD = "URbZv2cnylz1vOvjqU=j"
es = Elasticsearch(
    #"https://localhost:9200",
    "http://192.168.0.6:9200"
    #request_timeout=30
    #ca_certs="C:/elk/elasticsearch-8.6.2/config/certs/http_ca.crt",
    #basic_auth=("elastic", ELASTIC_PASSWORD)
)

@app.route('/')
def index():
    return jsonify({'message': 'Bem-vindo à minha API!'})

@app.route('/jokes', methods=['GET'])
def get_jokes():
    response = requests.get('https://official-joke-api.appspot.com/random_ten')
    jokes = response.json()
    response = requests.get('https://api.thecatapi.com/v1/images/search')
    cat = response.json()[0]['url']
    # Cria um dicionário com as piadas e a imagem de gato
    data = {'jokes': jokes, 'cat': cat}
    return jsonify(data)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if users_collection.find_one({'username': username}):
        return jsonify({'message': 'Usuário já existe!'}), 400
    user_id = users_collection.insert_one({'username': username, 'password': password}).inserted_id
    return jsonify({'message': f'Usuário criado com sucesso! ID: {user_id}'}), 201

@app.route('/logs', methods=['POST'])
def get_logs():

if __name__ == '__main__':
    app.run(debug=True)