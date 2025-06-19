# Projeto Frota: Sistema de Rastreamento e Simulação de Viagens

Sistema web completo para criação, simulação e monitoramento de viagens logísticas em tempo real. Desenvolvido com Python + Flask no backend e JavaScript + Leaflet no frontend para uma interface moderna e interativa.

---

## Principais Funcionalidades

- Cadastro de Entidades:
  - Veículos: Cadastro por placa e modelo.
  - Locais: Nome, tipo (Origem/Destino) e coordenadas (Latitude/Longitude).

- Criação de Viagens:
  - Selecione um veículo, origem e destino para iniciar uma nova viagem.

- Simulação Realista de Rota:
  - Usa a API da OpenRouteService para calcular rotas otimizadas para caminhões.
  - Simulação é controlada pelo backend para performance e estabilidade.

- Painel Interativo em Tempo Real:
  - Mapa Dinâmico (Leaflet.js) mostrando o trajeto.
  - Movimento do Caminhão: Atualização a cada 5 segundos.
  - Status Dinâmico: (A CAMINHO DA ORIGEM, NA ORIGEM, EM TRÂNSITO, NO DESTINO).
  - Rastro Visível: Posições salvas no mapa com popups clicáveis.
  - Trajetória Contínua: Linha ligando os pontos do trajeto.
  - Persistência Visual: Mesmo após atualizar a página.
  - Popups Interativos: Caminhão exibe a placa, pontos mostram coordenadas.

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

---

## Como Executar o Projeto Localmente

### 1. Pré-requisitos
- Python 3 instalado
- pip funcionando
- Chave da API da [OpenRouteService](https://openrouteservice.org/dev/#/signup)

### 2. Instalação

```bash
# Clone o projeto
git clone https://github.com/Vlyzin/ProjetoFT.git
cd ProjetoFT

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

Acesse: http://127.0.0.1:5000

---

## Fluxo de Uso

1. Cadastrar Veículo: Vá até "Veículos" e adicione um novo.
2. Cadastrar Locais: Adicione pelo menos uma origem e um destino.
3. Criar Viagem: Selecione veículo, origem e destino. Inicie.
4. Painel Principal: Veja o caminhão se mover e o status atualizar.
5. Finalizar Viagem: Ao chegar ao destino, finalize a simulação.

---

## Próximos Passos (Roadmap)

- Autenticação de Usuários
- Banco de Dados (SQLite/PostgreSQL)
- CRUD completo de Locais
- Monitoramento Múltiplo de Viagens
- Geração de Relatórios de Viagens
- Tradução PT/EN na Interface

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

## Contribuições

Sugestões, melhorias e pull requests são bem-vindos.
