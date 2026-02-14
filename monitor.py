import requests
import json
import os
import re

# =========================
# 🔶 COMMUNITIES TO MONITOR
# replace with active communities
COMMUNITIES = [
    "Verasity",
    "Lumia",
    "CosmoFox",
    "Coingarage",
    "Coinquant"
]
# =========================

BOT_TOKEN = os.environ["8374656735:AAHcy8FSz-MPvfUTfAWUZS2WYdvGcevVeNg"]   # <<ADD IN GITHUB SECRETS>>
CHAT_ID = os.environ["8123412199"]       # <<ADD IN GITHUB SECRETS>>

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def fetch_page_json(community):
    url = f"https://zealy.io/cw/{community}/questboard"
    html = requests.get(url).text

    match = re.search(r'__NEXT_DATA__" type="application/json">(.*?)</script>', html)

    if not match:
        return None

    return json.loads(match.group(1))

try:
    with open("data.json") as f:
        old = json.load(f)
except:
    old = {}

for community in COMMUNITIES:

    data = fetch_page_json(community)
    if not data:
        continue

    quests = data["props"]["pageProps"]["campaign"]["quests"]
    sprints = data["props"]["pageProps"]["campaign"].get("sprints", [])

    old.setdefault(community, {"quests": {}, "sprints": []})

    for q in quests:
        qid = q["id"]
        title = q.get("title","No title")
        xp = q.get("xp",0)
        status = q.get("status","unknown")
        hidden = q.get("isHidden", False)

        if qid not in old[community]["quests"]:
            send(f"🔥 NEW QUEST ({community})\n{title}\nXP: {xp}\nStatus: {status}")
        else:
            old_q = old[community]["quests"][qid]
            if xp != old_q["xp"] or status != old_q["status"]:
                send(f"⚡ QUEST UPDATED ({community})\n{title}\nXP: {xp}\nStatus: {status}")

        if hidden and qid not in old[community]["quests"]:
            send(f"👀 HIDDEN QUEST DETECTED EARLY ({community})\n{title}")

        old[community]["quests"][qid] = {"xp": xp, "status": status}

    for s in sprints:
        sid = s["id"]
        name = s.get("name","Sprint")

        if sid not in old[community]["sprints"]:
            send(f"🚀 NEW SPRINT ({community})\n{name}")

    old[community]["sprints"] = [s["id"] for s in sprints]

with open("data.json","w") as f:
    json.dump(old, f)
