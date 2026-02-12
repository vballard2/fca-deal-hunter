import requests
import os
from twilio.rest import Client
from datetime import datetime, timedelta

# === LOAD ENV VARIABLES ===
AMADEUS_API_KEY = os.environ.get("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.environ.get("AMADEUS_API_SECRET")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.environ.get("TWILIO_PHONE")
YOUR_PHONE = os.environ.get("YOUR_PHONE")

# === GET AMADEUS ACCESS TOKEN ===
def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    response = requests.post(url, data=data)
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

# === SEND TEXT ===
def send_text(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE,
        to=YOUR_PHONE
    )

# === MAIN ===
if __name__ == "__main__":
    deals = search_deals()

    if deals:
        msg = "🔥 FCA DEAL REPORT 🔥\n"
        for dest, price in deals:
            msg += f"{dest}: ${price}\n"
    else:
        msg = "No deals found today from FCA."

    send_text(msg)