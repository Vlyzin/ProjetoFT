import math
import openrouteservice
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO DA API DE ROTAS ---
ORS_API_KEY = ''
ors_client = openrouteservice.Client(key=ORS_API_KEY)

# --- BANCO DE DADOS EM MEMÓRIA ---
veiculos = []
locais = []
id_counter = 1
viagem_ativa = {}

# --- ROTAS PARA RENDERIZAR PÁGINAS ---
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

# --- API ENDPOINTS ---

@app.route('/api/veiculos', methods=['POST', 'GET'])
def handle_veiculos():
    global id_counter
    if request.method == 'POST':
        dados = request.json
        novo_veiculo = {'id': id_counter, 'placa': dados['placa'], 'modelo': dados['modelo']}
        veiculos.append(novo_veiculo)
        id_counter += 1
        return jsonify({'status': 'sucesso', 'veiculo': novo_veiculo}), 201
    return jsonify(veiculos)

@app.route('/api/locais', methods=['POST', 'GET'])
def handle_locais():
    global id_counter
    if request.method == 'POST':
        dados = request.json
        novo_local = {'id': id_counter, 'nome': dados['nome'], 'tipo': dados['tipo'], 'lat': float(dados['lat']), 'lon': float(dados['lon'])}
        locais.append(novo_local)
        id_counter += 1
        return jsonify({'status': 'sucesso', 'local': novo_local}), 201
    return jsonify(locais)

@app.route('/api/viagens', methods=['POST'])
def create_viagem():
    global viagem_ativa
    if viagem_ativa: return jsonify({'status': 'erro', 'mensagem': 'Já existe uma viagem em andamento.'}), 400
    
    try:
        dados = request.json
        if not all(k in dados and dados[k] for k in ['veiculo_id', 'origem_id', 'destino_id']):
             return jsonify({'status': 'erro', 'mensagem': 'IDs de veículo, origem ou destino estão faltando.'}), 400

        veiculo = next((v for v in veiculos if v['id'] == int(dados['veiculo_id'])), None)
        origem = next((l for l in locais if l['id'] == int(dados['origem_id'])), None)
        destino = next((l for l in locais if l['id'] == int(dados['destino_id'])), None)
        if not all([veiculo, origem, destino]): 
            return jsonify({'status': 'erro', 'mensagem': 'Um dos IDs fornecidos não foi encontrado.'}), 404

        ponto_partida_sp = (-46.633999737460684, -23.55040577221674)
        
        coords_estagio_1 = (ponto_partida_sp, (origem['lon'], origem['lat']))
        
        routes = ors_client.directions(coordinates=coords_estagio_1, profile='driving-hgv', format='geojson')
        route_coordinates = routes['features'][0]['geometry']['coordinates']
    
    except (ValueError, KeyError) as e:
        print(f"ERRO DE DADOS NA REQUISIÇÃO: {e}")
        return jsonify({'status': 'erro', 'mensagem': 'Dados inválidos ou incompletos na requisição.'}), 400
    except Exception as e:
        print(f"ERRO AO CRIAR VIAGEM: {e}")
        return jsonify({'status': 'erro', 'mensagem': 'Não foi possível calcular a rota inicial.'}), 500

    viagem_ativa = {
        'veiculo': veiculo, 'origem': origem, 'destino': destino, 'status': 'A CAMINHO DA ORIGEM',
        'ponto_partida_sp': {'lat': ponto_partida_sp[1], 'lon': ponto_partida_sp[0]},
        'route_coordinates': route_coordinates, 
        'simulation_index': 0, 
        'pings_na_origem': 0, 
        'finalizado': False,
        'pontos_percorridos': [],
        'stage': 'to_origin' # Controla o estágio da viagem
    }
    return jsonify({'status': 'sucesso'}), 201


@app.route('/api/viagens/ativa', methods=['GET'])
def get_viagem_ativa():
    if not viagem_ativa: return jsonify({})
    dados_iniciais = {
        'veiculo': viagem_ativa['veiculo'], 'origem': viagem_ativa['origem'], 'destino': viagem_ativa['destino'],
        'status': viagem_ativa['status'], 'ponto_partida_sp': viagem_ativa['ponto_partida_sp'],
        'pontos_percorridos': viagem_ativa.get('pontos_percorridos', [])
    }
    return jsonify(dados_iniciais)

@app.route('/api/viagens/tick', methods=['GET'])
def tick_viagem():
    if not viagem_ativa or viagem_ativa.get('finalizado', False): return jsonify({'status': 'sem_viagem'})

    pulo_simulacao = 45
    viagem_ativa['simulation_index'] = min(viagem_ativa['simulation_index'] + pulo_simulacao, len(viagem_ativa['route_coordinates']) - 1)
    
    index = viagem_ativa['simulation_index']
    lon, lat = viagem_ativa['route_coordinates'][index]
    
    viagem_ativa['pontos_percorridos'].append([lon, lat])

    def haversine_distance(lon1, lat1, lon2, lat2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)
        a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    status_atual = viagem_ativa['status']
    novo_status = status_atual

    # Estágio 1: Indo para a Origem
    if viagem_ativa['stage'] == 'to_origin':
        dist_origem = haversine_distance(lon, lat, viagem_ativa['origem']['lon'], viagem_ativa['origem']['lat'])
        # Se entrar no raio da origem, muda de estágio
        if dist_origem <= 500:
            novo_status = 'NA ORIGEM'
            viagem_ativa['stage'] = 'to_destination'
            print("--- CHEGOU NA ORIGEM: INICIANDO ESTÁGIO 2 (Origem -> Destino) ---")
            
            # Calcula a nova rota do estágio 2
            origem_coords = (viagem_ativa['origem']['lon'], viagem_ativa['origem']['lat'])
            destino_coords = (viagem_ativa['destino']['lon'], viagem_ativa['destino']['lat'])
            try:
                routes = ors_client.directions(coordinates=(origem_coords, destino_coords), profile='driving-hgv', format='geojson')
                viagem_ativa['route_coordinates'] = routes['features'][0]['geometry']['coordinates']
                viagem_ativa['simulation_index'] = 0 # Reseta o progresso para a nova rota
            except Exception as e:
                print(f"ERRO AO CALCULAR ROTA DO ESTÁGIO 2: {e}")
                viagem_ativa['finalizado'] = True

    # Estágio 2: Indo para o Destino
    elif viagem_ativa['stage'] == 'to_destination':
        dist_origem = haversine_distance(lon, lat, viagem_ativa['origem']['lon'], viagem_ativa['origem']['lat'])
        dist_destino = haversine_distance(lon, lat, viagem_ativa['destino']['lon'], viagem_ativa['destino']['lat'])
        
        if status_atual == 'NA ORIGEM' and dist_origem > 500:
            novo_status = 'EM TRÂNSITO'
        elif status_atual == 'EM TRÂNSITO' and dist_destino <= 500:
            novo_status = 'NO DESTINO'

    viagem_ativa['status'] = novo_status
    
    # Condição de parada final
    if novo_status == 'NO DESTINO' and viagem_ativa['simulation_index'] >= len(viagem_ativa['route_coordinates']) - 1:
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
