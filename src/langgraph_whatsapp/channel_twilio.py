# channel.py
import base64, logging, requests
from abc import ABC, abstractmethod

from fastapi import Request, HTTPException
from twilio.twiml.messaging_response import MessagingResponse

from src.langgraph_whatsapp.agent import Agent
from src.langgraph_whatsapp.config import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID
from src.openai.audio import transcribe_audio

LOGGER = logging.getLogger("whatsapp")


def twilio_url_to_data_uri(url: str, content_type: str = None) -> str:
    """Download the Twilio media URL and convert to data‑URI (base64)."""
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
        raise RuntimeError("Twilio credentials are missing")

    LOGGER.info(f"Downloading image from Twilio URL: {url}")
    resp = requests.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=20)
    resp.raise_for_status()

    # Use provided content_type or get from headers
    mime = content_type or resp.headers.get('Content-Type')

    # Ensure we have a proper image mime type
    if not mime or not mime.startswith('image/'):
        LOGGER.warning(f"Converting non-image MIME type '{mime}' to 'image/jpeg'")
        mime = "image/jpeg"  # Default to jpeg if not an image type

    b64 = base64.b64encode(resp.content).decode()
    data_uri = f"data:{mime};base64,{b64}"

    return data_uri


class WhatsAppAgent(ABC):
    @abstractmethod
    async def handle_message(self, request: Request) -> str: ...


class WhatsAppAgentTwilio(WhatsAppAgent):
    def __init__(self) -> None:
        if not (TWILIO_AUTH_TOKEN and TWILIO_ACCOUNT_SID):
            raise ValueError("Twilio credentials are not configured")
        # TODO: Uncomment when LangGraph server is ready
        # self.agent = Agent()
        pass

    async def handle_message(self, request: Request) -> str:
        form = await request.form()

        sender  = form.get("From", "").strip()
        content = form.get("Body", "").strip()

        if not sender:
            raise HTTPException(400, detail="Missing 'From' in request form")

        LOGGER.info(f"\nReceived message:\nFrom {sender}\nBody: {content}\n")

        # Collect ALL images (you'll forward only the first one for now)
        images = []

        for i in range(int(form.get("NumMedia", "0"))):
            ctype = form.get(f"MediaContentType{i}", "")
            url   = form.get(f"MediaUrl{i}", "")

            # IMAGE
            if url and ctype.startswith("image/"):
                try:
                    LOGGER.info(f"\nDownloading image #{i}")
                    LOGGER.info(f'Url: "{url}"')
                    LOGGER.info(f'Content type: "{ctype}"')

                    images.append({
                        "url": url,
                        "data_uri": twilio_url_to_data_uri(url, ctype),
                    })
                except Exception as err:
                    LOGGER.error("Failed to download image %s: %s", url, err)

            # AUDIO
            elif url and ctype.startswith("audio/"):
                try:
                    LOGGER.info(f"\nDownloading audio #{i}")
                    LOGGER.info(f'Url: "{url}"')
                    LOGGER.info(f'Content type: "{ctype}"')

                    # transcribe audio
                    transcription = transcribe_audio(url, is_url=True)

                    LOGGER.info(f"\nTranscription:\n{transcription}")
                except Exception as err:
                    LOGGER.error("Failed to download audio %s: %s", url, err)

        # TODO: Uncomment when LangGraph server is ready
        # # Assemble payload for the LangGraph agent
        # input_data = {
        #     "id": sender,
        #     "user_message": content,
        # }
        # if images:
        #     # Pass all images to the agent
        #     input_data["images"] = [
        #         {"image_url": {"url": img["data_uri"]}} for img in images
        #     ]
        # 
        # reply = await self.agent.invoke(**input_data)

        # Temporary response without LangGraph
        reply = f"Received your message: {content}\nLangGraph integration coming soon!"

        LOGGER.info(f"\nReplying to {sender}")
        LOGGER.info(f'Body: "{reply}"')

        twiml = MessagingResponse()
        twiml.message(reply)

        LOGGER.info(f"\nOriginal form data:")
        LOGGER.info(form)

        LOGGER.info("\n- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")

        return str(twiml)
