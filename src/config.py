from dotenv import load_dotenv
import os

# Carrega do .env forçando sobrescrita de variáveis existentes
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path, override=True)

# Pega as chaves do .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
ZAPIER_URL_MCP = os.getenv('ZAPIER_URL_MCP')
SUPERMEMORY_URL_MCP = os.getenv('SUPERMEMORY_URL_MCP')

