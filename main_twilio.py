import sys
from pathlib import Path

# Adiciona o diretório src ao PYTHONPATH
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# server.py
import logging
from urllib.parse import parse_qs

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
from twilio.request_validator import RequestValidator

from langgraph_whatsapp.channel_twilio import WhatsAppAgentTwilio
from langgraph_whatsapp.config import TWILIO_AUTH_TOKEN

LOGGER = logging.getLogger("server")
app = FastAPI()
WSP_AGENT = WhatsAppAgentTwilio()


class TwilioMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, path: str = "/whatsapp"):
        super().__init__(app)
        self.path = path
        self.validator = RequestValidator(TWILIO_AUTH_TOKEN)

    async def dispatch(self, request: Request, call_next):
        # Only guard the WhatsApp webhook
        if request.url.path == self.path and request.method == "POST":
            body = await request.body()

            # Signature check
            form_dict = parse_qs(body.decode(), keep_blank_values=True)
            flat_form_dict = {k: v[0] if isinstance(v, list) and v else v for k, v in form_dict.items()}
            
            proto = request.headers.get("x-forwarded-proto", request.url.scheme)
            host  = request.headers.get("x-forwarded-host", request.headers.get("host"))
            url   = f"{proto}://{host}{request.url.path}"
            sig   = request.headers.get("X-Twilio-Signature", "")

            if not self.validator.validate(url, flat_form_dict, sig):
                LOGGER.warning("Invalid Twilio signature for %s", url)
                return Response(status_code=401, content="Invalid Twilio signature")

            # Rewind: body and receive channel
            async def _replay() -> Message:
                return {"type": "http.request", "body": body, "more_body": False}

            request._body = body
            request._receive = _replay  # type: ignore[attr-defined]

        return await call_next(request)


app.add_middleware(TwilioMiddleware, path="/whatsapp")


# Health check endpoint
@app.get("/health")
async def health_check() -> JSONResponse:
    """Simple health check endpoint"""

    return JSONResponse(
        content={"status": "healthy"},
        status_code=200
    )


@app.post("/whatsapp")
async def whatsapp_reply_twilio(request: Request):
    try:
        xml = await WSP_AGENT.handle_message(request)
        return Response(content=xml, media_type="application/xml")
    except HTTPException as e:
        LOGGER.error("Handled error: %s", e.detail)
        raise
    except Exception as e:
        LOGGER.exception("Unhandled exception")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7777,
        log_level="info",
        #reload=True,
        #ssl_keyfile="key.pem",
        #ssl_certfile="cert.pem"
    )
