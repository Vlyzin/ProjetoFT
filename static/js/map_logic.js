document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:5000/api';
    let map;
    let truckMarker;
    let routePolyline;
    let simulationInterval = null;


    function initMap() {
        map = L.map('map').setView([0, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
    }

    /**
     * Constrói o painel de status com as informações da viagem.
     * @param {object} viagem - O objeto da viagem ativa.
     */
    function updateStatusBar(viagem) {
        const statusContainer = document.getElementById('status-container');
        const statusColors = {
            'A CAMINHO DA ORIGEM': 'bg-yellow-100 text-yellow-800',
            'NA ORIGEM': 'bg-orange-100 text-orange-800',
            'EM TRÂNSITO': 'bg-blue-100 text-blue-800',
            'NO DESTINO': 'bg-green-100 text-green-800'
        };
        const statusClass = statusColors[viagem.status] || 'bg-gray-100';

        statusContainer.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                <div><strong>Placa:</strong> ${viagem.veiculo.placa}</div>
                <div><strong>Origem:</strong> ${viagem.origem.nome}</div>
                <div><strong>Destino:</strong> ${viagem.destino.nome}</div>
                <div class="flex items-center">
                    <strong>Status:</strong> 
                    <span class="ml-2 px-3 py-1 text-sm font-semibold rounded-full ${statusClass}" id="trip-status-badge">
                        ${viagem.status.replace(/_/g, ' ')}
                    </span>
                </div>
            </div>
            <div id="action-area" class="mt-4 text-right"></div>
        `;
    }

    /**
     */
    function startPositionPolling() {
        if (simulationInterval) clearInterval(simulationInterval);

        simulationInterval = setInterval(async () => {
            try {
                const response = await fetch(`${API_URL}/viagens/tick`);
                const data = await response.json();

                if (data.status === 'sem_viagem' || !truckMarker) {
                    clearInterval(simulationInterval);
                    return;
                }

                const newPosition = [data.lat, data.lon];
                truckMarker.setLatLng(newPosition);

                // Desenha o rastro e adiciona o popup com as coordenadas
                L.circleMarker(newPosition, { 
                    radius: 4, fillColor: "#ef4444", color: "#fff",
                    weight: 1.5, opacity: 1, fillOpacity: 0.8
                })
                .addTo(map)
                .bindPopup(`<b>Posição:</b><br>Lat: ${data.lat.toFixed(6)}<br>Lon: ${data.lon.toFixed(6)}`);


                if (routePolyline) {
                    routePolyline.addLatLng(newPosition);
                }

                const statusBadge = document.getElementById('trip-status-badge');
                if (statusBadge) {
                    statusBadge.textContent = data.status.replace(/_/g, ' ');
                }

                if (data.finalizado) {
                    clearInterval(simulationInterval);
                    const actionArea = document.getElementById('action-area');
                    actionArea.innerHTML = '<button id="btn-finalizar" class="bg-red-500 text-white font-bold py-2 px-4 rounded hover:bg-red-600">Finalizar Viagem</button>';
                    document.getElementById('btn-finalizar').onclick = async () => {
                        await fetch(`${API_URL}/viagens/finalizar`, { method: 'PUT' });
                        alert('Viagem finalizada!');
                        window.location.reload();
                    };
                }
            } catch (error) {
                console.error("Erro no loop de atualização:", error);
                clearInterval(simulationInterval);
            }
        }, 5000);
    }

    /**
     * Função principal que desenha o estado inicial do mapa e da viagem.
     */
    async function loadActiveTrip() {
        try {
            const response = await fetch(`${API_URL}/viagens/ativa`);
            const viagem = await response.json();

            if (Object.keys(viagem).length > 0) {
                updateStatusBar(viagem);

                const spCoords = [viagem.ponto_partida_sp.lat, viagem.ponto_partida_sp.lon];
                const origemCoords = [viagem.origem.lat, viagem.origem.lon];
                const destinoCoords = [viagem.destino.lat, viagem.destino.lon];

                L.circle(origemCoords, { radius: 500, color: 'blue' }).addTo(map)
                    .bindTooltip("Origem", { permanent: true, direction: 'top' }).openTooltip();
                L.circle(destinoCoords, { radius: 500, color: 'green' }).addTo(map)
                    .bindTooltip("Destino", { permanent: true, direction: 'top' }).openTooltip();
                
                const truckIcon = L.icon({
                    iconUrl: '/static/img/truck-icon.png',
                    iconSize: [40, 40], iconAnchor: [20, 20]
                });
                truckMarker = L.marker(spCoords, { icon: truckIcon })
                    .addTo(map)
                    .bindPopup(`<b>Veículo:</b> ${viagem.veiculo.placa}`);

                // Inicializa a linha da rota
                routePolyline = L.polyline([], { color: '#0d6efd', weight: 4, opacity: 0.8 }).addTo(map);
                
                // Desenha o histórico de pontos que já existem e adiciona os popups a eles
                if (viagem.pontos_percorridos && viagem.pontos_percorridos.length > 0) {
                    const latLngs = [];
                    viagem.pontos_percorridos.forEach(ponto => {
                        const [lon, lat] = ponto;
                        const latLng = [lat, lon];
                        latLngs.push(latLng);
                        
                        L.circleMarker(latLng, { 
                            radius: 4, fillColor: "#ef4444", color: "#fff",
                            weight: 1.5, opacity: 1, fillOpacity: 0.8
                        })
                        .addTo(map)
                        .bindPopup(`<b>Posição:</b><br>Lat: ${lat.toFixed(6)}<br>Lon: ${lon.toFixed(6)}`);
                    });
                    
                    routePolyline.setLatLngs(latLngs);
                    truckMarker.setLatLng(latLngs[latLngs.length - 1]);
                }
                
                map.fitBounds([spCoords, origemCoords, destinoCoords], { padding: [50, 50] });
                startPositionPolling();

            } else {
                document.getElementById('status-container').innerHTML = '<p class="text-gray-500">Nenhuma viagem ativa. Crie uma no menu "Criar Viagem".</p>';
            }
        } catch (error) {
            console.error('Erro ao carregar dados da viagem:', error);
            document.getElementById('status-container').innerHTML = `<p class="text-red-500">Erro ao carregar a viagem. Verifique o console.</p>`;
        }
    }

    // --- INÍCIO DA EXECUÇÃO ---
    // Garante que só vamos tentar rodar a lógica do mapa se o elemento #map existir na página
    if (document.getElementById('map')) {
        initMap();
        loadActiveTrip();
    }
});