import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

def get_weather(city_name):
    # Construction de l'URL de la requête
    complete_url = f"{BASE_URL}appid={API_KEY}&q={city_name}&units=metric&lang=fr"
    
    # Envoi de la requête à l'API
    response = requests.get(complete_url)
    
    # Conversion de la réponse en format JSON
    x = response.json()
    
    # Vérification si la requête a réussi
    if x["cod"] != "404":
        # Extraction des données importantes
        y = x["main"]
        current_temperature = y["temp"]
        current_humidity = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        
        # Formatage du résultat
        return (f"La température à {city_name} est de {current_temperature}°C avec une humidité de {current_humidity}%. "
                f"Le ciel est actuellement {weather_description}.")
    else:
        return "Ville non trouvée."