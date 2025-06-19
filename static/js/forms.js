document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:5000/api';

    /**
     * Função genérica para enviar dados e tratar a resposta
     */
    async function postData(url, data, successMessage) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            // Tenta ler a resposta como JSON independentemente do status
            const result = await response.json();
            
            // Se a resposta não for OK, lança um erro com a mensagem do backend
            if (!response.ok) {
                throw new Error(result.mensagem || `Falha na requisição: ${response.statusText}`);
            }

            alert(successMessage);
            return true;
        } catch (err) {
            console.error('Erro na requisição:', err);
            // Verifica se o erro é de sintaxe JSON (caso o backend retorne HTML)
            if (err instanceof SyntaxError) {
                alert("Erro: O servidor respondeu com um formato inesperado. Verifique o console do servidor Python.");
            } else {
                alert(`Erro: ${err.message}`);
            }
            return false;
        }
    }

    // --- Lógica para o Formulário de Veículo ---
    const formVeiculo = document.getElementById('form-veiculo');
    if (formVeiculo) {
        formVeiculo.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                placa: document.getElementById('placa').value,
                modelo: document.getElementById('modelo').value
            };
            const success = await postData(`${API_URL}/veiculos`, data, 'Veículo criado com sucesso!');
            if (success) {
                formVeiculo.reset();
            }
        });
    }

    // --- Lógica para o Formulário de Local ---
    const formLocal = document.getElementById('form-local');
    if (formLocal) {
        formLocal.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                nome: document.getElementById('nome-local').value,
                tipo: document.getElementById('tipo-local').value,
                lat: document.getElementById('lat-local').value,
                lon: document.getElementById('lon-local').value,
            };
            if (isNaN(parseFloat(data.lat)) || isNaN(parseFloat(data.lon))) {
                alert("Por favor, insira valores numéricos válidos para latitude e longitude.");
                return;
            }
            const success = await postData(`${API_URL}/locais`, data, 'Local criado com sucesso!');
            if (success) {
                formLocal.reset();
            }
        });
    }

    // --- Lógica para o Formulário de Viagem ---
    const formViagem = document.getElementById('form-viagem');
    if (formViagem) {
        const populateForm = async () => {
            try {
                const [veiculosRes, locaisRes] = await Promise.all([
                    fetch(`${API_URL}/veiculos`),
                    fetch(`${API_URL}/locais`)
                ]);
                const veiculos = await veiculosRes.json();
                const locais = await locaisRes.json();
                
                const selVeiculo = document.getElementById('viagem-veiculo');
                const selOrigem = document.getElementById('viagem-origem');
                const selDestino = document.getElementById('viagem-destino');

                selVeiculo.innerHTML = '<option value="">Selecione um veículo</option>' + veiculos.map(v => `<option value="${v.id}">${v.placa} - ${v.modelo}</option>`).join('');
                selOrigem.innerHTML = '<option value="">Selecione uma origem</option>' + locais.filter(l => l.tipo === 'Origem').map(l => `<option value="${l.id}">${l.nome}</option>`).join('');
                selDestino.innerHTML = '<option value="">Selecione um destino</option>' + locais.filter(l => l.tipo === 'Destino').map(l => `<option value="${l.id}">${l.nome}</option>`).join('');
            } catch (error) {
                console.error("Erro ao popular formulário: ", error);
            }
        };

        populateForm();

        formViagem.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                veiculo_id: document.getElementById('viagem-veiculo').value,
                origem_id: document.getElementById('viagem-origem').value,
                destino_id: document.getElementById('viagem-destino').value,
            };
            
            // ATUALIZADO: Validação crucial para evitar o erro
            if (!data.veiculo_id || !data.origem_id || !data.destino_id) {
                alert("Por favor, preencha todos os campos para iniciar a viagem.");
                return;
            }
            
            const success = await postData(`${API_URL}/viagens`, data, 'Viagem criada com sucesso! Redirecionando para o painel...');
            if (success) {
                window.location.href = '/';
            }
        });
    }
});