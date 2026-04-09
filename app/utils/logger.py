import logging
# logging = Python এর built-in library
# print() দিয়েও দেখানো যেতো, কিন্তু logging অনেক বেশি powerful
# কারণ —
#   ১. কখন হয়েছে (time) automatically যোগ হয়
#   ২. কতটা serious সেটা বলা যায় (INFO, ERROR, WARNING)
#   ৩. একসাথে console এ দেখানো এবং file এ save করা যায়
#   ৪. project বড় হলে কোন ফাইল থেকে log এলো সেটা বোঝা যায়

import sys
# sys = Python এর built-in library
# sys.stdout = console (terminal) কে represent করে
# এখানে দরকার — log গুলো কোথায় দেখাবে সেটা বলার জন্য

# ======================================================

logging.basicConfig(
# basicConfig = logging এর global settings একবারে set করে
# এটা একবার করলেই পুরো project এ কাজ করে

    level=logging.INFO,
    # level মানে — কোন ধরনের log দেখাবে সেটা ঠিক করে
    # logging এ ৫টা level আছে, ছোট থেকে বড় —
    #   DEBUG   → development এ detail দেখার জন্য (সবচেয়ে ছোট)
    #   INFO    → সব ঠিক আছে, কী হচ্ছে জানাচ্ছে  ← আমরা এটা দিয়েছি
    #   WARNING → সমস্যা না, কিন্তু সাবধান থাকো
    #   ERROR   → কিছু একটা ভুল হয়েছে
    #   CRITICAL→ সব বন্ধ হয়ে যাচ্ছে (সবচেয়ে বড়)
    #
    # INFO দিলে — INFO, WARNING, ERROR, CRITICAL সব দেখাবে
    # DEBUG দেখাবে না (INFO এর নিচে তাই)
    # মানে শুধু দরকারি log গুলো দেখাবে, অতিরিক্ত না

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # প্রতিটা log line কেমন দেখাবে সেটা define করছে
    # %(asctime)s   → কখন হয়েছে: "2024-01-15 10:30:45,123"
    # %(name)s      → কোন logger থেকে এলো: "InsureFlowAI"
    # %(levelname)s → কতটা serious: "INFO" বা "ERROR"
    # %(message)s   → আসল message: "Incoming call received"
    #
    # Output এরকম দেখাবে —
    # 2024-01-15 10:30:45,123 - InsureFlowAI - INFO - Incoming call received

    stream=sys.stdout
    # log গুলো কোথায় পাঠাবে — sys.stdout মানে console এ
    # sys.stderr ও আছে — সেটা error output (আলাদা stream)
    # stdout দিলে সব একসাথে terminal এ দেখা যায়
    # production এ এখানে file দিলে file এ save হতো
)

# ======================================================

logger = logging.getLogger("InsureFlowAI")
# getLogger("InsureFlowAI") = "InsureFlowAI" নামে একটা logger তৈরি করো
# এই নামটাই log এ %(name)s এর জায়গায় দেখাবে
#
# কেন named logger?
#   logging.info() সরাসরি call করা যেতো
#   কিন্তু তাহলে কোন project এর log বোঝা যেতো না
#   "InsureFlowAI" নাম দিলে —
#   log দেখে বোঝা যাবে এটা এই project এর log
#
# অন্য ফাইলে এই logger কীভাবে ব্যবহার হয় —
#   from app.utils.logger import logger
#   logger.info("Incoming call received")
#   logger.error("Something went wrong")
#
# Output →
#   2024-01-15 10:30:45 - InsureFlowAI - INFO - Incoming call received
#   2024-01-15 10:30:46 - InsureFlowAI - ERROR - Something went wrong