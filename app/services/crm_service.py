import os
# .env ফাইল থেকে ONYX_CRM_API_KEY পড়ার জন্য

import requests
# requests = Python এর সবচেয়ে popular HTTP library
# এটা দিয়ে অন্য server এ request পাঠানো যায়
# যেমন — CRM এর API তে GET, POST request পাঠানো
# (এই ফাইলে এখনো actually use হয়নি, comment এ আছে)

from app.utils.logger import logger
# পুরো project এর shared logger

# ======================================================

class CRMService:
# CRM = Customer Relationship Management
# customer এর তথ্য রাখার সফটওয়্যার
# এখানে Onyx CRM ব্যবহার করা হচ্ছে
# এই class এ CRM এর সাথে সব কাজ একজায়গায় রাখা হয়েছে —
#   customer খোঁজা, নতুন contact বানানো, appointment নেওয়া

    def __init__(self):
    # class তৈরি হওয়ার সাথে সাথে এটা চলে
    # API key এবং base URL save করে রাখে

        self.api_key = os.getenv("ONYX_CRM_API_KEY")
        # .env থেকে CRM এর API key পড়ছে
        # এই key দিয়ে CRM এ "login" করা হয়
        # প্রতিটা request এ এই key পাঠাতে হয়
        # নাহলে CRM বলবে — "তুমি কে? access নেই"

        self.base_url = "https://api.onyxcrm.com/v1"
        # CRM এর API এর base address
        # সব request এই URL দিয়ে শুরু হবে
        # যেমন —
        #   customer খুঁজতে → https://api.onyxcrm.com/v1/customers
        #   appointment নিতে → https://api.onyxcrm.com/v1/appointments
        # "Placeholder" comment মানে —
        #   এটা real URL না, পরে actual CRM এর URL দিতে হবে

# ======================================================

    def search_customer(self, phone):
    # phone = customer এর ফোন নম্বর
    # CRM এ এই নম্বর দিয়ে customer খুঁজবে
    #
    # কে call করে?
    #   ফোন কল আসলে — caller এর নম্বর দিয়ে আগে CRM এ খুঁজবে
    #   যদি পাওয়া যায় → পুরনো customer, তার তথ্য দেখাবে
    #   না পাওয়া গেলে → নতুন customer, create_contact() call হবে

        try:
            logger.info(f"Searching customer: {phone}")
            # Output → "Searching customer: +8801XXXXXXXX" log এ লেখে

            # response = requests.get(
            #     f"{self.base_url}/customers?phone={phone}",
            #     headers={"Authorization": f"Bearer {self.api_key}"}
            # )
            # এই line গুলো comment করা — এখনো implement হয়নি
            # comment খুললে কী হতো —
            #   requests.get() → CRM এর server এ GET request যেতো
            #   ?phone={phone} → URL এ phone নম্বর দিয়ে খুঁজতো
            #   headers={"Authorization": f"Bearer {self.api_key}"}
            #     → API key পাঠিয়ে prove করতো "আমি authorized"
            #   response এ customer এর তথ্য আসতো

            return None
            # এখন সবসময় None ফেরত দেয়
            # মানে — "customer পাওয়া যায়নি" বলছে
            # real implement হলে customer এর data ফেরত দেবে

        except Exception as e:
            logger.error(f"CRM Search error: {e}")
            # Output → "CRM Search error: ..." log এ লেখে
            return None

# ======================================================

    def create_contact(self, customer_data):
    # customer_data = নতুন customer এর তথ্য (dict হিসেবে)
    # যেমন —
    #   {
    #     "name": "Rahim",
    #     "phone": "+8801XXXXXXXX",
    #     "car_interest": "SUV"
    #   }
    #
    # কে call করে?
    #   search_customer() তে customer না পাওয়া গেলে
    #   AI customer এর নাম, নম্বর collect করার পর
    #   এই function call হবে — CRM এ নতুন entry তৈরি করতে

        try:
            logger.info(f"Creating contact: {customer_data.get('name')}")
            # customer_data.get('name') → dict থেকে name বের করছে
            # Output → "Creating contact: Rahim" log এ লেখে

            # response = requests.post(
            #     f"{self.base_url}/contacts",
            #     json=customer_data,
            #     headers={"Authorization": f"Bearer {self.api_key}"}
            # )
            # এই line গুলো comment করা — এখনো implement হয়নি
            # comment খুললে কী হতো —
            #   requests.post() → CRM এ নতুন contact তৈরির request
            #   json=customer_data → customer এর তথ্য পাঠাতো
            #   CRM নতুন entry বানিয়ে তার ID ফেরত দিতো

            return {"id": "mock-123"}
            # এখন fake ID ফেরত দিচ্ছে — testing এর জন্য
            # real implement হলে CRM এর দেওয়া actual ID আসবে
            # এই ID পরে appointment book করতে লাগবে

        except Exception as e:
            logger.error(f"CRM Create error: {e}")
            # Output → "CRM Create error: ..." log এ লেখে
            return None

# ======================================================

    def book_appointment(self, appointment_data):
    # appointment_data = appointment এর তথ্য (dict হিসেবে)
    # যেমন —
    #   {
    #     "customer_id": "mock-123",   ← create_contact থেকে পাওয়া ID
    #     "date": "2024-01-20",
    #     "time": "10:00 AM",
    #     "type": "test_drive"
    #   }
    #
    # কে call করে?
    #   AI যখন customer কে appointment confirm করাবে
    #   customer রাজি হলে এই function call হবে

        try:
            logger.info(f"Booking appointment for: {appointment_data.get('customer_id')}")
            # Output → "Booking appointment for: mock-123" log এ লেখে

            # response = requests.post(
            #     f"{self.base_url}/appointments",
            #     json=appointment_data,
            #     headers={"Authorization": f"Bearer {self.api_key}"}
            # )
            # এই line গুলো comment করা — এখনো implement হয়নি
            # comment খুললে কী হতো —
            #   CRM এ নতুন appointment entry তৈরি হতো
            #   Masum এর calendar এ automatically দেখা যেতো

            return {"success": True}
            # এখন সবসময় success ফেরত দিচ্ছে — testing এর জন্য
            # real implement হলে CRM confirm করলে True, না হলে False

        except Exception as e:
            logger.error(f"CRM Book error: {e}")
            # Output → "CRM Book error: ..." log এ লেখে
            return {"success": False}
            # সমস্যা হলে success: False ফেরত দাও
            # caller কে বলা যাবে — "appointment নেওয়া যায়নি, আবার চেষ্টা করুন"

# ======================================================

crm_service = CRMService()
# ফাইলের শেষে একটা READY object তৈরি
# অন্য ফাইল সরাসরি import করে ব্যবহার করতে পারবে —
#   from app.services.crm_service import crm_service
#   customer = crm_service.search_customer(phone)

# ======================================================
# 🔗 পুরো flow এক নজরে —
#
# ফোন কল আসে
#         ↓
# search_customer(phone)
#   → CRM এ customer আছে কিনা খোঁজে
#         ↓
#   পাওয়া গেলে → পুরনো customer এর তথ্য দেখাও
#   না পাওয়া গেলে ↓
#         ↓
# AI কথা বলে নাম, নম্বর, interest collect করে
#         ↓
# create_contact(customer_data)
#   → CRM এ নতুন entry তৈরি হয়
#   → customer ID পাওয়া যায়
#         ↓
# book_appointment(appointment_data)
#   → CRM এ appointment save হয়
#   → Masum এর calendar এ দেখা যায়
#
# ⚠️ এই ফাইলের সব API call এখনো comment এ আছে
#    মানে CRM এর সাথে real connection এখনো হয়নি
#    এটা এখন শুধু structure — পরে implement করতে হবে