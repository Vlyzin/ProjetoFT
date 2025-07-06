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
    /**
     * NOVO: Função para validar CPF
     * @param {string} cpf 
     * @returns {boolean} - Retorna true se o CPF for válido, false caso contrário.
     */
    function validarCPF(cpf) {
        // 1. Remove caracteres não numéricos
        const cpfLimpo = cpf.replace(/[^\d]/g, '');

        // 2. Verifica se tem 11 dígitos
        if (cpfLimpo.length !== 11) {
            return false;
        }

        // 3. Verifica se todos os dígitos são iguais
        const todosIguais = /^(\d)\1+$/.test(cpfLimpo);
        if (todosIguais) {
            return false;
        }

        // 4. Calcula o primeiro dígito verificador
        let soma = 0;
        for (let i = 0; i < 9; i++) {
            soma += parseInt(cpfLimpo.charAt(i)) * (10 - i);
        }
        let resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) {
            resto = 0;
        }
        if (resto !== parseInt(cpfLimpo.charAt(9))) {
            return false;
        }

        // 5. Calcula o segundo dígito verificador
        soma = 0;
        for (let i = 0; i < 10; i++) {
            soma += parseInt(cpfLimpo.charAt(i)) * (11 - i);
        }
        resto = (soma * 10) % 11;
        if (resto === 10 || resto === 11) {
            resto = 0;
        }
        if (resto !== parseInt(cpfLimpo.charAt(10))) {
            return false;
        }

        // Se passou por todas as verificações, o CPF é válido
        return true;
    }

    /**
     * NOVO: Função para aplicar a máscara de CPF (XXX.XXX.XXX-XX).
     * @param {HTMLInputElement} input - O campo de input do CPF.
     */
    function mascaraCPF(input) {
        let value = input.value.replace(/\D/g, ''); // Remove tudo que não é dígito
        value = value.slice(0, 11); // Limita a 11 dígitos

        if (value.length > 9) {
            value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        } else if (value.length > 6) {
            value = value.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
        } else if (value.length > 3) {
            value = value.replace(/(\d{3})(\d{1,3})/, '$1.$2');
        }
        
        input.value = value;
    }

    // --- Lógica para o Formulário de Motorista ---
    const formMotorista = document.getElementById('form-motorista');
    if (formMotorista) {
        const cpfInput = document.getElementById('cpf-motorista');
        
        cpfInput.addEventListener('input', () => mascaraCPF(cpfInput));

        formMotorista.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const nome = document.getElementById('nome-motorista').value;
            const cpf = cpfInput.value;
            const sexo = document.getElementById('sexo-motorista').value;

            if (!validarCPF(cpf)) {
                alert("O CPF inserido é inválido. Por favor, verifique.");
                return; // Para a execução aqui
            }

            const data = { nome, cpf, sexo };

    try {
        const response = await fetch(`${API_URL}/motoristas`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.mensagem || 'Falha ao criar motorista');
        }
        
        alert('Motorista criado com sucesso!');
        formMotorista.reset();
    } catch (err) { 
        alert(err.message); 
    }
        });
    }

    // --- Lógica para o Formulário de Local ---
    const formLocal = document.getElementById('form-local');
      if (formLocal) {
        
        const tomSelectEstado = new TomSelect("#estado-local", {
            create: false,
            sortField: {
                field: "text",
                direction: "asc"
            }
        });

        formLocal.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                nome: document.getElementById('nome-local').value,
                tipo: document.getElementById('tipo-local').value,
                cidade: document.getElementById('cidade-local').value,
                estado: document.getElementById('estado-local').value,
                lat: document.getElementById('lat-local').value,
                lon: document.getElementById('lon-local').value,
            };
            if (isNaN(parseFloat(data.lat)) || isNaN(parseFloat(data.lon))) {
                alert("Por favor, insira valores numéricos válidos para latitude e longitude.");
                return;
            }
            try {
                const response = await fetch(`${API_URL}/locais`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
                });
                const result = await response.json();
                if (!response.ok) throw new Error(result.mensagem || 'Falha ao criar local');
                
                alert('Local criado com sucesso!');
                formLocal.reset();
                tomSelectEstado.clear(); 

            } catch (err) { alert(err.message); }
        });
    }

    // --- Lógica para o Formulário de Viagem ---
    const formViagem = document.getElementById('form-viagem');
    if (formViagem) {
        const populateForm = async () => {
            try {
                const [veiculosRes, locaisRes, motoristasRes] = await Promise.all([
                    fetch(`${API_URL}/veiculos`),
                    fetch(`${API_URL}/locais`),
                    fetch(`${API_URL}/motoristas`)
                ]);
                const veiculos = await veiculosRes.json();
                const locais = await locaisRes.json();
                const motoristas = await motoristasRes.json();
                
                const selVeiculo = document.getElementById('viagem-veiculo');
                const selOrigem = document.getElementById('viagem-origem');
                const selDestino = document.getElementById('viagem-destino');
                const selMotorista = document.getElementById('viagem-motorista');

                selVeiculo.innerHTML = '<option value="">Selecione um veículo</option>' + veiculos.map(v => `<option value="${v.id}">${v.placa} - ${v.modelo}</option>`).join('');
                selOrigem.innerHTML = '<option value="">Selecione uma origem</option>' + locais.filter(l => l.tipo === 'Origem').map(l => `<option value="${l.id}">${l.nome}</option>`).join('');
                selDestino.innerHTML = '<option value="">Selecione um destino</option>' + locais.filter(l => l.tipo === 'Destino').map(l => `<option value="${l.id}">${l.nome}</option>`).join('');
                
                // ATUALIZADO: Mostra o nome e o CPF do motorista no dropdown
                selMotorista.innerHTML = '<option value="">Selecione um motorista</option>' + motoristas.map(m => 
                    `<option value="${m.id}">${m.nome} (${m.cpf})</option>`
                ).join('');

            } catch (error) { console.error("Erro ao popular formulário: ", error); }
        };

        populateForm();

        formViagem.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                veiculo_id: document.getElementById('viagem-veiculo').value,
                origem_id: document.getElementById('viagem-origem').value,
                destino_id: document.getElementById('viagem-destino').value,
                motorista_id: document.getElementById('viagem-motorista').value,
            };
            
            if (!data.veiculo_id || !data.origem_id || !data.destino_id || !data.motorista_id) {
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