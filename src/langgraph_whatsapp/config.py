import logging
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

LOGGER = logging.getLogger(__name__)

LANGGRAPH_URL = os.getenv("LANGGRAPH_URL")
ASSISTANT_ID = os.getenv("LANGGRAPH_ASSISTANT_ID", "agent")
CONFIG = os.getenv("CONFIG") or "{}"
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")

# WhatsApp Business Cloud API Configuration
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")

# Optional: LangSmith for observability
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")