from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import requests

bg_color = "#1b2a3a"
card_color = "#2a3f55"
blue = "#4aa3df"
white = "#ffffff"
grey = "#b0bec5"

codes = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Cloudy",
    45: "Fog",
    48: "Fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    71: "Snow",
    73: "Snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Rain showers",
    82: "Heavy showers",
    95: "Thunderstorm",
    96: "Thunderstorm",
    99: "Thunderstorm",
}


def get_condition(code):
    if code in codes:
        return codes[code]
    return "Unknown"


def load_history():
    try:
        f = open("history.txt", "r")
        lines = f.read().split("\n")
        f.close()
    except:
        return []
    cities = []
    for c in lines:
        if c != "" and c not in cities:
            cities.append(c)
    cities.reverse()
    return cities[:8]


def save_city(name):
    f = open("history.txt", "a")
    f.write(name + "\n")
    f.close()
    city_box["values"] = load_history()


def clear_history():
    f = open("history.txt", "w")
    f.close()
    city_box["values"] = []
    messagebox.showinfo("Done", "History cleared")


def get_weather(event=None):
    city = city_box.get().strip()

    if city == "":
        messagebox.showerror("Error", "Please enter a city name")
        return

    status_label.config(text="Loading...")
    root.update()

    try:
        url1 = "https://geocoding-api.open-meteo.com/v1/search?name=" + city + "&count=1"
        data1 = requests.get(url1, timeout=10).json()

        if "results" not in data1:
            status_label.config(text="")
            messagebox.showerror("Error", "City not found")
            return

        lat = data1["results"][0]["latitude"]
        lon = data1["results"][0]["longitude"]
        name = data1["results"][0]["name"]
        country = data1["results"][0].get("country", "")

        if unit.get() == 1:
            unit_name = "celsius"
            sym = " C"
        else:
            unit_name = "fahrenheit"
            sym = " F"

        url2 = ("https://api.open-meteo.com/v1/forecast?latitude=" + str(lat) +
                "&longitude=" + str(lon) +
                "&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code" +
                "&daily=weather_code,temperature_2m_max,temperature_2m_min" +
                "&temperature_unit=" + unit_name +
                "&timezone=auto&forecast_days=5")
        data2 = requests.get(url2, timeout=10).json()

        cur = data2["current"]

        city_label.config(text=name + ", " + country)
        temp_label.config(text=str(round(cur["temperature_2m"])) + sym)
        cond_label.config(text=get_condition(cur["weather_code"]))
        feels_value.config(text=str(round(cur["apparent_temperature"])) + sym)
        humidity_value.config(text=str(cur["relative_humidity_2m"]) + " %")
        wind_value.config(text=str(cur["wind_speed_10m"]) + " km/h")

        daily = data2["daily"]
        for i in range(5):
            date = datetime.strptime(daily["time"][i], "%Y-%m-%d")
            day_labels[i].config(text=date.strftime("%a %d"))
            day_conds[i].config(text=get_condition(daily["weather_code"][i]))
            day_temps[i].config(text=str(round(daily["temperature_2m_max"][i])) + " / " +
                                str(round(daily["temperature_2m_min"][i])))

        save_city(name)
        status_label.config(text="Last updated: " + datetime.now().strftime("%I:%M %p"))

    except:
        status_label.config(text="")
        messagebox.showerror("Error", "Could not get data. Check your internet")


root = Tk()
root.title("Weather Tracker")
root.geometry("700x600")
root.config(bg=bg_color)
root.resizable(False, False)

Label(root, text="Weather Tracker", font=("Arial", 22, "bold"),
      bg=bg_color, fg=white).pack(pady=(18, 8))

top = Frame(root, bg=bg_color)
top.pack()

city_box = ttk.Combobox(top, font=("Arial", 13), width=24, values=load_history())
city_box.grid(row=0, column=0, padx=5, ipady=3)
city_box.bind("<Return>", get_weather)

Button(top, text="Search", font=("Arial", 11, "bold"), bg=blue, fg="black",
       padx=14, command=get_weather).grid(row=0, column=1, padx=5)

Button(top, text="Clear history", font=("Arial", 9),
       command=clear_history).grid(row=0, column=2, padx=5)

unit = IntVar()
unit.set(1)
uf = Frame(root, bg=bg_color)
uf.pack(pady=6)
Radiobutton(uf, text="Celsius", variable=unit, value=1, bg=bg_color, fg=white,
            selectcolor=card_color, activebackground=bg_color, font=("Arial", 10),
            command=get_weather).pack(side=LEFT, padx=8)
Radiobutton(uf, text="Fahrenheit", variable=unit, value=2, bg=bg_color, fg=white,
            selectcolor=card_color, activebackground=bg_color, font=("Arial", 10),
            command=get_weather).pack(side=LEFT, padx=8)

card = Frame(root, bg=card_color)
card.pack(fill=X, padx=30, pady=10)

city_label = Label(card, text="Search a city to start", font=("Arial", 16, "bold"),
                   bg=card_color, fg=white)
city_label.pack(pady=(14, 0))

temp_label = Label(card, text="--", font=("Arial", 40, "bold"), bg=card_color, fg=blue)
temp_label.pack()

cond_label = Label(card, text="", font=("Arial", 14), bg=card_color, fg=grey)
cond_label.pack(pady=(0, 10))

info = Frame(card, bg=card_color)
info.pack(pady=(0, 14))


def make_box(title):
    box = Frame(info, bg=bg_color, width=150, height=60)
    box.pack(side=LEFT, padx=8)
    box.pack_propagate(False)
    Label(box, text=title, font=("Arial", 9), bg=bg_color, fg=grey).pack(pady=(8, 0))
    value = Label(box, text="--", font=("Arial", 13, "bold"), bg=bg_color, fg=white)
    value.pack()
    return value


feels_value = make_box("Feels like")
humidity_value = make_box("Humidity")
wind_value = make_box("Wind speed")

Label(root, text="5 Day Forecast", font=("Arial", 13, "bold"),
      bg=bg_color, fg=white).pack(anchor=W, padx=32)

fc = Frame(root, bg=bg_color)
fc.pack(pady=8)

day_labels = []
day_conds = []
day_temps = []

for i in range(5):
    f = Frame(fc, bg=card_color, width=118, height=100)
    f.grid(row=0, column=i, padx=5)
    f.pack_propagate(False)

    d = Label(f, text="--", font=("Arial", 10, "bold"), bg=card_color, fg=white)
    d.pack(pady=(10, 2))
    c = Label(f, text="", font=("Arial", 9), bg=card_color, fg=grey, wraplength=100)
    c.pack()
    t = Label(f, text="", font=("Arial", 11), bg=card_color, fg=white)
    t.pack(pady=4)

    day_labels.append(d)
    day_conds.append(c)
    day_temps.append(t)

status_label = Label(root, text="", font=("Arial", 9), bg=bg_color, fg=grey)
status_label.pack(side=BOTTOM, pady=6)

root.mainloop()