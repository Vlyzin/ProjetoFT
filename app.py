import math
import openrouteservice
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import json
import os

app = Flask(__name__)
CORS(app)

#Configuração do OpenRouteService, Utilize sua própria chave de API
# Você pode obter uma chave gratuita em https://openrouteservice.org/sign-up/
ORS_API_KEY = '' # Insira sua chave aqui
ors_client = openrouteservice.Client(key=ORS_API_KEY)

#Dicionário com as coordenadas centrais de cada estado
ESTADOS_CENTROS = {
    'Acre': (-67.82441, -9.97499),
    'Alagoas': (-35.7350, -9.66599),
    'Amapá': (-51.06664, 0.0395),
    'Amazonas': (-60.0261, -3.1019),
    'Bahia': (-38.5014, -12.9714),
    'Ceará': (-38.5434, -3.71722),
    'Distrito Federal': (-47.8828, -15.7939),
    'Espírito Santo': (-40.3377, -20.3297),
    'Goiás': (-49.2643, -16.6867),
    'Maranhão': (-44.3068, -2.5307),
    'Mato Grosso': (-56.0949, -15.5963),
    'Mato Grosso do Sul': (-54.6291, -20.4486),
    'Minas Gerais': (-43.9352, -19.9239),
    'Pará': (-48.5039, -1.4558),
    'Paraíba': (-34.8631, -7.1153),
    'Paraná': (-49.2733, -25.4284),
    'Pernambuco': (-34.8770, -8.0476),
    'Piauí': (-42.8034, -5.0919),
    'Rio de Janeiro': (-43.1964, -22.9083),
    'Rio Grande do Norte': (-35.2088, -5.7950),
    'Rio Grande do Sul': (-51.2177, -30.0346),
    'Rondônia': (-63.8999, -8.7608),
    'Roraima': (-60.6730, 2.8196),
    'Santa Catarina': (-48.5586, -27.5936),
    'São Paulo': (-46.6339, -23.5505),
    'Sergipe': (-37.0731, -10.9472),
    'Tocantins': (-48.3336, -10.1846)
}

JSON_FOLDER = 'json'
VEICULOS_FILE = os.path.join(JSON_FOLDER, 'veiculos.json')
LOCAIS_FILE = os.path.join(JSON_FOLDER, 'locais.json')
MOTORISTAS_FILE = os.path.join(JSON_FOLDER, 'motoristas.json')

def carregar_dados(arquivo):
    """Carrega dados de um arquivo JSON. Se o arquivo não existir, retorna uma lista vazia."""
    if os.path.exists(arquivo):
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_dados(arquivo, dados):
    """Salva dados em um arquivo JSON."""
    os.makedirs(JSON_FOLDER, exist_ok=True) # Garante que a pasta 'json' exista
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Carrega os dados na inicialização do servidor
veiculos = carregar_dados(VEICULOS_FILE)
locais = carregar_dados(LOCAIS_FILE)
motoristas = carregar_dados(MOTORISTAS_FILE)

# Lógica para o ID não começar do 1 sempre
if veiculos or locais or motoristas:
    max_id = 0
    todos_os_itens = veiculos + locais + motoristas
    if todos_os_itens:
        max_id = max(item.get('id', 0) for item in todos_os_itens)
    id_counter = max_id + 1
else:
    id_counter = 1

viagem_ativa = {}

#ROTAS PARA RENDERIZAR PÁGINAS
@app.route('/')
def index():
    return render_template('index.html', active_page='home')

@app.route('/criar-viagem')
def criar_viagem_page():
    return render_template('criar_viagem.html', active_page='criar_viagem')

@app.route('/criar-veiculo')
def criar_veiculo_page():
    return render_template('criar_veiculo.html', active_page='criar_veiculo')

@app.route('/criar-local')
def criar_local_page():
    return render_template('criar_local.html', active_page='criar_local')

@app.route('/criar-motorista')
def criar_motorista_page():
    return render_template('criar_motorista.html', active_page='criar_motorista')

#API ENDPOINTS
@app.route('/api/veiculos', methods=['POST', 'GET'])
def handle_veiculos():
    global id_counter
    if request.method == 'POST':
        dados = request.json
        if any(v['placa'].lower() == dados['placa'].lower() for v in veiculos):
            return jsonify({'status': 'erro', 'mensagem': f"Placa '{dados['placa']}' já cadastrada."}), 409
        
        novo_veiculo = {'id': id_counter, 'placa': dados['placa'], 'modelo': dados['modelo']}
        veiculos.append(novo_veiculo)
        salvar_dados(VEICULOS_FILE, veiculos) # Salva no arquivo
        id_counter += 1
        return jsonify({'status': 'sucesso', 'veiculo': novo_veiculo}), 201
    return jsonify(veiculos)


@app.route('/api/locais', methods=['POST', 'GET'])
def handle_locais():
    global id_counter
    if request.method == 'POST':
        dados = request.json
        if any(l['nome'].lower() == dados['nome'].lower() for l in locais):
            return jsonify({'status': 'erro', 'mensagem': f"Local '{dados['nome']}' já cadastrado."}), 409

        novo_local = {
            'id': id_counter, 'nome': dados['nome'], 'tipo': dados['tipo'],
            'cidade': dados['cidade'], 'estado': dados['estado'],
            'lat': float(dados['lat']), 'lon': float(dados['lon'])
        }
        locais.append(novo_local)
        salvar_dados(LOCAIS_FILE, locais) # Salva no arquivo
        id_counter += 1
        return jsonify({'status': 'sucesso', 'local': novo_local}), 201
    return jsonify(locais)

@app.route('/api/motoristas', methods=['POST', 'GET'])
def handle_motoristas():
    global id_counter
    if request.method == 'POST':
        dados = request.json
        if any(m['cpf'] == dados['cpf'] for m in motoristas):
            return jsonify({'status': 'erro', 'mensagem': f"CPF '{dados['cpf']}' já cadastrado."}), 409
            
        novo_motorista = { 'id': id_counter, 'nome': dados['nome'], 'cpf': dados['cpf'], 'sexo': dados['sexo'] }
        motoristas.append(novo_motorista)
        salvar_dados(MOTORISTAS_FILE, motoristas) # Salva no arquivo
        id_counter += 1
        return jsonify({'status': 'sucesso', 'motorista': novo_motorista}), 201
    return jsonify(motoristas)

@app.route('/api/viagens', methods=['POST'])
def create_viagem():
    global viagem_ativa
    if viagem_ativa: return jsonify({'status': 'erro', 'mensagem': 'Já existe uma viagem em andamento.'}), 400
    
    try:
        dados = request.json
        if not all(k in dados and dados[k] for k in ['veiculo_id', 'origem_id', 'destino_id', 'motorista_id']):
             return jsonify({'status': 'erro', 'mensagem': 'Todos os campos são obrigatórios.'}), 400

        veiculo = next((v for v in veiculos if v['id'] == int(dados['veiculo_id'])), None)
        origem = next((l for l in locais if l['id'] == int(dados['origem_id'])), None)
        destino = next((l for l in locais if l['id'] == int(dados['destino_id'])), None)
        motorista = next((m for m in motoristas if m['id'] == int(dados['motorista_id'])), None)
        if not all([veiculo, origem, destino, motorista]): return jsonify({'status': 'erro', 'mensagem': 'Um dos IDs fornecidos não foi encontrado.'}), 404

        estado_origem = origem.get('estado', 'São Paulo')
        ponto_partida_coords = ESTADOS_CENTROS.get(estado_origem, ESTADOS_CENTROS['São Paulo'])
        
        coords_estagio_1 = (ponto_partida_coords, (origem['lon'], origem['lat']))
        
        routes = ors_client.directions(coordinates=coords_estagio_1, profile='driving-hgv', format='geojson')
        route_coordinates_s1 = routes['features'][0]['geometry']['coordinates']

    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': 'Não foi possível calcular a rota inicial.'}), 500

    viagem_ativa = {
        'veiculo': veiculo, 'origem': origem, 'destino': destino, 'motorista': motorista, 
        'status': 'A CAMINHO DA ORIGEM',
        'ponto_partida': {'lat': ponto_partida_coords[1], 'lon': ponto_partida_coords[0]},
        'start_time': datetime.now(timezone.utc),
        'stage2_start_time': None,
        'finalizado': False,
        'stage': 'to_origin',
        'route_stage1': route_coordinates_s1,
        'route_stage2': None,
        'pontos_percorridos': []
    }
    return jsonify({'status': 'sucesso'}), 201


@app.route('/api/viagens/ativa', methods=['GET'])
def get_viagem_ativa():
    if not viagem_ativa: 
        return jsonify({})
    
    pontos_percorridos = []
    
    # Constantes da simulação
    intervalo_tick_segundos = 5
    pontos_por_tick = 48
    
    # --- Reconstrói o histórico do Estágio 1 ---
    # Define o tempo final do estágio 1: ou é agora, ou foi quando o estágio 2 começou
    end_time_s1 = viagem_ativa.get('stage2_start_time') or datetime.now(timezone.utc)
    tempo_decorrido_s1 = (end_time_s1 - viagem_ativa['start_time']).total_seconds()
    ticks_passados_s1 = int(tempo_decorrido_s1 / intervalo_tick_segundos)
    
    rota_s1 = viagem_ativa['route_stage1']
    for i in range(ticks_passados_s1 + 1):
        index = min(i * pontos_por_tick, len(rota_s1) - 1)
        ponto = rota_s1[index]
        # Adiciona apenas se for um novo ponto para evitar duplicatas
        if not pontos_percorridos or pontos_percorridos[-1] != ponto:
            pontos_percorridos.append(ponto)
        if index == len(rota_s1) - 1: break

    # --- Reconstrói o histórico do Estágio 2 (se já começou) ---
    if viagem_ativa.get('stage2_start_time') and viagem_ativa.get('route_stage2'):
        tempo_decorrido_s2 = (datetime.now(timezone.utc) - viagem_ativa['stage2_start_time']).total_seconds()
        ticks_passados_s2 = int(tempo_decorrido_s2 / intervalo_tick_segundos)
        rota_s2 = viagem_ativa['route_stage2']
        for i in range(ticks_passados_s2 + 1):
            index = min(i * pontos_por_tick, len(rota_s2) - 1)
            ponto = rota_s2[index]
            if not pontos_percorridos or pontos_percorridos[-1] != ponto:
                pontos_percorridos.append(ponto)
            if index == len(rota_s2) - 1: break
    
    dados_iniciais = {
        'veiculo': viagem_ativa['veiculo'], 'origem': viagem_ativa['origem'], 'destino': viagem_ativa['destino'],
        'motorista': viagem_ativa['motorista'], 'status': viagem_ativa['status'], 
        'ponto_partida': viagem_ativa['ponto_partida'],
        'pontos_percorridos': pontos_percorridos
    }
    return jsonify(dados_iniciais)

@app.route('/api/viagens/tick', methods=['GET'])
def tick_viagem():
    if not viagem_ativa or viagem_ativa.get('finalizado', False): return jsonify({'status': 'sem_viagem'})

    intervalo_tick_segundos, pontos_por_tick = 5, 50
    status_atual = viagem_ativa['status']
    novo_status = status_atual

    # Define qual rota e tempo inicial usar com base no estágio atual
    if viagem_ativa['stage'] == 'to_origin':
        rota_atual = viagem_ativa['route_stage1']
        tempo_inicial = viagem_ativa['start_time']
    else: # to_destination
        rota_atual = viagem_ativa['route_stage2']
        tempo_inicial = viagem_ativa['stage2_start_time']

    # Se a rota do estágio atual ainda não foi calculada, retorna a última posição conhecida
    if not rota_atual:
        # Pega a última posição do estágio anterior para não dar erro
        lon, lat = viagem_ativa['route_stage1'][-1]
        return jsonify({'lat': lat, 'lon': lon, 'status': status_atual, 'finalizado': False})

    # Calcula o índice na rota baseado no tempo decorrido
    tempo_decorrido = (datetime.now(timezone.utc) - tempo_inicial).total_seconds()
    tick_atual = int(tempo_decorrido / intervalo_tick_segundos)
    simulation_index = min(tick_atual * pontos_por_tick, len(rota_atual) - 1)
    
    lon, lat = rota_atual[simulation_index]
    
    def haversine_distance(lon1, lat1, lon2, lat2):
        R, phi1, phi2 = 6371000, math.radians(lat1), math.radians(lat2)
        d_phi, d_lambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Lógica de mudança de status e estágio
    if viagem_ativa['stage'] == 'to_origin':
        dist_origem = haversine_distance(lon, lat, viagem_ativa['origem']['lon'], viagem_ativa['origem']['lat'])
        if dist_origem <= 500:
            novo_status = 'NA ORIGEM'
            viagem_ativa['stage'] = 'to_destination'
            viagem_ativa['stage2_start_time'] = datetime.now(timezone.utc)
            
            origem_coords = (viagem_ativa['origem']['lon'], viagem_ativa['origem']['lat'])
            destino_coords = (viagem_ativa['destino']['lon'], viagem_ativa['destino']['lat'])
            try:
                # ATUALIZADO: Salva a nova rota na chave correta 'route_stage2'
                routes = ors_client.directions(coordinates=(origem_coords, destino_coords), profile='driving-hgv', format='geojson')
                viagem_ativa['route_stage2'] = routes['features'][0]['geometry']['coordinates']
            except Exception as e:
                viagem_ativa['finalizado'] = True

    elif viagem_ativa['stage'] == 'to_destination':
        dist_origem = haversine_distance(lon, lat, viagem_ativa['origem']['lon'], viagem_ativa['origem']['lat'])
        dist_destino = haversine_distance(lon, lat, viagem_ativa['destino']['lon'], viagem_ativa['destino']['lat'])
        if status_atual == 'NA ORIGEM' and dist_origem > 500: novo_status = 'EM TRÂNSITO'
        elif status_atual == 'EM TRÂNSITO' and dist_destino <= 500: novo_status = 'NO DESTINO'

    viagem_ativa['status'] = novo_status
    
    if novo_status == 'NO DESTINO' and simulation_index >= len(rota_atual) - 1:
        viagem_ativa['finalizado'] = True
    
    return jsonify({'lat': lat, 'lon': lon, 'status': viagem_ativa['status'], 'finalizado': viagem_ativa['finalizado']})


@app.route('/api/viagens/finalizar', methods=['PUT'])
def finalizar_viagem():
    global viagem_ativa
    if not viagem_ativa: return jsonify({'status': 'erro'}), 404
    viagem_ativa = {}
    return jsonify({'status': 'sucesso'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
