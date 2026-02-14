import os
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

print("Testing Telegram message...")

try:
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": "✅ Telegram test message from GitHub Actions!"}
    )
    print("Message sent!")
except Exception as e:
    print(f"Failed to send message: {e}")
