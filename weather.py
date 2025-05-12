import requests
from datetime import datetime

# --------- Weather Chatbot Functions ---------

def get_weather(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city_name}&units=metric"
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        main = data["main"]
        wind = data["wind"]
        weather = data["weather"][0]

        temperature = main["temp"]
        feels_like = main["feels_like"]
        humidity = main["humidity"]
        description = weather["description"].capitalize()
        wind_speed = wind["speed"]
        country = data["sys"]["country"]
        timezone_offset = data["timezone"]
        city_time = datetime.utcfromtimestamp(data["dt"] + timezone_offset)
        local_time = city_time.strftime('%Y-%m-%d %H:%M:%S')

        emoji = get_weather_emoji(weather["main"])
        clothing = suggest_clothing(temperature)
        health = health_advice(temperature, humidity, weather["main"])

        return (f"\n{emoji} Weather in {city_name}, {country} ({local_time})\n"
                f"Condition: {description}\n"
                f"Temperature: {temperature}°C (Feels like {feels_like}°C)\n"
                f"Humidity: {humidity}% | Wind Speed: {wind_speed} m/s\n"
                f"\n👕 Clothing Tip: {clothing}\n"
                f"💡 Health Tip: {health if health else 'No major health concerns.'}")
    else:
        return "❌ City not found. Please check the city name."

def suggest_clothing(temp):
    if temp < 10:
        return "It's quite cold! Wear warm clothes like jackets and sweaters."
    elif 10 <= temp < 20:
        return "Cool weather! A light jacket would be nice."
    elif 20 <= temp < 30:
        return "Pleasant weather! Comfortable clothes are perfect."
    else:
        return "It's hot outside! Stay hydrated and wear light clothes."

def get_weather_emoji(condition):
    emoji_map = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️"
    }
    return emoji_map.get(condition, "🌈")

def health_advice(temp, humidity, condition):
    advice = ""

    # Temperature-based health tips
    if temp >= 35:
        advice += "Risk of heat stroke or dehydration. Drink plenty of water. Avoid outdoor activities.\n"
    elif temp <= 5:
        advice += "Risk of cold-related illnesses. Dress warmly in layers.\n"

    # Humidity-related advice
    if humidity >= 80:
        advice += "High humidity can cause fatigue and worsen respiratory issues.\n"
    elif humidity <= 20:
        advice += "Low humidity may cause dry skin and throat irritation.\n"

    # Weather condition-based tips
    condition = condition.lower()
    if "rain" in condition or "drizzle" in condition:
        advice += "Carry an umbrella. Risk of catching a cold.\n"
    elif "snow" in condition:
        advice += "Wear gloves and boots. Beware of slippery roads.\n"

    return advice.strip()

# --------- Main Chatbot Function ---------

def weather_chatbot():
    print("🌦️ Welcome to Smart WeatherBot 3.0!")
    print("Type 'exit' to end the chat.\n")
    api_key = "abf8385654503e4c5fc432e28b822729" 

    while True:
        city = input("Enter city name: ")
        if city.lower() == "exit":
            print("👋 Goodbye! Stay safe and weather-aware.")
            break
        print(get_weather(city, api_key))

# --------- Run the Chatbot ---------
weather_chatbot()
