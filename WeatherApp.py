import requests
from bs4 import BeautifulSoup
from win10toast import ToastNotifier
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Import PIL modules for image handling
from ttkthemes import ThemedTk
import threading
import multiprocessing

# Create an object of the ToastNotifier class
n = ToastNotifier()

# Define a function to fetch weather data by latitude and longitude from OpenWeatherMap API
def get_weather_data(lat, lon):
    api_key = "836f6fbd2f064dfa31368b7e11efb4e2"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",  # Request temperature in Celsius
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return str(e)

# Define a function to geocode a city name and retrieve its coordinates
def get_coordinates(city_name):
    geocoding_api_key = "836f6fbd2f064dfa31368b7e11efb4e2"
    geocoding_base_url = "http://api.openweathermap.org/geo/1.0/direct?"

    params = {
        "q": city_name,
        "apikey": geocoding_api_key,
    }
    
    try:
        response = requests.get(geocoding_base_url, params=params)
        response.raise_for_status()
        geocoding_data = response.json()
        
        # Assuming geocoding_data is a list, you can access the first result
        if len(geocoding_data) > 0:
            first_result = geocoding_data[0]
            print(geocoding_data)
            lat = first_result.get("lat")
            lon = first_result.get("lon")
            return lat, lon
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        return None, None
    

def show_notification(city_name, description, temperature_celsius, temperature_fahrenheit):
    result = f"Weather in {city_name}:\n{description.capitalize()}\nTemperature: {temperature_celsius}°C ({temperature_fahrenheit}°F)"
    n.show_toast("Live Weather Update", result, duration=50)

notification_process = None

def get_weather_info():
    global notification_process  # Use the global notification_process variable
    
    # Check if a notification process is already running
    if notification_process and notification_process.is_alive():
        messagebox.showinfo("Notification in Progress", "A weather notification is already being displayed.")
        return
    
    city_name = city_entry.get()
    
    # Get the coordinates using geocoding
    latitude, longitude = get_coordinates(city_name)
    
    if latitude is not None and longitude is not None:
        # Fetch weather data using the obtained coordinates
        weather_data = get_weather_data(latitude, longitude)
        
        if isinstance(weather_data, dict) and "main" in weather_data and "weather" in weather_data:
            temperature_celsius = round(weather_data["main"]["temp"])
            temperature_fahrenheit = round((temperature_celsius * 9/5) + 32)
            description = weather_data["weather"][0]["description"]
            
            # Show notification in a separate process to avoid blocking the main thread
            notification_thread = threading.Thread(target=show_notification, args=(city_name, description, temperature_celsius, temperature_fahrenheit))
            notification_thread.start()
        else:
            messagebox.showerror("Weather Data Not Found", f"Unable to retrieve weather data for {city_name}.")
    else:
        messagebox.showerror("Geocoding Error", f"Unable to retrieve coordinates for {city_name}")





# Create a ThemedTk window with a dark theme
root = ThemedTk(theme="equilux")
root.title("Weather App")

# Load the background image using PIL
bg_image = Image.open("Images/santorio.jpg")  # Replace "santorio.jpg" with your image file
bg_photo = ImageTk.PhotoImage(bg_image)

# Define the "Ask Again" function
def ask_again():
    # Clear the entry field for a new city
    city_entry.delete(0, tk.END)
    
# Create a Canvas widget to display the image as the background and fill the entire window
canvas = tk.Canvas(root, width=bg_image.width, height=bg_image.height)
canvas.pack()

# Place the image on the Canvas
canvas.create_image(0, 0, anchor=tk.NW, image=bg_photo)

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# Create and place a label and an entry field for entering the city name inside the Canvas
city_label = tk.Label(canvas, text="Enter the city name:")
city_label.place(x=20, y=20)

city_entry = tk.Entry(canvas)
city_entry.place(x=20, y=50)

# Create and place a button to fetch weather information inside the Canvas
get_weather_button = tk.Button(canvas, text="Get Weather Info", command=get_weather_info)
get_weather_button.place(x=20, y=80)


# Create an "Ask Again" button to request weather information for another city
ask_again_button = tk.Button(canvas, text="Ask Again", command=ask_again)
ask_again_button.place(x=20, y=110)

# Set the minimum and maximum window size to make it fixed
width = 300  # Your desired width
height = 300  # Your desired height
root.minsize(width, height)
root.maxsize(width, height)

# Load the new logo image
new_logo = tk.PhotoImage(file="Images/logoTemperature.png")

# Set the new logo as the app's icon
root.iconphoto(True, new_logo)



# Call the center_window function to center the window
center_window(root)



# Start the GUI event loop
root.mainloop()