import serial
import time
import json
import requests

FILE_PATH = "weather_data.json"  # Path to the file where data is saved
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
API_KEY = "dc134fd5dc7cd6be340cf5a441a3450d"  # Replace with your OpenWeatherMap API Key
FILE_PATH = "weather_data.json"  # Path to the file where data will be saved
time.sleep(2)

lora_set = False

def process_daily_forecast(forecasts):
    """
    Process the forecast data to calculate high, low, and chance of rain
    """
    daily_forecast = {}
    for forecast in forecasts:
        date = forecast['dt_txt'].split(" ")[0]
        temp = forecast['main']['temp']
        rain = 'rain' in forecast

        if date not in daily_forecast:
            daily_forecast[date] = {'high': temp, 'low': temp, 'rain': rain}
        else:
            daily_forecast[date]['high'] = max(daily_forecast[date]['high'], temp)
            daily_forecast[date]['low'] = min(daily_forecast[date]['low'], temp)
            daily_forecast[date]['rain'] |= rain

    return daily_forecast
    
def fetch_weather_data(CITY):
    URL = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def save_data_to_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def format_weather_data(data):
    forecasts = data['list']
    daily_data = process_daily_forecast(forecasts)
    
    formatted_data = []
    for i, (_, info) in enumerate(daily_data.items()):
        if i >= 5:  # Limit to 5 days
            break
        high_temp = round(info['high'])
        low_temp = round(info['low'])
        chance_of_rain = "Yes" if info['rain'] else "No"
        formatted_data.append({"h": high_temp, "l": low_temp, "r": chance_of_rain})

    return formatted_data


def send_data(data):
    json_string = str(data)  # Convert the list of dicts to a string
    ser.write((json_string + '\n').encode())

def listen_for_reply(timeout=10):
    global lora_set
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ser.in_waiting:
            response = ser.readline().decode('utf-8').rstrip()
            weather_data = fetch_weather_data(response)
            if weather_data:
                save_data_to_file(weather_data, FILE_PATH)
            else:
                print("Failed to fetch weather data")
            print(f"Received: {response}")
            if "Got reply:" in response:
                lora_set = True
                break
            elif "Receive failed" in response or "No reply" in response:
                lora_set = False
                break

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def main():
    while True:  # Run continuously
        try:
            weather_data = read_data_from_file(FILE_PATH)
            if weather_data:
                formatted_data = format_weather_data(weather_data)
                print(formatted_data)
                send_data(formatted_data)
                listen_for_reply()
            else:
                print("Weather data is empty")
            #time.sleep(30)  # Sleep for 30 seconds before sending the next data
        except FileNotFoundError:
            print(f"Failed to read weather data from {FILE_PATH}")

if __name__ == "__main__":
    main()
