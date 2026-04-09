import audioop
# audioop = Python এর built-in audio processing library
# কোনো install লাগে না, Python এর সাথেই আসে
# audio bytes এর format পরিবর্তন করার কাজে ব্যবহার হয়

# ======================================================

def pcm_to_mulaw(pcm_data: bytes) -> bytes:
# pcm_data: bytes = input হিসেবে PCM audio bytes নেবে
# -> bytes = output হিসেবে mulaw audio bytes দেবে
#
# কেন এই conversion দরকার?
#   OpenAI TTS (generate_tts) PCM format এ audio দেয়
#   কিন্তু Twilio শুধু mulaw format বোঝে
#   তাই PCM → mulaw convert না করলে
#   Twilio ফোনে কিছুই বাজাতে পারবে না
#
# PCM কী?
#   PCM = Pulse Code Modulation
#   raw audio data — কোনো compression নেই
#   প্রতিটা sound wave এর exact value সংখ্যায় লেখা থাকে
#   computer এ সব audio ভেতরে ভেতরে PCM এই থাকে
#   16-bit মানে প্রতিটা sound value 2 bytes এ লেখা (0 থেকে 65535)
#
# mulaw কী?
#   mulaw = একটা compressed audio format
#   ফোন network এর জন্য তৈরি — অনেক পুরনো standard (1960s থেকে)
#   16-bit PCM কে 8-bit এ compress করে
#   মানে audio এর size অর্ধেক হয়ে যায়
#   Twilio এবং সব ফোন network এই format ব্যবহার করে

    """
    Convert 16-bit PCM audio to 8-bit mu-law audio.
    Twilio Media Streams expect mu-law 8000Hz.
    """
    # এটা docstring — function এর কাজ বর্ণনা করে
    # code এ কোনো কাজ করে না, শুধু documentation

    return audioop.lin2ulaw(pcm_data, 2)
    # audioop.lin2ulaw() = PCM থেকে mulaw convert করার function
    #
    # pcm_data = input audio bytes (PCM format এ)
    #
    # 2 = প্রতিটা sample কত bytes এ আছে
    #   PCM 16-bit মানে প্রতিটা sample = 2 bytes
    #   তাই 2 দেওয়া হয়েছে
    #   8-bit PCM হলে 1 দিতে হতো
    #   32-bit PCM হলে 4 দিতে হতো
    #
    # Output → mulaw format এ converted audio bytes
    #   এই bytes সরাসরি Twilio তে পাঠানো যাবে
    #   Twilio এটা ফোনে বাজাবে

# ======================================================
# 🔗 এই function কোথায় use হবে —
#
# openai_service.generate_tts(text)
#         ↓
#     PCM bytes আসে
#         ↓
# pcm_to_mulaw(pcm_bytes)
#         ↓
#     mulaw bytes হয়
#         ↓
# Twilio তে পাঠানো হয়
#         ↓
#     ফোনে AI এর voice শোনা যায়