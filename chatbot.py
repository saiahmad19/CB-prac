from dotenv import load_dotenv
import os
import json
import requests
from groq import Groq

load_dotenv()
my_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=my_key)


def get_weather(city):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_response = requests.get(geo_url, params={"name": city, "count": 1}).json()

    lat = geo_response["results"][0]["latitude"]
    lon = geo_response["results"][0]["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_response = requests.get(weather_url, params={
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m"
    }).json()

    temp = weather_response["current"]["temperature_2m"]
    return f"The current temperature in {city} is {temp}°C."


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current temperature for a given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city, e.g. Karachi"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

messages = [
    {
        "role": "system",
"content": "You are a helpful assistant. For weather-related questions, only state facts that come from the get_weather tool's results. If asked about weather forecasts or historical weather, say so plainly since you don't have a tool for that. For all other topics, answer normally using your own knowledge."    }
]

while True:
    user_input = input("you: ")

    if user_input.lower() == "quit":
        print("Goodbye")
        break

    messages.append({"role": "user", "content": user_input})

    while True:
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                tools=tools
            )
        except Exception as e:
            print("Something went wrong talking to the AI:", e)
            reply = "Sorry, I ran into a connection problem. Please try again."
            break

        response_message = response.choices[0].message

        if response_message.tool_calls:
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                city = json.loads(tool_call.function.arguments)["city"]
                weather_result = get_weather(city)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": weather_result
                })
        else:
            reply = response_message.content
            break

    print("bot:", reply)
    messages.append({"role": "assistant", "content": reply})