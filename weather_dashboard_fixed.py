import json
import time
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import requests

class WeatherDashboard: 
    def __init__(self): 
        #the line that u gotta put ur API key in, im gonna use mine for now
        self.api_key = "cfa1c8ea11587b3b78096e6f5264aa57"
        self.base_url = "http://api.openweathermap.org/data/2.5/"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"

    def get_current_weather(self, city):
        url = f"{self.base_url}weather?q={city}&appid={self.api_key}&units=metric"

        try: 
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                return {
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'].title(),
                    'weather_main': data['weather'][0]['main'],
                    'wind_speed': data['wind']['speed'],
                    'wind_direction': data['wind'].get('deg', 0),
                    'visibility': data.get('visibility', 'N/A'),
                    'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                    'sunset': datetime.fromtimestamp(data['sys']['sunset']),
                    'timestamp': datetime.now()
                }
            else: 
                print (f"Error: {data.get('message', 'City not found')}")
                return None

        except Exception as e:
            print (f"Error fetching weather data: {e}")
            return None

    def get_5_day_forecast(self, city): 
        url = f"{self.forecast_url}?q={city}&appid={self.api_key}&units=metric"

        try: 
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                forecasts = []
                for item in data["list"]: 
                    forecasts.append({
                        'datetime': datetime.fromtimestamp(item['dt']),
                        'temperature': item['main']['temp'],
                        'description': item['weather'][0]['description'].title(),
                        'humidity': item['main']['humidity'],
                        'wind_speed': item['wind']['speed']
                    })
                return forecasts
            else: 
                print (f"Error: {data.get('message', 'city not found')}")
                return None

        except Exception as e:
            print(f"Error fetching forecast data: {e}")
            return None

    def display_current_weather (self, weather_data):
        if not weather_data:
            return
        
        #im having a headache pls send me pills
        print ("\n" + "="*25)
        print(f"CURRENT WEATHER FOR {weather_data['city']}, {weather_data['country']}")
        print("="*25)
        print(f"🌡️  Temperature: {weather_data['temperature']:.1f}°C (Feels like {weather_data['feels_like']:.1f}°C)")
        print(f"🌈  Condition: {weather_data['description']}")
        print(f"💧  Humidity: {weather_data['humidity']}%")
        print(f"🌬️  Wind: {weather_data['wind_speed']} m/s")
        print(f"🔍  Visibility: {weather_data['visibility']} meters" if weather_data['visibility'] != 'N/A' else "🔍  Visibility: N/A")
        print(f"🌅  Sunrise: {weather_data['sunrise'].strftime('%H:%M')}")
        print(f"🌇  Sunset: {weather_data['sunset'].strftime('%H:%M')}")
        print(f"⏰  Last Updated: {weather_data['timestamp'].strftime('%Y-%m-%d %H:%M')}")
        print("="*25)

    def get_weather_emoji(self, weather_main):
        weather_emojis = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '🌨️',
            'Mist': '🌫️',
            'Fog': '🌫️',
            'Haze': '🌫️'
        }
        return weather_emojis.get(weather_main, '🌤️')

    def create_temperature_chart(self, forecast_data, city): 
        if not forecast_data: 
            return

        next_24h = forecast_data[:8]
        times = [item['datetime'] for item in next_24h]
        temps = [item['temperature'] for item in next_24h]

        plt.figure (figsize = (12, 6))
        plt.plot (times, temps, marker='o', linewidth=2, markersize=6, color='#FF6B6B')
        plt.fill_between (times, temps, alpha=0.3, color = '#FF6B6B')
        
        plt.title (f'24-Hour Temperature Forecast for {city}', fontsize=16, fontweight='bold')
        plt.xlabel ('Time', fontsize = 12)
        plt.ylabel ('Temperature (°C)', fontsize = 12)
        plt.grid (True, alpha = 0.3)

        #the hours crap
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
        plt.xticks (rotation = 45)

        #the temp labels thingy
        for i, (time, temp) in enumerate (zip(times, temps)):
            plt.annotate(f'{temp:.1f}°', (time, temp), 
                        textcoords="offset points", xytext=(0,10), ha='center')

        plt.tight_layout()
        plt.show()
    
    def create_weather_summary_chart (self, forecast_data, city):
        if not forecast_data: 
            return

        daily_data = {}
        for item in forecast_data: 
            date = item ['datetime'].date()
            if date not in daily_data:
                daily_data[date] = {
                    'temps': [],
                    'humidity': [],
                    'wind': []
                }
            daily_data[date]['temps'].append(item['temperature'])
            daily_data[date]['humidity'].append(item['humidity'])
            daily_data[date]['wind'].append(item['wind_speed'])
        
        dates = list(daily_data.keys())[:5]  # Next 5 days
        avg_temps = [np.mean(daily_data[date]['temps']) for date in dates]
        avg_humidity = [np.mean(daily_data[date]['humidity']) for date in dates]
        avg_wind = [np.mean(daily_data[date]['wind']) for date in dates]

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize = (12, 10))

        ax1.plot (dates, avg_temps, marker='o', color='#FF6B6B', linewidth=2)
        ax1.set_title (f'5-Day Weather Forecast for {city}', fontsize=14, fontweight='bold')
        ax1.set_ylabel ('Temperature (°C)')
        ax1.grid (True, alpha=0.3)
        ax1.fill_between (dates, avg_temps, alpha=0.3, color='#FF6B6B')

        ax2.bar (dates, avg_humidity, color = '#4ECDC4', alpha = 0.7)
        ax2.set_ylabel ('Humidity (%)')
        ax2.grid (True, alpha = 0.3)

        ax3.plot (dates, avg_wind, marker='s', color='#45B7D1', linewidth=2)
        ax3.set_ylabel ('Wind Speed (m/s)')
        ax3.set_xlabel ('Date')
        ax3.grid (True, alpha=0.3)
        ax3.fill_between (dates, avg_wind, alpha=0.3, color='#45B7D1')

        for ax in [ax1, ax2, ax3]:
            ax.tick_params(axis = 'x', rotation = 45)

        plt.tight_layout()
        plt.show()

    def compare_cities (self, cities):
        print ("\n" + "="*60)
        print ("CITY WEATHER COMPARISON")
        print ("="*60)

        city_data = []
        for city in cities:
            weather = self.get_current_weather(city)
            if weather: 
                city_data.append(weather)
                emoji = self.get_weather_emoji (weather['weather_main'])
                print (f"{emoji} {weather['city']:<15} | {weather['temperature']:>6.1f}°C | {weather['description']:<20} | Humidity: {weather['humidity']:>3}%")

        print ("="*60)

        if len(city_data) > 1:
            cities_names = [data['city'] for data in city_data]
            temperatures = [data['temperature'] for data in city_data]
            humidity = [data['humidity'] for data in city_data]

            fig, (ax1, ax2) = plt.subplots (1, 2, figsize = (14, 6))

            bars1 = ax1.bar (cities_names, temperatures, color = '#FF6B6B', alpha = 0.7)
            ax1.set_title ('Temperature Comparison', fontweight = 'bold')
            ax1.set_ylabel ('Temperature (°C)')
            ax1.tick_params (axis = 'x', rotation = 45)

            for bar, temp in zip (bars1, temperatures): 
                height = bar.get_height()
                ax1.text (bar.get_x() + bar.get_width()/2., height + 0.5, f'{temp:.1f}°C', ha = 'center', va = 'bottom')

            bars2 = ax2.bar(cities_names, humidity, color='#4ECDC4', alpha=0.7)
            ax2.set_title('Humidity Comparison', fontweight='bold')
            ax2.set_ylabel('Humidity (%)')
            ax2.tick_params(axis='x', rotation=45)
            
            for bar, hum in zip(bars2, humidity):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1, f'{hum}%', ha='center', va='bottom')

            plt.tight_layout()
            plt.show()

    #the actual interactive dashboard
    def run_dashboard (self): 
        print ("Welcome to this weird Dashboard.. I guess")
        print ("Note again: You need an API key from OpenWeatherMap to use this")
        print ("Get one at: https://openweathermap.org/api")
        print("\n✅  Key is set! Ready to get real weather data.")

        while True: 
            print("\n" + "="*30)
            print("🌤️  WEATHER DASHBOARD MENU")
            print("="*30)
            print("1. Current Weather for a City")
            print("2. 24-Hour Temperature Forecast")
            print("3. 5-Day Weather Forecast Chart")
            print("4. Compare Multiple Cities")
            print("5. Exit")
            print("="*30)

            choice = input ("Choose an option between 1-5: ")

            if choice == '1': 
                city = input ("City Name: ")
                weather = self.get_current_weather(city)
                self.display_current_weather(weather)

            elif choice == '2':
                city = input("Enter city name: ")
                forecast = self.get_5_day_forecast(city)
                if forecast:
                    self.create_temperature_chart(forecast, city)
                
            elif choice == '3':
                city = input("Enter city name: ")
                forecast = self.get_5_day_forecast(city)
                if forecast:
                    self.create_weather_summary_chart(forecast, city)
                
            elif choice == '4':
                cities_input = input("Enter cities separated by commas (e.g., London,Paris,Tokyo): ")
                cities = [city.strip() for city in cities_input.split(',')]
                if cities:
                    self.compare_cities(cities)
                
            elif choice == '5':
                print("Thanks for using Weather Dashboard! 🌈")
                break
                
            else:
                print("Invalid choice! Please try again.")


# experimental demo if the user dont have API
def demo_mode():
    print("🌤️  WEATHER DASHBOARD - DEMO MODE")
    print ("="*30)

    sample_weather = {
        'city': 'London',
        'country': 'UK',
        'temperature': 18.5,
        'feels_like': 17.2,
        'humidity': 65,
        'pressure': 1013,
        'description': 'Partly Cloudy',
        'weather_main': 'Clouds',
        'wind_speed': 3.2,
        'wind_direction': 180,
        'visibility': 10000,
        'sunrise': datetime.now().replace(hour=6, minute=30),
        'sunset': datetime.now().replace(hour=20, minute=15),
        'timestamp': datetime.now()
    }

    dashboard = WeatherDashboard()
    dashboard.display_current_weather(sample_weather)

    sample_forecast = []
    base_time = datetime.now()

    for i in range (24): 
        sample_forecast.append({
            'datetime': base_time + timedelta(hours=i*3),
            'temperature': 18 + np.sin(i/4) * 5 + np.random.random() * 2,
            'description': 'Partly Cloudy',
            'humidity': 60 + np.random.randint(-10, 10),
            'wind_speed': 3 + np.random.random() * 2
        })
    print ("\nGenerating sample temp chart...")
    dashboard.create_temperature_chart (sample_forecast, "London (Demo)")

if __name__ == "__main__": 
    dashboard = WeatherDashboard()
    dashboard.run_dashboard()