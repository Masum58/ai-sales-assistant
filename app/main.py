import os
# .env ফাইল থেকে secret values পড়ার জন্য
# যেমন — MASUM_PHONE_NUMBER, API keys

import json
# Twilio থেকে আসা data JSON format এ থাকে
# json.loads() দিয়ে সেটা Python এ পড়া হয়

import base64
# Twilio audio কে directly bytes হিসেবে পাঠায় না
# base64 format এ encode করে পাঠায় (text হিসেবে)
# base64.b64decode() দিয়ে সেটা আবার real audio bytes এ ফেরানো হয়

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
# FastAPI = এই পুরো server টা চালানোর framework
# Request = HTTP request এর তথ্য পড়ার জন্য (যেমন — কোন host থেকে এলো)
# WebSocket = ফোনের audio real-time পাঠানোর জন্য live connection
# WebSocketDisconnect = WebSocket হঠাৎ বন্ধ হলে সেটা ধরার জন্য

from fastapi.responses import HTMLResponse
# Twilio XML response পাঠানোর জন্য
# Twilio শুধু XML বোঝে, তাই HTMLResponse দিয়ে XML পাঠাতে হয়

from twilio.twiml.voice_response import VoiceResponse, Dial, Start, Stream
# VoiceResponse = Twilio কে instruction দেওয়ার জন্য XML বানায়
# Dial = ফোন কাউকে forward করার instruction
# Start = audio streaming শুরু করার instruction
# Stream = কোথায় audio পাঠাবে সেটা বলার instruction

from dotenv import load_dotenv
# .env ফাইল থেকে সব secret values পড়ে
# memory তে রাখে যাতে os.getenv() দিয়ে পাওয়া যায়

from app.utils.logger import logger
# পুরো project এর shared logger
# console এ print করে এবং file এ save করে

from app.services.deepgram_service import deepgram_service
# আগের ফাইল — audio শুনে text বানায়
# ওই ফাইলের শেষে বানানো ready object টা এখানে import করা হচ্ছে

from app.services.openai_service import openai_service
# OpenAI (ChatGPT) এর সাথে কথা বলার service
# transcript পাঠালে AI insight দেয়

from app.services.crm_service import crm_service
# CRM (Customer Relationship Management) service
# customer এর তথ্য save/read করার জন্য
# (এই ফাইলে import করা হয়েছে কিন্তু এখনো use করা হয়নি)

# ======================================================

load_dotenv()
# .env ফাইল টা পড়ো এবং সব values memory তে রাখো
# এই লাইন না থাকলে os.getenv() কিছুই পাবে না

app = FastAPI()
# FastAPI server তৈরি করছে
# এই "app" object এ সব routes (URL) জুড়ে দেওয়া হবে

# ======================================================

MASUM_PHONE_NUMBER = os.getenv("MASUM_PHONE_NUMBER")
# .env থেকে Masum এর ফোন নম্বর পড়ছে
# ফোন কল আসলে এই নম্বরে forward করা হবে
# সরাসরি code এ নম্বর না লিখে .env এ রাখা হয়েছে —
#   কারণ code GitHub এ গেলে নম্বর expose হয়ে যেতো

# ======================================================

@app.get("/")
async def root():
# "/" URL এ GET request আসলে এই function চলে
# মানে browser এ গিয়ে server এর address লিখলে এটা দেখাবে
# শুধু check করার জন্য — server চলছে কিনা
#
# Output → {"message": "InsureFlow AI Copilot Server is Running"}

    return {"message": "InsureFlow AI Copilot Server is Running"}

# ======================================================

@app.post("/incoming-call")
async def incoming_call(request: Request):
# "/incoming-call" URL এ POST request আসলে এই function চলে
# কে call করে?
#   Twilio — কেউ ফোন করলে Twilio এই URL এ request পাঠায়
#   বলে — "একটা call এসেছে, কী করবো?"
#   এই function Twilio কে XML দিয়ে বলে — "এই কাজগুলো করো"

    logger.info("Incoming call received for Copilot mode")
    # Output → "Incoming call received for Copilot mode" log এ লেখে

    response = VoiceResponse()
    # Twilio কে instruction দেওয়ার জন্য একটা খালি XML তৈরি করছে
    # এরপর এই XML এ একটা একটা করে instruction যোগ করা হবে

    host = request.headers.get("host")
    # request.headers = HTTP request এর header তথ্য
    # "host" = এই server এর address (যেমন — abc.ngrok.io)
    # এটা দরকার কারণ WebSocket URL বানাতে হবে
    # যেমন — wss://abc.ngrok.io/media-stream

    start = Start()
    start.stream(url=f"wss://{host}/media-stream", track="both_tracks")
    # Start() = Twilio কে বলছি — "audio streaming শুরু করো"
    # .stream(url=...) = কোথায় audio পাঠাবে সেই URL
    #   wss:// = WebSocket Secure connection
    #   /media-stream = নিচে যে WebSocket route আছে সেখানে
    # track="both_tracks" = দুইজনের কথাই পাঠাও
    #   শুধু "inbound_track" দিলে শুধু customer এর কথা আসতো
    #   "both_tracks" মানে customer + Masum দুইজনেরটাই আসবে

    response.append(start)
    # XML এ এই instruction যোগ করলাম

    dial = Dial()
    dial.number(MASUM_PHONE_NUMBER)
    response.append(dial)
    # Dial() = ফোন কাউকে forward করার instruction
    # .number(MASUM_PHONE_NUMBER) = Masum এর নম্বরে forward করো
    # মানে — customer ফোন করলে সেটা Masum এর ফোনে যাবে
    # এবং একই সাথে audio আমাদের server এও আসতে থাকবে

    logger.info(f"Bridging call to Masum at {MASUM_PHONE_NUMBER}")
    # Output → "Bridging call to Masum at +8801XXXXXXXX" log এ লেখে

    return HTMLResponse(content=str(response), status_code=200, media_type="application/xml")
    # str(response) = XML instruction টা string এ convert করে
    # media_type="application/xml" = Twilio বুঝতে পারে এটা XML
    # Twilio এই XML পড়ে কাজ করে

# ======================================================

@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
# "/media-stream" এ WebSocket connection আসলে এই function চলে
# কে connect করে?
#   Twilio — incoming-call থেকে পাওয়া URL এ connect করে
#   এবং real-time audio পাঠাতে থাকে
#
# WebSocket কেন? HTTP নয় কেন?
#   HTTP = request করো → response পাও → connection শেষ
#   WebSocket = connection খোলা থাকে, দুইদিক থেকে data আসা যাওয়া করে
#   ফোনের audio real-time পাঠাতে হলে connection খোলা রাখতে হবে

    await websocket.accept()
    # Twilio এর connection টা accept করলাম
    # এটা না করলে connection হবে না

    logger.info("Twilio Media Stream connected (Copilot Mode)")
    # Output → "Twilio Media Stream connected (Copilot Mode)" log এ লেখে

    stream_sid = None
    # stream_sid = এই নির্দিষ্ট stream এর unique ID
    # Twilio "start" event এ পাঠাবে, তখন save করা হবে
    # এখন None কারণ এখনো পাওয়া যায়নি

    conversation_history = []
    # AI কে context দেওয়ার জন্য কথোপকথনের ইতিহাস রাখা হচ্ছে
    # প্রতিটা transcript এখানে যোগ হবে
    # AI পরের insight দেওয়ার সময় এই ইতিহাস দেখবে

    # --------------------------------------------------

    async def on_transcript(transcript):
    # এই function টা deepgram_service কে দেওয়া হবে
    # Deepgram যখনই কথা text এ convert করবে, এখানে পাঠাবে
    # (আগের ফাইলে on_transcript হিসেবে এটাই "বাইরে থেকে দেওয়া function")

        nonlocal conversation_history
        # conversation_history বাইরের variable
        # nonlocal না লিখলে এই function এর ভেতরে সেটা change করা যাবে না

        logger.info(f"User/Salesperson said: {transcript}")
        # Output → "User/Salesperson said: Hello I want insurance" log এ লেখে

        prompt = f"""
        You are a Sales Copilot for Masum. 
        Listen to the following transcript and provide a brief helpful insight for the salesperson.
        If a vehicle is mentioned, remind Masum about its features.
        If customer details are missing, suggest asking for them.
        Transcript: {transcript}
        """
        # AI কে কী role দিতে চাই সেটা define করছে
        # transcript টা এখানে inject করা হচ্ছে
        # কিন্তু নিচে দেখো — এই prompt আসলে use হচ্ছে না (bug আছে)

        insight = await openai_service.generate_response(transcript, conversation_history)
        # openai_service কে transcript পাঠাচ্ছে
        # conversation_history = আগের কথাবার্তার context
        # insight = AI এর দেওয়া suggestion
        #
        # সমস্যা — উপরের prompt বানানো হলো কিন্তু এখানে পাঠানো হলো না
        # শুধু transcript পাঠানো হচ্ছে, তাই AI সঠিক role এ নেই
        # এটা সম্ভবত একটা bug

        print(f"\n[AI INSIGHT FOR MASUM]: {insight}\n")
        # Masum এর dashboard এ দেখানোর জন্য console এ print করছে
        # এখন শুধু console এ, পরে real dashboard এ যাবে

        conversation_history.append({"role": "user", "content": transcript})
        # পরের AI call এর জন্য এই transcript টা history তে রাখছে
        # {"role": "user"} মানে এটা customer/salesperson এর কথা

    # --------------------------------------------------

    await deepgram_service.start_transcription(on_transcript)
    # Deepgram connection চালু করছে
    # on_transcript function টা দিয়ে দিচ্ছে —
    #   "কথা পেলে এই function এ পাঠাও"
    # এর পর থেকে send_audio() দিয়ে audio পাঠালেই transcript আসবে

    # --------------------------------------------------

    try:
        while True:
        # অনন্তকাল loop চলবে
        # প্রতিটা iteration এ Twilio থেকে একটা message আসবে
        # break বা exception ছাড়া loop থামবে না

            data = await websocket.receive_text()
            # Twilio থেকে আসা data পড়ছে
            # await মানে — data না আসা পর্যন্ত অপেক্ষা করো
            # কিন্তু অপেক্ষার সময় অন্য কাজ বন্ধ থাকবে না (asyncio)

            packet = json.loads(data)
            # data টা JSON string, সেটা Python dict এ convert করছে
            # যেমন — '{"event": "media", "media": {...}}' → dict হয়

            if packet["event"] == "start":
            # Twilio প্রথমে "start" event পাঠায়
            # মানে — "streaming শুরু হলো, এই stream এর ID হলো..."

                stream_sid = packet["start"]["streamSid"]
                # stream এর unique ID save করছে
                logger.info(f"Stream started: {stream_sid}")
                # Output → "Stream started: MZ1234..." log এ লেখে

            elif packet["event"] == "media":
            # প্রতিটা audio chunk এর সাথে "media" event আসে
            # এটাই সবচেয়ে বেশি আসে — কথা বলার সময় প্রতি সেকেন্ডে অনেকবার

                payload = packet["media"]["payload"]
                # payload = base64 encoded audio data (text হিসেবে আছে)

                raw_audio = base64.b64decode(payload)
                # base64 decode করে real audio bytes এ ফেরানো হচ্ছে

                deepgram_service.send_audio(raw_audio)
                # সেই audio bytes Deepgram এ পাঠানো হচ্ছে
                # Deepgram শুনে on_transcript কে text দেবে

            elif packet["event"] == "stop":
            # ফোন কল শেষ হলে Twilio "stop" event পাঠায়

                logger.info(f"Stream stopped: {stream_sid}")
                # Output → "Stream stopped: MZ1234..." log এ লেখে
                break
                # loop থেকে বের হয়ে যাও

    except WebSocketDisconnect:
    # হঠাৎ internet গেলে বা Twilio disconnect করলে এখানে আসে
        logger.info("WebSocket disconnected")
        # Output → "WebSocket disconnected" log এ লেখে

    except Exception as e:
    # অন্য যেকোনো unexpected error এখানে ধরা পড়বে
        logger.error(f"WebSocket error: {e}")
        # Output → "WebSocket error: ..." log এ লেখে

    finally:
    # try এর যেভাবেই শেষ হোক — finally সবসময় চলে
    # break হোক, disconnect হোক, error হোক — সবক্ষেত্রেই

        deepgram_service.stop_transcription()
        # Deepgram connection বন্ধ করো
        # না করলে connection আটকে থাকবে, charge হতে থাকবে

# ======================================================

if __name__ == "__main__":
# এই ফাইল সরাসরি run করলে এই block চলে
# অন্য ফাইল থেকে import হলে এই block চলে না
#
# যেমন — "python main.py" দিলে চলবে
# কিন্তু "from main import app" করলে চলবে না

    import uvicorn
    # uvicorn = FastAPI server চালানোর tool

    uvicorn.run(app, host="0.0.0.0", port=5050)
    # app = উপরে বানানো FastAPI app
    # host="0.0.0.0" = যেকোনো IP থেকে access করা যাবে
    #   "127.0.0.1" দিলে শুধু নিজের computer থেকে যেতো
    # port=5050 = এই port এ server চলবে
    #   মানে http://localhost:5050 তে server পাওয়া যাবে

# ======================================================
# 🔗 পুরো flow এক নজরে —
#
# কেউ ফোন করে (Twilio নম্বরে)
#         ↓
# Twilio → POST /incoming-call এ request পাঠায়
#         ↓
# incoming_call() → XML বানায়:
#   ১. audio streaming শুরু করো → wss://.../media-stream এ
#   ২. Masum এর নম্বরে forward করো
#         ↓
# Twilio → Masum এর ফোনে ring করে (customer কথা বলতে পারে)
# Twilio → একই সাথে WebSocket /media-stream এ connect করে
#         ↓
# media_stream() চালু হয়
#   → Deepgram connection শুরু হয়
#         ↓
# Twilio প্রতিটা audio chunk পাঠায় ("media" event)
#   → Deepgram এ পাঠানো হয়
#   → Deepgram text বানায়
#   → on_transcript() চলে
#   → AI insight দেয়
#   → Console এ print হয়
#         ↓
# ফোন কল শেষ ("stop" event)
#   → Deepgram বন্ধ হয়