# LangGraph WhatsApp Agent

Para executar a aplicação:
```bash
# crie o virtual environment
python -m venv venv

# ative o virtual environment
source venv/bin/activate

# com o uv instalado
uv pip install -r pyproject.toml

# execute with Twilio
python main_twilio.py

# or execute with WhatsApp Business
python main_whatsapp.py

# using gunicorn is recommended for production
```

## Deploy
Para fazer o deploy da aplicação, é recomendado usar o LangGraph Platform, porém utilizei um servidor EC2 para fazer o deploy.

Foi utilizado o Nginx com proxy reverso para servir a aplicação.

Para inicializar foi utilizado o gunicorn.

```bash
# para iniciar
sudo systemctl start gunicorn

# caso haja alterações no código ou no arquivo de configuração do gunicorn
sudo systemctl restart gunicorn

# para verificar o status
sudo systemctl status gunicorn

# para parar
sudo systemctl stop gunicorn

# para alterar o arquivo de configuração do gunicorn
sudo nano /etc/systemd/system/gunicorn.service
```

## Logs
```bash
# para ver os logs de erro do gunicorn em tempo real
sudo tail -f /var/log/gunicorn/error.log

# para ver os logs da aplicação em tempo real
sudo tail -f /var/log/gunicorn/app.log
```

## About the project

A template for building WhatsApp agents using LangGraph and Twilio. This project enables you to deploy AI agents that interact with users via WhatsApp, process messages and images, and invoke custom graph-based agents hosted on the LangGraph Platform.

It provides a foundation for building scalable, secure, and maintainable AI agent services.

Fork this repo and iterate to create your production-ready solution.

![Architecture Diagram](./docs/app_architecture_v0.1.0.png)

## Features

- Create custom LangGraph-powered agents for WhatsApp
- Support for multi-agents with supervisor-based architecture
- Integration with Model Context Protocol (MCP) servers (Supermemory, Sapier, etc.)
- Support for image processing and multimodal interactions
- Persistent conversation state across messages
- Request validation for security
- Comprehensive observability via LangSmith
- Easy deployment with LangGraph Platform

## Stack

- **WhatsApp Integration**: Twilio API for messaging and multimedia handling
- **Agent Framework**: LangGraph (by LangChain) as the MCP client and multi-agent system using langgraph_supervisor
- **Models**: Supports Google Gemini, OpenAI GPT models, and more
- **MCP Servers**:
  Using langchain-mcp-adapters
  - Supermemory
  - Zapier for access to thousands of apps and integrations (Google, Slack, Spotify, etc.)
- **Observability**: Complete tracing with LangSmith
- **Deployment**: LangGraph Platform for simplified production hosting

## Prerequisites

- Twilio account with WhatsApp integration
- API key for LLM access (OpenAI, Google, etc.)
- LangGraph Platform access
- (Optional) MCP server configurations

## Getting Started

1. Fork this repository to start your own project
2. Build your agent using the template structure
3. Deploy to LangGraph Platform
![Langggraph Platform](./docs/langgraph-platform_config.png)
4. Configure Twilio webhook to point to your LangGraph deployment URL (/whatsapp)
![Twilio](./docs/twilio_config.png)

## License

This project is licensed under the terms included in the LICENSE file.