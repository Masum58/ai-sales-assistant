import os
import asyncio
from deepgram import DeepgramClient
from deepgram.clients.live.v1 import LiveOptions
from deepgram.clients.live.v1.events import LiveTranscriptionEvents
from app.utils.logger import logger

class DeepgramService:
    def __init__(self):
        self.client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
        self.connection = None

    async def start_transcription(self, on_transcript):
        logger.info("Starting Deepgram transcription")
        self.connection = self.client.listen.live.v("1")

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) > 0 and result.speech_final:
                logger.info(f"Transcript: {sentence}")
                asyncio.create_task(on_transcript(sentence))

        def on_error(self, error, **kwargs):
            logger.error(f"Deepgram error: {error}")

        self.connection.on(LiveTranscriptionEvents.Transcript, on_message)
        self.connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="mulaw",
            sample_rate=8000,
        )

        self.connection.start(options)

    def send_audio(self, audio_payload):
        if self.connection:
            self.connection.send(audio_payload)

    def stop_transcription(self):
        if self.connection:
            self.connection.finish()
            self.connection = None

deepgram_service = DeepgramService()
