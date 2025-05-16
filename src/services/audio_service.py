import requests, time, logging
from openai import OpenAI, RateLimitError, APIError, APIConnectionError
from langgraph_whatsapp.config import OPENAI_API_KEY, TRANSCRIBE_MODEL, NLP_MODEL, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

LOGGER = logging.getLogger("whatsapp")

llm = OpenAI(api_key=OPENAI_API_KEY)


def transcribe_audio(audio_source: str, is_url: bool = False, retries: int = 3) -> str:
    """
    Transcreve áudio para texto usando o OpenAI.
    """
    # Download do áudio apenas uma vez, fora do loop de retry
    try:
        if is_url:
            try:
                response = requests.get(
                    audio_source,
                    auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                )
                response.raise_for_status()
                audio_bytes = response.content
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Failed to request audio URL: {e}")
        else:
            try:
                with open(audio_source, "rb") as f:
                    audio_bytes = f.read()
            except FileNotFoundError:
                raise ValueError(f"Audio file not found: {audio_source}")

        # Prepara o arquivo para envio à API
        from io import BytesIO
        audio_file = BytesIO(audio_bytes)
        audio_file.name = "audio.ogg"  # Nome necessário para o multipart/form-data

        # Loop de retry apenas para a transcrição
        for i in range(retries):
            try:
                transcription = llm.audio.transcriptions.create(
                    model=TRANSCRIBE_MODEL,
                    file=audio_file,
                    response_format="text"
                )
                # Quando response_format="text", a API retorna diretamente uma string
                return transcription.strip()

            except RateLimitError as e:
                if "insufficient_quota" in str(e):
                    LOGGER.error("OpenAI API quota exceeded. Please check your billing status.")
                    raise Exception("OpenAI API quota exceeded. Please check your billing status.") from e
                
                if i < retries - 1:  # Não espera na última tentativa
                    wait = 2 ** i
                    LOGGER.warning(f"Rate limit exceeded. Retrying in {wait} seconds...")
                    time.sleep(wait)
                    audio_file.seek(0)  # Reset do ponteiro do arquivo para nova tentativa
                else:
                    raise
            except (APIError, APIConnectionError) as e:
                if i < retries - 1:
                    wait = 2 ** i
                    LOGGER.warning(f"API error: {str(e)}. Retrying in {wait} seconds...")
                    time.sleep(wait)
                    audio_file.seek(0)
                else:
                    raise

    except Exception as e:
        LOGGER.error(f"Failed to transcribe audio {audio_source}: {str(e)}")
        raise Exception(f"Failed to transcribe audio: {str(e)}")


def generate_response(transcribed_text: str, user_context: str = None) -> str:
    """
    Gera uma resposta baseada no texto transcrito.
    """
    prompt = f"Mensagem do cliente: {transcribed_text}\n"

    if user_context:
        prompt += f"Contexto do cliente: {user_context}\n"
    prompt += "\nResponda de forma clara e objetiva como um atendente de suporte."

    response = llm.chat.completions.create(
        model=NLP_MODEL,
        messages=[
            {"role": "system", "content": "Você é um atendente de suporte ao cliente."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()
