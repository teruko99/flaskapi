import json
import requests
import xml.etree.ElementTree as ET
import yaml
from datetime import datetime
from elasticsearch import Elasticsearch
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from pymongo import MongoClient
from unidecode import unidecode
from yaml.loader import SafeLoader

app = Flask(__name__)
CORS(app)

#client = MongoClient('mongodb://cool-rats-stay-189-62-149-27.loca.lt/')
client = MongoClient('192.168.0.6', 27017)
#client = MongoClient('localhost', 27017)
db = client['mydb']
users_collection = db['users']

# Substituir por uma chave secreta segura
app.config['JWT_SECRET_KEY'] = 'super-secret-key' 
jwt = JWTManager(app)

# Configuração da documentação Swagger
SWAGGER_URL = '/docs'  # URL da documentação Swagger
API_URL = '/swagger.json'  # URL da API
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Minha API Flask'  # Nome da sua API
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

#Configuração do Elasticsearch
ELASTIC_PASSWORD = "URbZv2cnylz1vOvjqU=j"
es = Elasticsearch(
    "https://localhost:9200",
    ca_certs="C:/elk/elasticsearch-8.6.2/config/certs/http_ca.crt",
    basic_auth=("elastic", ELASTIC_PASSWORD)
)

@app.before_request
def log_request():
    start_time = datetime.now()
    log_data = {
        "timestamp": start_time.isoformat(),
        "request": {
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            #"body": request.get_data(),
        },
    }
    es.index(index="logs", document=log_data)

@app.after_request
def log_response(response):
    end_time = datetime.now()
    log_data = {
        "timestamp": end_time.isoformat(),
        "response": {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            #"body": response.get_data(),
        },
        "duration": (end_time - end_time).total_seconds(),
    }
    es.index(index="logs", document=log_data)
    return response

@app.route('/')
def index():
    return jsonify({'message': 'Bem-vindo à minha API!'})

@app.route('/jokes', methods=['GET'])
def get_jokes():
    # Integração com a API de piadas
    response = requests.get('https://official-joke-api.appspot.com/random_ten')
    jokes = response.json()
    # Integração com a API de gatos
    response = requests.get('https://api.thecatapi.com/v1/images/search')
    cat = response.json()[0]['url']
    # Cria um dicionário com as piadas e a imagem de gato
    data = {'jokes': jokes, 'cat': cat}
    # Retorna os dados em formato JSON
    return jsonify(data)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    password = data['password']
    # Verifica se o usuário já existe no banco de dados
    if users_collection.find_one({'username': username}):
        return jsonify({'message': 'Usuário já existe!'}), 400
    # Insere o novo usuário no banco de dados
    user_id = users_collection.insert_one({'username': username, 'password': password}).inserted_id
    return jsonify({'message': f'Usuário criado com sucesso! ID: {user_id}'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    # Verifica se o usuário e a senha são válidos e crie um access token
    if users_collection.find_one({'username': username,'password': password}):
        access_token = create_access_token(identity='username')
        return jsonify({'access_token': access_token}), 201
    else:
        return jsonify({'message': 'Acesso negado!'}), 400

@app.route('/endereco', methods=['POST'])
def endereco():
    cep = request.json.get('cep')
    if not cep:
        return jsonify({'error': 'CEP não informado'})
    # Consulta a API ViaCEP para obter o endereço e a cidade
    url = f'https://viacep.com.br/ws/{cep}/json/'
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Erro ao consultar ViaCEP'})
    via_cep = response.json()
    cidade = unidecode(via_cep['localidade'].lower())
    # Busca o código da cidade na API do INPE
    response = requests.get(f'http://servicos.cptec.inpe.br/XML/listaCidades?city={cidade}')
    if response.status_code != 200:
        return jsonify({'error': 'Erro ao consultar INPE'})
    roota = ET.fromstring(response.content)
    codigo = roota[0][2].text
    # Obtém as informações da previsão do tempo dos 4 dias
    response = requests.get(f'http://servicos.cptec.inpe.br/XML/cidade/{codigo}/previsao.xml')
    if response.status_code != 200:
        return jsonify({'error': 'Erro ao consultar INPE'})
    rootb = ET.fromstring(response.content)
    previsao = []
    for dia in rootb.findall('.//previsao'):
        previsao.append({
            'dia': dia.find('dia').text,
            'tempo': dia.find('tempo').text,
            'maxima': dia.find('maxima').text,
            'minima': dia.find('minima').text,
            'iuv': dia.find('iuv').text
        })
    log = {'cep': cep, 'usuario': 'nezuko'}
    res = es.index(index='logs', document=log)
    #resultado do elastic
    #return res['result']
    # Combina as informações da ViaCEP e do INPE e retorne em JSON
    return jsonify({
        'cep': via_cep['cep'],
        'logradouro': via_cep['logradouro'],
        'complemento': via_cep['complemento'],
        'bairro': via_cep['bairro'],
        'localidade': via_cep['localidade'],
        'uf': via_cep['uf'],
        'ibge': via_cep['ibge'],
        'gia': via_cep['gia'],
        'ddd': via_cep['ddd'],
        'siafi': via_cep['siafi'],
        'previsao': previsao
    })

@app.route('/logs', methods=['POST'])
def get_logs():
    token = request.json.get('token')
    if not token:
        return {'error': 'Token de acesso não informado'}
    res = es.search(index='logs', query={'match_all': {}})
    logs = [hit['_source'] for hit in res['hits']['hits']]
    return {'logs': logs}

@app.route('/swagger.json')
def get_swagger():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Nome da sua API"
    with open('swagger.yaml', 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data
    #return jsonify(swag)

if __name__ == '__main__':
    app.run(debug=True)