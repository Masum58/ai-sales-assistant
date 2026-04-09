import os
# .env ফাইল থেকে OPENAI_API_KEY পড়ার জন্য

from openai import OpenAI
# OpenAI এর official Python library
# এটা দিয়ে ChatGPT এবং TTS (Text-to-Speech) ব্যবহার করা যায়

from app.utils.logger import logger
# পুরো project এর shared logger
# console এ print করে এবং file এ save করে

# ======================================================

class OpenAIService:
# OpenAI এর সাথে সম্পর্কিত সব কাজ এই একটা জায়গায়
# বাইরের ফাইল শুধু এই class ব্যবহার করবে —
#   OpenAI কীভাবে কাজ করে সেটা জানতে হবে না

    def __init__(self):
    # class তৈরি হওয়ার সাথে সাথে এটা চলে
    # এখানে OpenAI তে login এবং AI এর personality set করা হয়

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # os.getenv("OPENAI_API_KEY") → .env থেকে API key পড়ছে
        # OpenAI(api_key=...) → সেই key দিয়ে OpenAI তে "login" করছে
        # self.client → এই login টা save করে রাখছে
        #   পরে ChatGPT বা TTS ব্যবহার করতে এই client লাগবে

        self.system_prompt = """
        You are an expert AI Sales Assistant...
        """
        # system_prompt = AI এর "ব্যক্তিত্ব" বা "role" define করে
        # এটা প্রতিটা AI call এর শুরুতে পাঠানো হয়
        # মানে AI কে বলা হচ্ছে —
        #   "তুমি InsureFlow Auto এর sales assistant"
        #   "তোমার কাজ কী কী"
        #   "কীভাবে কথা বলবে"
        #
        # Keep responses concise → ছোট উত্তর দাও (voice এ বড় উত্তর বিরক্তিকর)
        # Don't use bullet points → বলার সময় bullet point শোনা যায় না
        # Always encourage booking → appointment নেওয়ার দিকে নিয়ে যাও

# ======================================================

    async def generate_response(self, transcript, history=[]):
    # transcript = Deepgram থেকে আসা কথার text
    # history = এই call এ এতক্ষণ যা কথা হয়েছে তার list
    #   history থাকলে AI আগের কথা মনে রেখে উত্তর দিতে পারে
    #   যেমন — আগে নাম বললে পরে আবার জিজ্ঞেস করবে না
    #
    # কে call করে?
    #   main.py এর on_transcript() — transcript আসলেই এখানে পাঠায়
    #   এরকম → insight = await openai_service.generate_response(transcript, history)

        try:
        # try মানে — এই কাজ করার চেষ্টা করো
        # যদি কোনো সমস্যা হয়, except এ যাও (crash করো না)

            logger.info("Generating OpenAI response")
            # Output → "Generating OpenAI response" log এ লেখে

            messages = [{"role": "system", "content": self.system_prompt}]
            # messages = AI কে পাঠানোর জন্য কথোপকথনের list
            # প্রথমে system_prompt দিয়ে শুরু হয়
            # এখন messages এর ভেতরে শুধু একটা item —
            #   [{"role": "system", "content": "তুমি sales assistant..."}]

            messages.extend(history)
            # history = আগের সব কথাবার্তা এখানে যোগ হলো
            # যেমন history তে থাকতে পারে —
            #   {"role": "user", "content": "I want a SUV"}
            #   {"role": "assistant", "content": "Great choice! We have..."}
            # এখন messages এ system + পুরনো কথা আছে

            messages.append({"role": "user", "content": transcript})
            # সবশেষে নতুন transcript টা যোগ হলো
            # এখন messages সম্পূর্ণ —
            #   system prompt + পুরনো কথা + নতুন কথা
            # AI এই পুরো context দেখে উত্তর দেবে

            completion = self.client.chat.completions.create(
                model="gpt-4o",
                # gpt-4o = OpenAI এর সবচেয়ে smart এবং fast model
                # gpt-3.5 এর চেয়ে অনেক ভালো বোঝে, কিন্তু একটু বেশি খরচ

                messages=messages
                # পুরো কথোপকথন AI কে পাঠানো হচ্ছে
            )
            # এই লাইনে OpenAI এর server এ request যায়
            # AI উত্তর বানিয়ে পাঠায়
            # completion এ সেই উত্তর আসে

            response_text = completion.choices[0].message.content
            # completion.choices = AI এর সম্ভাব্য উত্তরের list
            # [0] = প্রথম এবং সবচেয়ে ভালো উত্তরটা নাও
            # .message.content = শুধু text টুকু বের করো
            #
            # choices list কেন?
            # OpenAI একসাথে একাধিক উত্তর বানাতে পারে
            # কিন্তু আমরা n=1 দিইনি তাই default এ ১টাই আসে

            logger.info(f"OpenAI Response: {response_text}")
            # Output → "OpenAI Response: Great choice! We have SUVs..." log এ লেখে

            return response_text
            # AI এর উত্তরটা caller কে ফেরত দাও

        except Exception as e:
        # OpenAI server down, internet না থাকলে, API key ভুল হলে
        # যেকোনো সমস্যায় এখানে আসবে

            logger.error(f"OpenAI error: {e}")
            # Output → "OpenAI error: ..." log এ লেখে

            return "I'm sorry, I'm having trouble. Can you say that again?"
            # সমস্যা হলে এই default উত্তর দাও
            # call টা awkward silence এ শেষ না হয়ে একটা response পাবে

# ======================================================

    async def generate_tts(self, text):
    # TTS = Text-to-Speech → text কে voice এ convert করে
    # text = যা বলতে চাই সেটা string হিসেবে
    #
    # কে call করে?
    #   এই project এ এখনো কোথাও call করা হয়নি
    #   Copilot mode এ AI নিজে কথা বলে না, শুধু insight দেয়
    #   পরে যদি AI নিজে ফোনে কথা বলার feature আসে, তখন use হবে

        try:
            logger.info("Generating OpenAI TTS")
            # Output → "Generating OpenAI TTS" log এ লেখে

            response = self.client.audio.speech.create(
                model="tts-1",
                # tts-1 = OpenAI এর Text-to-Speech model
                # tts-1-hd আছে — আরো ভালো quality কিন্তু slow এবং বেশি খরচ
                # real-time call এ tts-1 ই ভালো কারণ fast

                voice="alloy",
                # alloy = OpenAI এর একটা voice এর নাম
                # অন্য options — echo, fable, onyx, nova, shimmer
                # alloy = neutral এবং professional শোনায়

                input=text,
                # এই text টাকে voice এ convert করো

                response_format="pcm"
                # pcm = raw audio bytes format
                # mp3 বা wav এর মতো compressed না
                # Twilio তে সরাসরি পাঠানোর জন্য pcm দরকার
                # compressed format পাঠালে Twilio আবার decode করতে হতো
            )

            return response.content
            # response.content = raw audio bytes
            # এই bytes সরাসরি Twilio তে পাঠালে ফোনে voice শোনা যাবে

        except Exception as e:
            logger.error(f"TTS error: {e}")
            # Output → "TTS error: ..." log এ লেখে

            return None
            # সমস্যা হলে None ফেরত দাও
            # caller কে বলা যাবে না কিছু — silence হবে
            # তাই পরে এই None check করে handle করতে হবে

# ======================================================

openai_service = OpenAIService()
# ফাইলের শেষে একটা READY object তৈরি
# অন্য ফাইল সরাসরি import করে ব্যবহার করতে পারবে —
#   from app.services.openai_service import openai_service
#   response = await openai_service.generate_response(transcript, history)
#
# প্রতিটা ফাইলে নতুন করে OpenAIService() বানালে —
#   প্রতিটা আলাদা আলাদা client তৈরি হতো
#   অনেক unnecessary connection তৈরি হতো

# ======================================================
# 🔗 পুরো flow এক নজরে —
#
# Deepgram → transcript বানায়
#         ↓
# main.py এর on_transcript() → এখানে পাঠায়
#         ↓
# generate_response(transcript, history)
#   → system prompt + history + transcript একসাথে করে
#   → OpenAI তে পাঠায়
#   → AI insight/response বানায়
#         ↓
# main.py → console এ print করে Masum দেখতে পায়
#         ↓
# (ভবিষ্যতে) generate_tts(response)
#   → text কে voice এ convert করে
#   → Twilio তে পাঠাবে
#   → ফোনে AI এর voice শোনা যাবে