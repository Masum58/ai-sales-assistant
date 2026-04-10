# InsureFlow AI Copilot

An AI-powered real-time Sales Copilot designed for auto dealerships. This system listens to live conversations between a salesperson (Masum) and a customer, providing real-time insights and data-driven assistance using Twilio, Deepgram, and OpenAI.

## 🚀 Features
- **Real-time Call Bridging**: Automatically dials the salesperson when a customer calls the Twilio number.
- **Live Transcription**: High-accuracy, low-latency speech-to-text powered by Deepgram Nova-2.
- **Sales Insights**: Real-time analysis of conversation context using OpenAI GPT-4o.
- **CRM Integration**: Modular structure ready for Onyx CRM integration.

## 🛠️ Tech Stack
- **Backend**: Python, FastAPI
- **Voice**: Twilio (Programmable Voice + Media Streams)
- **STT**: Deepgram SDK
- **LLM**: OpenAI SDK
- **Environment**: Python 3.12+

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Masum58/ai-sales-assistant.git
   cd ai-sales-assistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

## 🏃 Running the Project

1. **Start the FastAPI server**:
   ```bash
   python -m app.main
   ```

2. **Expose locally using Ngrok**:
   ```bash
   ngrok http 5050
   ```

3. **Set Twilio Webhook**:
   Go to your Twilio console and set the "A CALL COMES IN" webhook to:
   `https://your-ngrok-url.app/incoming-call`


## 📖 কাজের ধাপ ও প্রক্রিয়া (Detailed Workflow in Bengali)

এই প্রোজেক্টে মূলত ৩টি ফাইলের মধ্যে যোগাযোগ হয়: `main.py`, `deepgram_service.py` এবং `openai_service.py`। নিচে পুরো প্রক্রিয়ার একটি বিস্তারিত ব্রেকডাউন দেওয়া হলো:

### ধাপ ১: কলার যখন ফোন দেয় (Twilio → `main.py`)
কেউ যখন Twilio নাম্বারে কল করে, Twilio সবার প্রথমে আপনার সার্ভারের `main.py` ফাইলের **`/incoming-call`** রাউটে যোগাযোগ করে জিজ্ঞেস করে, "আমি এখন কী করবো?"
আপনার সিস্টেম তখন Twilio-কে দুটি কাজ করতে বলে:
1. কলটি নির্দিষ্ট সেলসপারসনের (Masum) মোবাইল নাম্বারে ট্রান্সফার (Dial) করে দাও।
2. একই সাথে একটি "WebSocket" কানেকশন (`/media-stream`) তৈরি করে কলের অডিও সার্ভারে পাঠাতে থাকো।

### ধাপ ২: Deepgram কে প্রস্তুত করা (`main.py` → `deepgram_service.py`)
Twilio যখন `/media-stream`-এ কানেক্ট হয়, তখন `main.py` ফাইলে একটি ফাংশন বসে থাকে, যার নাম `on_transcript`। কিন্তু এই ফাংশনটার কাজ শুরু হবে পরে। 
তার আগে `await deepgram_service.start_transcription(on_transcript)` কল করে Deepgram-এর সার্ভারে লগিন করা হয়।

`deepgram_service.py` ফাইলের ভেতরে:
- `DeepgramClient` ব্যবহার করে একটি Live কানেকশন খোলা হয়।
- সেটিংসে বলে দেওয়া হয়: `model="nova-2"`, ভাষা `English`, এবং `sample_rate=8000` (কারণ ফোনের অডিও 8000Hz এ আসে)।
- এখানে বলা হয়, Deepgram যখন নিজে নিজে অডিও থেকে কোনো কথা (Transcript) খুঁজে পাবে, তখন যেন সে ঐ `on_transcript` ফাংশনটিকে সেই কথাটা বুঝিয়ে দেয়।

### ধাপ ৩: অডিও পাঠানো (`main.py` → `deepgram_service.py`)
কল চলার সময়:
- Twilio প্রতি সেকেন্ডে অনেকবার অডিওর ছোট ছোট অংশ (Chunks) পাঠায় আপনার `main.py` ফাইলে। এই অডিওগুলো `base64` ফরমেটে এনকোড করা টেক্সটের মতো আসে। 
- `main.py` সেই টেক্সটকে ডিকোড করে আসল অডিও (raw Bytes) বের করে।
- এরপর `deepgram_service.send_audio(raw_audio)` ফাংশনের মাধ্যমে সেই বাইটসগুলোকে Deepgram-এর মুখে তুলে দেওয়া হয়।

### ধাপ ৪: Deepgram থেকে কথা বের হয়ে আসা (`deepgram_service.py` → `main.py`)
- Deepgram সেই অডিও শুনতে থাকে। `deepgram_service.py` তে চেক করা হয় `if len(sentence) > 0 and result.speech_final:`। এর মানে হলো, Deepgram যখন বুঝতে পারে যে কলার একটা পুরো বাক্য বলা শেষ করেছে, তখনই সে বাক্যটাকে ফাইনাল করে।
- ফাইনাল বাক্যটা পাওয়ার পর সে `on_transcript(sentence)`-কে কল করে বাক্যটা `main.py` এর কাছে পাঠিয়ে দেয়।

### ধাপ ৫: বাক্যটি AI কে দেওয়া (`main.py` → `openai_service.py`)
- কথাটি এখন `main.py`-এর `on_transcript` ফাংশনের হাতে। 
- এই ফাংশনটি এখন কথাটিকে নিয়ে `await openai_service.generate_response(transcript, conversation_history)` কল করে ওপেনএআই-এর কাছে যায়।

`openai_service.py` ফাইলের ভেতরে:
- সেখানে `system_prompt`-এ আগে থেকেই লেখা আছে (Role দেওয়া আছে), *"You are an expert AI Sales Assistant..."*
- আগের কথাবার্তার যদি কিছু হিস্টোরি (history) থাকে, সেটাও যোগ করা হয়।
- সবশেষে এখনকার বলা নতুন কথাটি বসিয়ে پورا প্যাকেটটি `gpt-4o` মডেলের কাছে পাঠানো হয়। 
- ChatGPT (বা GPT-4o) এটি পড়ে বুঝতে পারে যে কী নিয়ে কথা হচ্ছে, এবং সেলসম্যানকে কী বলা উচিত, তার একটা "Insight" বা টিপস সে তৈরি করে ফেরত দেয়।

### ধাপ ৬: লগ (Logs) ও রেজাল্ট 
সবশেষে AI-এর দেওয়া সেই টিপসটি `main.py`-এ ফিরে আসে এবং `print(f"\n[AI INSIGHT FOR MASUM]: {insight}\n")` কোডটি দিয়ে কনসোলে প্রদর্শন করে। সেলসম্যান তখন স্ক্রিনে দেখে বুঝতে পারে যে কাস্টমারকে এখন কী উত্তর দেওয়া উচিত।

পুরো সময়ে কোডের বিভিন্ন অংশে কী ঘটছে তা ট্র্যাক করার জন্য `logger.info()` ব্যবহার করা হয়েছে (যেমন: কানেকশন হওয়া, অডিও আসা শুরু হওয়া, ইত্যাদি)। 

## 📄 License
MIT License
