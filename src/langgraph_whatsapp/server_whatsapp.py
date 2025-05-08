import logging
from typing import Union
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from src.langgraph_whatsapp.channel_whatsapp import WhatsAppBusinessAgent
from src.langgraph_whatsapp.config import WHATSAPP_VERIFY_TOKEN

LOGGER = logging.getLogger("whatsapp")
APP = FastAPI()
WSP_AGENT = WhatsAppBusinessAgent()

@APP.get("/webhook", response_model=None)
async def verify_webhook(request: Request) -> JSONResponse:
    """Handle webhook verification from WhatsApp Cloud API
    
    WhatsApp Cloud API will make a GET request to verify your webhook endpoint.
    We must return the challenge code if the verify token matches.
    
    See: https://developers.facebook.com/docs/graph-api/webhooks/getting-started
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if not all([mode, token, challenge]):
        return JSONResponse(
            status_code=400,
            content={"error": "Missing required parameters"}
        )

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        try:
            return JSONResponse(
                status_code=200,
                content=int(challenge)
            )
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid challenge value"}
            )

    return JSONResponse(
        status_code=403,
        content={"error": "Invalid verify token"}
    )

@APP.post("/webhook")
async def whatsapp_webhook(request: Request) -> JSONResponse:
    """Handle incoming messages and status updates from WhatsApp Cloud API
    
    This endpoint receives various types of webhooks:
    - Message received
    - Message status update
    - Media upload status
    - Business account update
    
    See: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/components
    """
    try:
        # Process the webhook and get response data
        response_data = await WSP_AGENT.handle_message(request)

        # Return success response
        return JSONResponse(
            content=response_data,
            status_code=200
        )

    except HTTPException as e:
        LOGGER.error("Handled error: %s", e.detail)
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.detail}
        )

    except Exception as e:
        LOGGER.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

# Health check endpoint
@APP.get("/health")
async def health_check() -> JSONResponse:
    """Simple health check endpoint"""
    return JSONResponse(
        content={"status": "healthy"},
        status_code=200
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        APP,
        host="0.0.0.0",
        port=8082,
        log_level="info",
        ssl_keyfile="key.pem",  # SSL é obrigatório para webhooks do WhatsApp
        ssl_certfile="cert.pem"
    )
