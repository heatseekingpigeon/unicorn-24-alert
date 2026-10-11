import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL = "https://www.thornwatches.com/collections/pre-owned/products.json"
SEEN_FILE = "seen_products.txt"

def load_seen():
    # Temporarily bypassed for testing so everything looks new!
    return set()

def save_seen(seen_set):
    with open(SEEN_FILE, "w") as f:
        for pid in seen_set:
            f.write(f"{pid}\n")

def send_alert(message):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(telegram_url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})
    print(f"Telegram API Response: {response.status_code} - {response.text}")

def check_products():
    seen = load_seen()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return
    
    products = data.get("products", [])
    print(f"Fetched {len(products)} total products from site. Seen file currently has {len(seen)} IDs.")

    for product in products:
        pid = str(product["id"])
        title = product["title"]
        handle = product["handle"]
        link = f"https://www.thornwatches.com/products/{handle}"
        
        # Check if any variant is available
        available = any(v.get("available", False) for v in product.get("variants", []))

        print(f"-> Checking: {title} | ID: {pid} | In Seen: {pid in seen} | Available: {available}")

        if pid not in seen:
            if available:
                msg = f"🚨 <b>NEW PRE-OWNED WATCH DROP!</b>\n\n<b>{title}</b>\n\n🔗 {link}"
                print(f"--> SENDING ALERT for: {title}")
                send_alert(msg)
            else:
                print(f"--> Sold out, skipping alert.")
            seen.add(pid)

    save_seen(seen)

if __name__ == "__main__":
    check_products()
