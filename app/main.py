import os
import json
import base64
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Dial, Start, Stream
from dotenv import load_dotenv

from app.utils.logger import logger
from app.services.deepgram_service import deepgram_service
from app.services.openai_service import openai_service
from app.services.crm_service import crm_service

load_dotenv()

app = FastAPI()

# Configuration
MASUM_PHONE_NUMBER = os.getenv("MASUM_PHONE_NUMBER")

@app.get("/")
async def root():
    return {"message": "InsureFlow AI Copilot Server is Running"}

@app.post("/incoming-call")
async def incoming_call(request: Request):
    logger.info("Incoming call received for Copilot mode")
    
    response = VoiceResponse()
    
    # 1. Start streaming the audio to our server
    host = request.headers.get("host")
    start = Start()
    start.stream(url=f"wss://{host}/media-stream", track="both_tracks")
    response.append(start)
    
    # 2. Bridge the call to Masum
    dial = Dial()
    dial.number(MASUM_PHONE_NUMBER)
    response.append(dial)
    
    logger.info(f"Bridging call to Masum at {MASUM_PHONE_NUMBER}")
    return HTMLResponse(content=str(response), status_code=200, media_type="application/xml")

@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("Twilio Media Stream connected (Copilot Mode)")
    
    stream_sid = None
    conversation_history = []

    async def on_transcript(transcript):
        nonlocal conversation_history
        
        logger.info(f"User/Salesperson said: {transcript}")
        
        # In Copilot mode, the AI doesn't talk. It provides INSIGHTS.
        prompt = f"""
        You are a Sales Copilot for Masum. 
        Listen to the following transcript and provide a brief helpful insight for the salesperson.
        If a vehicle is mentioned, remind Masum about its features.
        If customer details are missing, suggest asking for them.
        Transcript: {transcript}
        """
        
        insight = await openai_service.generate_response(transcript, conversation_history)
        
        # Log the insight for Masum to see on his dashboard (console for now)
        print(f"\n[AI INSIGHT FOR MASUM]: {insight}\n")
        
        # Update history for context
        conversation_history.append({"role": "user", "content": transcript})

    # Start Deepgram for this session
    await deepgram_service.start_transcription(on_transcript)

    try:
        while True:
            data = await websocket.receive_text()
            packet = json.loads(data)

            if packet["event"] == "start":
                stream_sid = packet["start"]["streamSid"]
                logger.info(f"Stream started: {stream_sid}")
            elif packet["event"] == "media":
                payload = packet["media"]["payload"]
                raw_audio = base64.b64decode(payload)
                deepgram_service.send_audio(raw_audio)
            elif packet["event"] == "stop":
                logger.info(f"Stream stopped: {stream_sid}")
                break
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        deepgram_service.stop_transcription()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)
