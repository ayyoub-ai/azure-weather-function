import logging
import azure.functions as func
import urllib.request
import urllib.parse
import json
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    city = req.params.get('city', 'Casablanca')
    api_key = os.environ.get('WEATHER_API_KEY')
    if not api_key:
        return func.HttpResponse("❌ Missing API key", status_code=500)

    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': api_key,
        'q': city,
        'lang': 'fr'
    }
    url = base_url + '?' + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if 'error' in data:
            msg = data['error'].get('message', 'Unknown error')
            return func.HttpResponse(f"⚠️ {msg}", status_code=400)

        temp = int(data['current']['temp_c'])
        cond = data['current']['condition']['text']
        loc = data['location']['name']

        emoji = "🌤️"
        if "nuageux" in cond.lower(): emoji = "⛅"
        elif "pluie" in cond.lower() or "averse" in cond.lower(): emoji = "🌧️"
        elif "soleil" in cond.lower() or "ensoleillé" in cond.lower(): emoji = "☀️"
        elif "orage" in cond.lower(): emoji = "⛈️"

        result = {
            "emoji": emoji,
            "temp": temp,
            "message": f"{cond} à {loc} !"
        }
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(f"💥 {str(e)}", status_code=500)
