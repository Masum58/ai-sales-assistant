# InsureFlow AI Copilot

An AI-powered real-time Sales Copilot designed for auto dealerships. This system listens to live conversations between a salesperson (Masum) and a customer (Kamal), providing real-time insights and data-driven assistance using Twilio, Deepgram, and OpenAI.

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

## 📄 License
MIT License
