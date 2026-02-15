import requests
import os
from datetime import datetime, timedelta

# === LOAD ENV VARIABLES ===
AMADEUS_API_KEY = os.environ.get("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.environ.get("AMADEUS_API_SECRET")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# === GET AMADEUS ACCESS TOKEN ===
def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# === SEARCH CHEAP FLIGHTS ===
def search_deals():
    token = get_amadeus_token()
    headers = {"Authorization": f"Bearer {token}"}

    future_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

    destinations = ["LAS", "LAX", "DEN", "SEA", "ORD", "PHX", "MCO", "JFK"]

    deals = []

    for dest in destinations:
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        params = {
            "originLocationCode": "FCA",
            "destinationLocationCode": dest,
            "departureDate": future_date,
            "adults": 1,
            "max": 1
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                price = float(data["data"][0]["price"]["total"])
                deals.append((dest, price))

    deals.sort(key=lambda x: x[1])
    return deals[:3]

# === SEND TELEGRAM MESSAGE ===
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=payload)

    print("Telegram response status:", response.status_code)
    print("Telegram response body:", response.text)

    response.raise_for_status()

# === MAIN ===
if __name__ == "__main__":
    deals = search_deals()

    if deals:
        msg = "🔥 FCA DEAL REPORT 🔥\n"
        for dest, price in deals:
            msg += f"{dest}: ${price}\n"
    else:
        msg = "No deals found today from FCA."

    print("Final message being sent:")
    print(msg)

    send_telegram(msg)
