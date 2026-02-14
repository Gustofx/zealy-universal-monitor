import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

print("BOT_TOKEN detected:", BOT_TOKEN is not None)
print("CHAT_ID detected:", CHAT_ID is not None)

r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": "✅ Telegram test message from GitHub Actions!"}
)

print("Response:", r.text)
