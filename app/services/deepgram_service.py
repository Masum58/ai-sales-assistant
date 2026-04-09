import os
# os কেন লাগে?
# DEEPGRAM_API_KEY টা directly code এ লেখা যাবে না — security risk
# তাই .env ফাইলে লুকিয়ে রাখা হয়
# os.getenv("DEEPGRAM_API_KEY") দিয়ে সেখান থেকে পড়া হয়

import asyncio
# asyncio কেন লাগে?
# এই project এ একসাথে ৩টা কাজ চলে —
#   ১. ফোন থেকে audio আসছে (সবসময়)
#   ২. সেই audio Deepgram এ পাঠানো হচ্ছে (সবসময়)
#   ৩. Deepgram থেকে text আসলে সেটা process হচ্ছে
# এই ৩টা কাজ যদি একটার পর একটা হতো —
#   audio আসা বন্ধ থাকতো যতক্ষণ text process হয়
#   মানে কথার মাঝে মাঝে gap পড়ে যেতো
# asyncio দিয়ে এই ৩টা কাজ "একসাথে" চলে, কেউ কাউকে আটকায় না

from deepgram import DeepgramClient
# Deepgram এর official Python library থেকে DeepgramClient আনছি
# এটা দিয়ে Deepgram এর server এর সাথে কথা বলা যায়

from deepgram.clients.live.v1 import LiveOptions
# LiveOptions = live transcription এর settings একসাথে রাখার জন্য
# যেমন — কোন language, কোন model, কোন audio format ইত্যাদি

from deepgram.clients.live.v1.events import LiveTranscriptionEvents
# LiveTranscriptionEvents = Deepgram এর বিভিন্ন "ঘটনার" নাম
# যেমন — Transcript (কথা পাওয়া গেছে), Error (সমস্যা হয়েছে)
# এগুলো দিয়ে বলা হয় — "এই ঘটনা হলে এই function চালাও"

from app.utils.logger import logger
# logger = অন্য একটা ফাইল (app/utils/logger.py) থেকে আনা
# কাজের তথ্য console এ print করে এবং file এ save করে
# যেমন — কখন connection হলো, কী transcript আসলো, কোনো error হলো
# এটা অন্য ফাইল থেকে আনার কারণ —
#   logger টা পুরো project এ একই জায়গা থেকে ব্যবহার হয়
#   প্রতি ফাইলে নতুন করে logger বানালে সব আলাদা আলাদা হয়ে যেতো

# ======================================================

class DeepgramService:
# class মানে একটা "ব্লুপ্রিন্ট" বা "ছাঁচ"
# Deepgram এর সাথে সম্পর্কিত সব কাজ এই একটা জায়গায় রাখা হয়েছে
# বাইরের ফাইল শুধু এই class ব্যবহার করবে —
#   Deepgram কীভাবে কাজ করে সেটা জানতে হবে না

    def __init__(self):
    # __init__ = class এর "জন্মের মুহূর্ত"
    # যখনই DeepgramService() লেখা হবে, এই function আগে চলে
    # এখানে শুধু প্রাথমিক setup হয়, connection হয় না

        self.client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
        # os.getenv("DEEPGRAM_API_KEY") → .env ফাইল থেকে API key পড়ছে
        # DeepgramClient(key) → সেই key দিয়ে Deepgram এ "login" করছে
        # self.client → এই login টা save করে রাখছে
        #   পরে যখনই connection লাগবে, এই client ব্যবহার হবে

        self.connection = None
        # None মানে এখন কোনো connection নেই
        # connection তৈরি হবে নিচের start_transcription() function এ
        # যখন কেউ ফোন করবে, তখন start_transcription() call হবে
        # সেখানে self.connection = self.client.listen.live.v("1") লাইনে
        # None থেকে real connection এ পরিণত হবে
        #
        # None রাখার কারণ —
        # send_audio() আর stop_transcription() এ
        # "if self.connection:" দিয়ে check করা হয়
        # যদি connection না থাকে (None), তাহলে কোনো কাজ করবে না
        # crash হবে না

# ======================================================

    async def start_transcription(self, on_transcript):
    # এই function টা Deepgram এর সাথে LIVE connection খোলে
    # async মানে — এই function চলার সময় অন্য কাজও চলতে পারবে
    #
    # on_transcript কী?
    # এই function টা নিজে জানে না — কথা শুনলে কী করতে হবে
    # সেটা অন্য ফাইল (যেমন websocket_handler.py) ঠিক করে দেয়
    #
    # উদাহরণ —
    # websocket_handler.py তে লেখা থাকে:
    #
    #   async def handle_transcript(text):
    #       ai_response = await gpt.ask(text)   ← AI কে পাঠাও
    #       await call.speak(ai_response)        ← ফোনে বলো
    #
    #   await deepgram_service.start_transcription(handle_transcript)
    #                                         ↑
    #                          এই function টা "on_transcript" হিসেবে আসে
    #
    # মানে deepgram_service শুধু text বানায়
    # সেই text দিয়ে কী করবে — সেটা বাইরের ফাইল ঠিক করে দেয়

        logger.info("Starting Deepgram transcription")
        # Output → "Starting Deepgram transcription" log এ লেখে
        # মানে জানান দিচ্ছে — connection শুরু হতে যাচ্ছে

        self.connection = self.client.listen.live.v("1")
        # self.client = Deepgram এ আগেই login করা আছে (API key দিয়ে)
        # .listen = "আমি audio শুনতে চাই" বলছে
        # .live = "recorded file না, real-time live audio শুনবো" বলছে
        # .v("1") = Deepgram এর version 1 API ব্যবহার করবো
        #
        # এই পুরো লাইনটা মূলত —
        # Deepgram এর server এর সাথে একটা "খোলা দরজা" তৈরি করে
        # এই দরজা দিয়ে audio ঢুকবে, text বের হবে
        # এই দরজাটাই self.connection এ save হলো
        # (আগে None ছিলো, এখন real connection হলো)

        # --------------------------------------------------

        def on_message(self, result, **kwargs):
        # Deepgram প্রতিটা audio chunk শুনে এখানে result পাঠায়
        # result এর ভেতরে অনেক কিছু থাকে, structure টা এরকম —
        #
        # result = {
        #   channel: {
        #     alternatives: [          ← একাধিক অনুবাদ থাকতে পারে
        #       { transcript: "Hello", confidence: 0.99 },  ← সবচেয়ে confident
        #       { transcript: "Helo",  confidence: 0.70 },  ← কম confident
        #       { transcript: "Yello", confidence: 0.40 },  ← আরো কম
        #     ]
        #   },
        #   speech_final: True/False   ← কথা বলা শেষ হয়েছে কিনা
        # }

            sentence = result.channel.alternatives[0].transcript
            # result.channel          → audio channel এ যাও
            # .alternatives           → সব সম্ভাব্য অনুবাদের list
            # [0]                     → index 0 = সবচেয়ে confident অনুবাদটা নাও
            # .transcript             → শুধু text টুকু বের করো
            #
            # মানে Deepgram ৩টা option দিলে, আমরা সবচেয়ে ভালোটাই নিচ্ছি

            if len(sentence) > 0 and result.speech_final:
            # len(sentence) > 0  → sentence খালি না, কিছু একটা আছে
            # result.speech_final → কথা বলা পুরোপুরি শেষ হয়েছে
            #
            # speech_final কেন দরকার?
            # Deepgram কথার মাঝে মাঝেও partial text পাঠায়
            # যেমন "How are" পাঠায়, তারপর "How are you" পাঠায়
            # speech_final = True মানে পুরো কথা শেষ, এখন process করো
            # নাহলে অর্ধেক কথা AI এ পাঠিয়ে দেওয়া হতো

                logger.info(f"Transcript: {sentence}")
                # Output → "Transcript: Hello how are you" log এ লেখে

                asyncio.create_task(on_transcript(sentence))
                # on_transcript(sentence) → বাইরে থেকে দেওয়া function এ text পাঠাচ্ছে
                # asyncio.create_task() কেন?
                #   on_transcript একটা async function
                #   সরাসরি on_transcript(sentence) call করলে চলবে না
                #   create_task() দিয়ে asyncio কে বলছি —
                #   "এই কাজটা background এ চালাও, audio শোনা বন্ধ করো না"

        # --------------------------------------------------

        def on_error(self, error, **kwargs):
        # Deepgram এর সাথে কোনো সমস্যা হলে এই function চলে
        # যেমন — internet গেলে, API key ভুল হলে, server down হলে

            logger.error(f"Deepgram error: {error}")
            # Output → "Deepgram error: ..." log এ লেখে
            # error variable এ সমস্যার বিবরণ থাকে

        # --------------------------------------------------

        self.connection.on(LiveTranscriptionEvents.Transcript, on_message)
        # LiveTranscriptionEvents.Transcript = "কথা পাওয়া গেছে" এই ঘটনার নাম
        # .on(ঘটনা, function) = "এই ঘটনা হলে এই function চালাও" বলছে
        # মানে — Deepgram কথা পেলে on_message চালাবে

        self.connection.on(LiveTranscriptionEvents.Error, on_error)
        # LiveTranscriptionEvents.Error = "সমস্যা হয়েছে" এই ঘটনার নাম
        # মানে — Deepgram এ সমস্যা হলে on_error চালাবে

        # --------------------------------------------------

        options = LiveOptions(
            model="nova-2",
            # Deepgram এর সবচেয়ে accurate এবং fast model
            # পুরনো model গুলো (nova, base) এর চেয়ে অনেক ভালো

            language="en-US",
            # ইংরেজি (আমেরিকান) ভাষা শুনবে
            # এটা না দিলে Deepgram নিজে ভাষা বোঝার চেষ্টা করে — slow হয়

            smart_format=True,
            # True মানে Deepgram নিজে নিজে punctuation বসাবে
            # যেমন "hello how are you" → "Hello, how are you?"
            # সংখ্যা → "one hundred" এর বদলে "100" লিখবে

            encoding="mulaw",
            # mulaw = ফোন কলের audio format (Twilio এই format এ পাঠায়)
            # এটা না দিলে Deepgram audio বুঝতে পারবে না

            sample_rate=8000,
            # ফোনের audio quality = 8000 Hz (8kHz)
            # সাধারণ microphone হলে 16000 বা 44100 হতো
            # কিন্তু ফোন কলের standard হলো 8000
        )

        self.connection.start(options)
        # এই settings দিয়ে Deepgram connection চালু করো
        # এর পরে send_audio() দিয়ে audio পাঠানো শুরু করা যাবে

# ======================================================

    def send_audio(self, audio_payload):
    # ফোন থেকে আসা প্রতিটা audio chunk এই function এ আসে
    # এবং সেটা Deepgram এ পাঠিয়ে দেয়
    #
    # কে call করে?
    # websocket_handler.py — ফোন থেকে audio আসলে এখানে পাঠায়
    # এরকম — deepgram_service.send_audio(audio_data)
    #
    # Output → কোনো output নেই, চুপচাপ audio পাঠায়

        if self.connection:
        # connection আছে কিনা check করছে
        # None হলে কিছু করবে না — crash হবে না
        # (ফোন কল শেষ হওয়ার পরেও audio আসতে পারে, তখন crash না হওয়ার জন্য)

            self.connection.send(audio_payload)
            # audio_payload = ফোন থেকে আসা raw audio bytes
            # .send() দিয়ে সেটা Deepgram এ পাঠানো হচ্ছে
            # Deepgram সেটা শুনে on_message তে transcript পাঠাবে

# ======================================================

    def stop_transcription(self):
    # ফোন কল শেষ হলে এই function call হয়
    # Deepgram connection বন্ধ করে দেয়
    #
    # কে call করে?
    # websocket_handler.py — ফোন কল disconnect হলে এখানে call করে
    # এরকম — deepgram_service.stop_transcription()
    #
    # Output → connection বন্ধ হয়, self.connection আবার None হয়

        if self.connection:
        # connection আছে কিনা check করছে
        # None হলে কিছু করবে না — crash হবে না

            self.connection.finish()
            # Deepgram কে বলছে — "শেষ, আর audio আসবে না, বন্ধ করো"
            # এটা না করলে Deepgram এর server এ connection আটকে থাকতো
            # এবং Deepgram account এ unnecessary charge হতো

            self.connection = None
            # connection টা আবার None করে দিলাম
            # মানে এই object টা আবার "fresh" অবস্থায় ফিরে গেলো
            # পরের ফোন কলের জন্য ready

# ======================================================

deepgram_service = DeepgramService()
# ফাইলের শেষে একটা READY object তৈরি করা হচ্ছে
#
# কেন এখানে বানানো?
# অন্য ফাইল এটা import করে সরাসরি ব্যবহার করতে পারে —
#   from app.services.deepgram_service import deepgram_service
#   await deepgram_service.start_transcription(...)
#
# যদি এখানে না বানাতাম —
#   প্রতিটা ফাইলকে নিজে নিজে DeepgramService() বানাতে হতো
#   তাহলে প্রতিটা আলাদা আলাদা connection তৈরি করতো
#   একটা connection এর অবস্থা অন্যটা জানতো না

# ======================================================
# 🔗 পুরো flow এক নজরে —
#
# ফোন কল আসে (Twilio)
#         ↓
# websocket_handler.py → start_transcription(handle_transcript) call করে
#         ↓
# Deepgram এর সাথে connection তৈরি হয়
#         ↓
# websocket_handler.py → প্রতিটা audio chunk এ send_audio(audio) call করে
#         ↓
# Deepgram audio শুনে on_message তে transcript পাঠায়
#         ↓
# on_transcript(sentence) → websocket_handler এর handle_transcript এ যায়
#         ↓
# AI response তৈরি হয়, ফোনে বলা হয়
#         ↓
# ফোন কল শেষ → stop_transcription() call হয়