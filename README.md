# 📊 Agente de Análise de Dados com IA (Gemini & Pandas)

Agente autônomo em Python que interpreta perguntas em linguagem natural sobre bases de dados em CSV, gera e executa código Pandas dinamicamente e exporta visualizações gráficas de performance.

## 🛠️ Tecnologias Utilizadas
* **Python 3.12+**
* **Google Gemini API (`google-genai`)**
* **Pandas** (Manipulação e Análise de Dados)
* **Matplotlib / Seaborn** (Geração de Gráficos)
* **python-dotenv** (Gestão de variáveis de ambiente)

## 📁 Estrutura do Projeto
```text
Agente-de-Dados-com-IA/
├── data/
│   └── vendas_exemplo.csv   # Base de dados de testes
├── outputs/                 # Pasta onde os gráficos são salvos
├── .env.example             # Modelo das variáveis de ambiente
├── .gitignore               # Arquivos ignorados pelo Git
├── agent.py                 # Lógica principal do agente e integração com LLM
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação do repositório