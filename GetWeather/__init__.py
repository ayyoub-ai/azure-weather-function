import logging
import azure.functions as func
import requests
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    city = req.params.get('city', 'Casablanca')
    api_key = os.environ.get('WEATHER_API_KEY')
    if not api_key:
        return func.HttpResponse("❌ Missing API key", status_code=500)

    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang=fr"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if response.status_code != 200:
            msg = data.get('error', {}).get('message', 'Unknown')
            return func.HttpResponse(f"⚠️ {msg}", status_code=400)

        temp = int(data['current']['temp_c'])
        cond = data['current']['condition']['text']
        loc = data['location']['name']

        emoji = "🌤️"
        if "nuageux" in cond.lower(): emoji = "⛅"
        elif "pluie" in cond.lower() or "averse" in cond.lower(): emoji = "🌧️"
        elif "soleil" in cond.lower() or "ensoleillé" in cond.lower(): emoji = "☀️"
        elif "orage" in cond.lower(): emoji = "⛈️"

        return func.HttpResponse(
            json.dumps({"emoji": emoji, "temp": temp, "message": f"{cond} à {loc} !"}, ensure_ascii=False),
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(f"💥 {str(e)}", status_code=500)
