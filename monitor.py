import requests
import json
import os
import re
import time

# =========================
# 🔶 COMMUNITIES TO MONITOR
COMMUNITIES = [
    "Verasity",
    "Lumia",
    "CosmoFox",
    "Coingarage",
    "Coinquant"
]
# =========================

# Telegram credentials (from GitHub Secrets)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ ERROR: BOT_TOKEN or CHAT_ID not set!")
    exit(1)

def send(msg):
    """Send a Telegram message with fail-proof logging"""
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
        if r.status_code == 200:
            print(f"✅ Telegram message sent: {msg[:50]}...")
        else:
            print(f"⚠ Telegram failed ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"⚠ Exception sending Telegram message: {e}")

# Startup alert
send("🚀 Zealy Universal Monitor started successfully!")
print("🚀 Zealy Universal Monitor started successfully!")

def fetch_page_json(community):
    """Fetch Zealy questboard page JSON"""
    url = f"https://zealy.io/cw/{community}/questboard"
    try:
        html = requests.get(url, timeout=10).text
        match = re.search(r'__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if not match:
            print(f"⚠ Could not find JSON data for {community}")
            return None
        return json.loads(match.group(1))
    except Exception as e:
        print(f"⚠ Error fetching {community}: {e}")
        return None

# Load saved data or create empty structure
try:
    with open("data.json") as f:
        old = json.load(f)
except:
    old = {}

# =========================
# LOOP FOREVER EVERY 30 SECONDS
while True:
    for community in COMMUNITIES:
        print(f"🔎 Checking community: {community}")

        data = fetch_page_json(community)
        if not data:
            continue

        quests = data["props"]["pageProps"]["campaign"].get("quests", [])
        sprints = data["props"]["pageProps"]["campaign"].get("sprints", [])

        old.setdefault(community, {"quests": {}, "sprints": []})

        # ----- QUEST MONITOR -----
        for q in quests:
            qid = str(q["id"])
            title = q.get("title", "No title")
            xp = q.get("xp", 0)
            status = q.get("status", "unknown")
            hidden = q.get("isHidden", False)

            # New quest
            if qid not in old[community]["quests"]:
                send(f"🔥 NEW QUEST ({community})\n{title}\nXP: {xp}\nStatus: {status}")
                if hidden:
                    send(f"👀 HIDDEN QUEST DETECTED EARLY ({community})\n{title}")

            # XP or status change
            else:
                old_q = old[community]["quests"][qid]
                if xp != old_q["xp"] or status != old_q["status"]:
                    send(f"⚡ QUEST UPDATED ({community})\n{title}\nXP: {xp}\nStatus: {status}")

            # Save latest quest data
            old[community]["quests"][qid] = {"xp": xp, "status": status}

        # ----- SPRINT MONITOR -----
        for s in sprints:
            sid = str(s["id"])
            name = s.get("name", "Sprint")
            active = s.get("active", False)

            if sid not in old[community]["sprints"]:
                send(f"🚀 NEW SPRINT ({community})\n{name}\nActive: {active}")

        # Update sprint IDs
        old[community]["sprints"] = [str(s["id"]) for s in sprints]

        # Log info
        print(f"✅ {len(quests)} quests and {len(sprints)} sprints checked for {community}")

    # Save data for next iteration
    with open("data.json", "w") as f:
        json.dump(old, f)

    # Wait 30 seconds before next check
    print("⏱ Waiting 30 seconds before next check...\n")
    time.sleep(30)
