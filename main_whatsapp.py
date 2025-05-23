import sys
from pathlib import Path

# Adiciona o diretório src ao PYTHONPATH
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from langgraph_whatsapp.channel_whatsapp import WhatsAppBusinessAgent
from langgraph_whatsapp.config import WHATSAPP_VERIFY_TOKEN
import uvicorn

LOGGER = logging.getLogger("whatsapp")

WSP_AGENT = WhatsAppBusinessAgent()

app = FastAPI()


@app.get("/webhook", response_model=None)
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

    challenge_int = int(challenge) if challenge else None

    print("Challenge (int) received: ", challenge_int)

    if not all([mode, token, challenge_int]):
        return JSONResponse(
            status_code=400,
            content={"error": "Missing required parameters"}
        )

    try:
        if mode != "subscribe":
            return JSONResponse(
                status_code=403,
                content={"error": f"Invalid mode: {mode}"}
            )
            
        LOGGER.info(f"Token received: {token}")
        LOGGER.info(f"Token expected: {WHATSAPP_VERIFY_TOKEN}")
        
        if token != WHATSAPP_VERIFY_TOKEN:
            return JSONResponse(
                status_code=403,
                content={"error": f"Invalid verify token: {token}"}
            )
        
        return JSONResponse(
            status_code=200,
            content=challenge_int
        )
    except ValueError as e:
        LOGGER.error(f"Error processing webhook verification: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid challenge value: {challenge}"}
        )


@app.post("/webhook")
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
@app.get("/health")
async def health_check() -> JSONResponse:
    """Simple health check endpoint"""

    return JSONResponse(
        content={"status": "healthy"},
        status_code=200
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7777,
        #reload=True,
        #ssl_keyfile="key.pem",
        #ssl_certfile="cert.pem"
    )