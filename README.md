# 🚀 Rastreador de Preços Inteligente

![GitHub last commit](https://img.shields.io/github/last-commit/seuuser/rastreador-precos)
![GitHub top language](https://img.shields.io/github/languages/top/seuuser/rastreador-precos)

**Monitoramento automático de preços com notificações e previsão de IA.**

## 📸 Demonstração
![Dashboard](docs/dashboard.gif)

## 🧩 Funcionalidades
- ✅ Cadastro de produtos de e-commerce e passagens aéreas
- ✅ Coleta diária automática à meia-noite com Playwright stealth
- ✅ Histórico de preços com gráfico interativo (Recharts)
- ✅ Notificações por e-mail, Telegram e Discord
- ✅ Autenticação JWT e sistema de usuários
- ✅ API REST documentada (Swagger)
- ✅ Previsão de preços com Facebook Prophet (microsserviço)
- ✅ Testes automatizados e CI/CD com GitHub Actions
- ✅ Containerização completa (Docker + Docker Compose)

## 🛠 Tecnologias
- **Backend:** FastAPI (async), SQLAlchemy 2.0, PostgreSQL, APScheduler
- **Scraping:** Playwright, Playwright-Stealth, rotação de User-Agent
- **IA:** Prophet (via microsserviço)
- **Frontend:** React, TypeScript, Recharts
- **DevOps:** Docker, Nginx, GitHub Actions, VPS

## ▶️ Como executar
1. Clone o repo
2. Copie `.env.example` para `.env`
3. Execute `docker-compose up -d`
4. Acesse `http://localhost` (frontend) ou `http://localhost:8000/docs` (API)

## 📊 Previsão de Preços
O microsserviço de IA utiliza séries temporais para prever a tendência de preço nos próximos 30 dias. Endpoint: `GET http://localhost:8001/predict/{product_id}`

## 🗂 Estrutura do Projeto
├── backend/ # API FastAPI + scrapers
├── frontend/ # Aplicação React
├── prediction_service/# Microsserviço de IA
├── nginx/ # Configuração do proxy reverso
├── docker-compose.yml
└── .github/workflows # CI/CD


## 🧪 Testes
`docker-compose exec backend pytest --cov=app tests/`

## 📈 Decisões de Arquitetura
- Monolito modular: código organizado por domínios, facilitando extração para microsserviços
- Scrapers baseados em classe abstrata: cada site é um plugin
- Fila de scraping com retry e delay randômico para evitar bloqueios
- Microsserviço separado de IA demonstra desacoplamento e escalabilidade

## 👤 Autor
**Luiz Guilherme da Silva** – 

---

graph TD
    A[Usuário] -->|HTTP| B[Nginx]
    B --> C[Frontend React]
    B --> D[Backend FastAPI :8000]
    D --> E[(PostgreSQL)]
    D --> F[Scraper Worker]
    F --> G[Sites Externos]
    D --> H[Notificações: SendGrid, Telegram]
    A --> I[Serviço Previsão :8001]
    I --> D