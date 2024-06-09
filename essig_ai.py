import google.generativeai as genai
from functools import wraps
import time

class ChatBotError(Exception):
    """Exception de base pour les erreurs de ChatBot."""
    pass

class ChatSessionError(ChatBotError):
    """Exception levée lorsque la session de chat ne peut pas être initialisée."""
    pass

class ChatBot:
    def __init__(self, api_key, model_name="gemini-1.5-flash"):
        try:
            # Configurer l'API Gemini avec la clé API
            genai.configure(api_key=api_key)

            # Initialiser le modèle génératif avec le nom du modèle
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 1,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain",
                }
            )
            self.chat_session = None  # Initialiser la session de chat
        except Exception as e:
            raise ChatBotError(f"Erreur lors de l'initialisation de ChatBot: {str(e)}")

    def retry_on_failure(retries=3, delay=2, backoff=2):
        """Décorateur pour réessayer une fonction en cas d'échec."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                attempts = 0
                while attempts < retries:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempts += 1
                        time.sleep(delay * backoff ** attempts)
                        if attempts == retries:
                            raise e
            return wrapper
        return decorator

    @retry_on_failure()
    def start_chat_session(self, prompt="Bonjour Gemini, j'ai besoin de vous aider."):
        try:
            self.chat_session = self.model.start_chat(
                history=[
                    {
                        "role": "user",  # Rôle de l'utilisateur dans la conversation
                        "parts": [""],  # Message initial de l'utilisateur, vide pour commencer
                    },
                    {
                        "role": "model",  # Rôle du modèle dans la conversation
                        "parts": [""],  # Réponse initiale du modèle, vide pour commencer
                    },
                ]
            )
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            raise ChatSessionError(f"Erreur lors de la création de la session de chat: {str(e)}")

    @retry_on_failure()
    def send_message(self, message):
        if self.chat_session is None:
            self.start_chat_session()
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            raise ChatBotError(f"Erreur lors de l'envoi du message: {str(e)}")

   