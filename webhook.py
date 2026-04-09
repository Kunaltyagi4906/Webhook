from fastapi import FastAPI, Request, HTTPException
import requests
import json
import datetime

from models import Mandate, Installment
from Database import SessionLocal

app = FastAPI()

# ================= CONFIG =================
WEBHOOK_SECRET = "connectingit202004"
ROCKETPAY_BASE_URL = "https://api-staging.rocketpay.co.in"
TOKEN = " eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjAwMDAwMTlkLTFhN2ItMWEzNC04Yzc3LTQ5YzU3MTIyYWM4OSIsIm1vYmlsZV9udW1iZXIiOiIrOTE5ODkxMDAxNDQzIiwibWVyY2hhbnRfaWQiOiIwMDAwMDE5ZC0xYTdiLTE4ZjUtYmM1MC1lZWQ1NmVkNzBkNWIiLCJyb2xlIjoiRElTVFJJQlVUT1JfQURNSU4iLCJhY2NvdW50X3R5cGUiOiJESVNUUklCVVRPUiIsInNvdXJjZSI6IkNPTU1PTl9MT0dJTiIsImVudGVycHJpc2VfaWQiOiIwMDAwMDE5ZC0xYTdiLTE4ZjUtYmM1MC1lZWQ1NmVkNzBkNWIiLCJpYXQiOjE3NzQzNTAzMTh9.H7Y2WibB3sLpAPXwVR-NDmxcxVEzDYSU4wYkbYnpn08"   # replace

# ================= DB SAVE =================
def save_mandate(data, real_state):
    db = SessionLocal()
    try:
        mandate_id = data.get("id")

        existing = db.query(Mandate).filter_by(mandate_id=mandate_id).first()

        if existing:
            existing.webhook_status = data.get("status")
            existing.real_state = real_state
            existing.full_payload = data
        else:
            new = Mandate(
                mandate_id=mandate_id,
                webhook_status=data.get("status"),
                real_state=real_state,
                full_payload=data
            )
            db.add(new)

        db.commit()
        print("✅ Mandate saved in DB")

    except Exception as e:
        db.rollback()
        print("❌ DB ERROR (MANDATE):", str(e))

    finally:
        db.close()


def save_installment(data):
    db = SessionLocal()
    try:
        inst_id = data.get("id")

        existing = db.query(Installment).filter_by(installment_id=inst_id).first()

        if existing:
            existing.status = data.get("status")
            existing.amount = data.get("amount", 0)
            existing.full_payload = data
        else:
            new = Installment(
                installment_id=inst_id,
                mandate_id=data.get("mandate_id"),
                status=data.get("status"),
                amount=data.get("amount", 0),
                full_payload=data
            )
            db.add(new)

        db.commit()
        print("✅ Installment saved in DB")

    except Exception as e:
        db.rollback()
        print("❌ DB ERROR (INSTALLMENT):", str(e))

    finally:
        db.close()


# ================= FETCH MANDATE =================
def fetch_mandate_details(mandate_id):
    url = f"{ROCKETPAY_BASE_URL}/v4/mandates/{mandate_id}"

    headers = {
        "x-token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjAwMDAwMTlkLTFhN2ItMWEzNC04Yzc3LTQ5YzU3MTIyYWM4OSIsIm1vYmlsZV9udW1iZXIiOiIrOTE5ODkxMDAxNDQzIiwibWVyY2hhbnRfaWQiOiIwMDAwMDE5ZC0xYTdiLTE4ZjUtYmM1MC1lZWQ1NmVkNzBkNWIiLCJyb2xlIjoiRElTVFJJQlVUT1JfQURNSU4iLCJhY2NvdW50X3R5cGUiOiJESVNUUklCVVRPUiIsInNvdXJjZSI6IkNPTU1PTl9MT0dJTiIsImVudGVycHJpc2VfaWQiOiIwMDAwMDE5ZC0xYTdiLTE4ZjUtYmM1MC1lZWQ1NmVkNzBkNWIiLCJpYXQiOjE3NzQzNTAzMTh9.H7Y2WibB3sLpAPXwVR-NDmxcxVEzDYSU4wYkbYnpn08" ,
        "x-app-context": "MERCHANT_API"
    }

    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            print("❌ Fetch failed:", res.text)
            return None
    except Exception as e:
        print("❌ Fetch error:", str(e))
        return None


# ================= HANDLE =================
def handle_mandate(data):
    mandate_id = data.get("id")

    print(f"\n🧾 Mandate → {mandate_id}")

    full_data = fetch_mandate_details(mandate_id)

    if not full_data:
        print("⚠️ No full data, saving basic webhook data")
        save_mandate(data, real_state="UNKNOWN")
        return

    real_state = full_data.get("state")

    print(f"✅ REAL STATE → {real_state}")

    save_mandate(data, real_state)


def handle_installment(data):
    print(f"\n💸 Installment → {data.get('id')}")

    save_installment(data)


# ================= WEBHOOKS =================

# 🧾 Mandate Webhook
from fastapi import Body

@app.post("/webhook/mandate")
async def mandate_webhook(data: dict = Body(...)):

    print("\n🔥 Mandate Webhook:")
    print(data)

    handle_mandate(data)

    return {"status": "ok"}


# 💸 Installment Webhook
@app.post("/webhook/installment")
async def installment_webhook(data: dict = Body(...)):

    print("\n🔥 Installment Webhook:")
    print(data)

    handle_installment(data)

    return {"status": "ok"}


# ================= STATUS API =================
@app.get("/status/{mandate_id}")
def status(mandate_id: str):
    db = SessionLocal()

    m = db.query(Mandate).filter_by(mandate_id=mandate_id).first()

    db.close()

    if not m:
        return {"error": "not found"}

    return {
        "mandate_id": m.mandate_id,
        "webhook_status": m.webhook_status,
        "real_state": m.real_state
    }


# ================= ROOT =================
@app.get("/")
def home():
    return {"message": "RocketPay system running 🚀"}
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(path_name: str, request: Request):
    print(f"❌ WRONG HIT → /{path_name} | METHOD: {request.method}")
    return {"error": "Invalid endpoint"}