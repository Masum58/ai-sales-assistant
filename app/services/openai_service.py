import os
from openai import OpenAI
from app.utils.logger import logger

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """
        You are an expert AI Sales Assistant for an Auto Dealership called "InsureFlow Auto".
        Your goal is to be helpful, professional, and friendly.
        
        Key Responsibilities:
        1. Answer questions about car inventory (say we have SUVs and Sedans).
        2. Schedule test drives and appointments.
        3. Collect customer information (Name, Phone Number, and car of interest).
        
        Guidelines:
        - Keep responses concise and natural for voice conversation.
        - Don't use bullet points.
        - Always encourage booking an appointment.
        """

    async def generate_response(self, transcript, history=[]):
        try:
            logger.info("Generating OpenAI response")
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": transcript})

            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )

            response_text = completion.choices[0].message.content
            logger.info(f"OpenAI Response: {response_text}")
            return response_text
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return "I'm sorry, I'm having trouble. Can you say that again?"

    async def generate_tts(self, text):
        try:
            logger.info("Generating OpenAI TTS")
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
                response_format="pcm"
            )
            # Response.content provides the raw audio bytes
            return response.content
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

openai_service = OpenAIService()
