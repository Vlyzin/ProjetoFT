# Projeto Frota: Sistema de Rastreamento e Simulação de Viagens

Sistema web completo para criação, simulação e monitoramento de viagens logísticas em tempo real. Desenvolvido com Python + Flask no backend e JavaScript + Leaflet no frontend para uma interface moderna e interativa.

---

## Log de Atualizações Recentes

### Atualização de 05/07/2025: Persistência de Dados e Melhorias de Usabilidade

- **Persistência de Dados com JSON:** Dados de veículos, locais e motoristas agora são salvos em arquivos `.json` na pasta `/json`, simulando um banco de dados local. Planeja-se a migração para PostgreSQL futuramente.
- **Validação de Dados Duplicados:** Placas, nomes de locais e CPFs agora são validados para evitar duplicatas.
- **Simulação Contínua e Persistente:** A simulação agora é gerenciada pelo backend e continua mesmo com navegação ou atualização de página.
- **Ponto de Partida Dinâmico:** A viagem inicia no centro do estado do local de origem.
- **Melhorias na Interface de Cadastro:**
  - Seleção de estado com busca (Tom Select).
  - Exibição de nome + CPF no dropdown de motoristas.
  - Validação robusta de CPF (máscara, formato e dígito verificador).

---

## Principais Funcionalidades

- **Cadastro de Entidades:**
  - Veículos: Placa e modelo.
  - Locais: Nome, tipo (Origem/Destino) e coordenadas.
  - Motoristas: Nome, CPF e sexo, com validação completa.

- **Criação de Viagens:**
  - Escolha de veículo, motorista, origem e destino.

- **Simulação Realista de Rota:**
  - Uso da API da OpenRouteService para rotas otimizadas.
  - Backend controla a lógica de simulação.

- **Painel Interativo em Tempo Real:**
  - Mapa com trajeto da viagem (Leaflet.js).
  - Atualização a cada 5 segundos.
  - Status dinâmico da viagem.
  - Histórico e rastro no mapa com popups interativos.
  - Persistência mesmo após refresh da página.

---

## Tecnologias Utilizadas

### Backend
- Python 3
- Flask
- Flask-CORS
- openrouteservice-py

### Frontend
- HTML5
- CSS3 + Tailwind CSS
- JavaScript (ES6+)
- Leaflet.js
- Tom Select

---

## Como Executar o Projeto Localmente

### 1. Pré-requisitos

- Python 3 instalado
- `pip` funcionando
- Chave da API da [OpenRouteService](https://openrouteservice.org/dev/#/signup)

### 2. Instalação

```bash
# Clone o projeto
git clone https://github.com/Vlyzin/ProjetoFT.git
cd ProjetoFT

# Crie a pasta para os arquivos JSON
mkdir json

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração da API

Abra o arquivo `app.py` e substitua:

```python
ORS_API_KEY = 'SUA_CHAVE_API_AQUI'
```

por sua chave real da OpenRouteService.

### 4. Rodar o servidor

```bash
python app.py
```

Acesse: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Fluxo de Uso

1. Cadastrar Veículo e Motorista: Use os menus laterais.
2. Cadastrar Locais: Adicione uma origem e um destino.
3. Criar Viagem: Escolha os dados e inicie a simulação.
4. Painel Principal: Acompanhe o trajeto em tempo real.
5. Finalizar Viagem: Ao chegar ao destino, finalize.

---

## Próximos Passos (Roadmap)

- Autenticação de Usuários (login/cadastro)
- Migração para PostgreSQL
- CRUD completo de entidades
- Monitoramento de múltiplas viagens simultâneas
- Geração de relatórios
- Tradução da interface (PT/EN)

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## Contribuições

Sugestões, melhorias e pull requests são muito bem-vindos!