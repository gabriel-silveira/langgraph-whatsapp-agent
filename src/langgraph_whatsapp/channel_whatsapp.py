import logging
from typing import Dict, Any
from fastapi import Request, HTTPException
from src.langgraph_whatsapp.channel_twilio import WhatsAppAgent
from src.langgraph_whatsapp.agent import Agent
from src.langgraph_whatsapp.config import WHATSAPP_VERIFY_TOKEN, WHATSAPP_API_TOKEN

LOGGER = logging.getLogger("whatsapp")

class WhatsAppBusinessAgent(WhatsAppAgent):
    def __init__(self) -> None:
        self.agent = Agent()

    async def handle_message(self, request: Request) -> Dict[str, Any]:
        try:
            # Parse webhook data
            webhook_data = await request.json()
            
            # Validate webhook object type
            if webhook_data.get("object") != "whatsapp_business_account":
                raise HTTPException(400, "Invalid webhook object type")

            # Get first entry and change
            entries = webhook_data.get("entry", [])
            if not entries:
                raise HTTPException(400, "No entries in webhook data")

            entry = entries[0]
            changes = entry.get("changes", [])
            if not changes:
                raise HTTPException(400, "No changes in webhook entry")

            change = changes[0]
            value = change.get("value", {})

            # Validate it's a WhatsApp message
            if value.get("messaging_product") != "whatsapp":
                raise HTTPException(400, "Invalid messaging product")

            # Get message metadata
            metadata = value.get("metadata", {})
            phone_number = metadata.get("display_phone_number")
            phone_number_id = metadata.get("phone_number_id")

            # Process messages
            messages = value.get("messages", [])
            if not messages:
                # This might be a status update webhook, just acknowledge
                return {"status": "success", "message": "Status update received"}

            message = messages[0]
            message_type = message.get("type")
            sender = message.get("from")

            if not sender:
                raise HTTPException(400, "Missing sender information")

            # Extract message content based on type
            content = ""
            images = []

            if message_type == "text":
                content = message.get("text", {}).get("body", "")
            elif message_type == "image":
                image = message.get("image", {})
                if image:
                    image_id = image.get("id")
                    if image_id:
                        # Here you would implement media download using the WhatsApp Cloud API
                        # GET /v17.0/{image-id}
                        # Authorization: Bearer {WHATSAPP_API_TOKEN}
                        images.append({
                            "url": f"https://graph.facebook.com/v17.0/{image_id}",
                            "data_uri": None
                        })

            # Prepare input for LangGraph agent
            input_data = {
                "id": sender,
                "user_message": content,
                "metadata": {
                    "phone_number": phone_number,
                    "phone_number_id": phone_number_id,
                    "message_id": message.get("id"),
                    "timestamp": message.get("timestamp")
                }
            }

            if images:
                input_data["images"] = [
                    {"image_url": {"url": img["url"]}} for img in images
                ]

            # Process with LangGraph agent
            reply = await self.agent.invoke(**input_data)

            # Format response for WhatsApp Cloud API
            # POST https://graph.facebook.com/v17.0/{phone-number-id}/messages
            return {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": sender,
                "type": "text",
                "text": {"body": reply}
            }

        except Exception as e:
            LOGGER.exception("Error processing WhatsApp webhook")
            raise HTTPException(500, str(e))
