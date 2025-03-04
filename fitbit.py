import requests
from datetime import datetime
from db import save_to_db
import sys

def get_fitbit_data(access_token, email):
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Datos de actividad diaria (pasos)
    activity_url = "https://api.fitbit.com/1/user/-/activities/date/today.json"
    response = requests.get(activity_url, headers=headers)
    activity_data = response.json()
    steps = activity_data.get("summary", {}).get("steps", 0)

    # Frecuencia cardíaca promedio diaria
    heart_rate_url = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/40min.json"
    response = requests.get(heart_rate_url, headers=headers)
    heart_rate_data = response.json()
    heart_rate = heart_rate_data.get("activities-heart", [{}])[0].get("value", {}).get("restingHeartRate", 0)

    # Sueño
    sleep_url = "https://api.fitbit.com/1.2/user/-/sleep/date/today.json"
    response = requests.get(sleep_url, headers=headers)
    sleep_data = response.json()
    sleep_minutes = sum([log.get("minutesAsleep", 0) for log in sleep_data.get("sleep", [])])

    # Guardar en la base de datos
    date = datetime.now().strftime("%Y-%m-%d")
    save_to_db(email, date, steps, heart_rate, sleep_minutes)

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python fitbit.py <access_token> <email>")
        sys.exit(1)

    access_token = sys.argv[1]
    email = sys.argv[2]

    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Datos de actividad diaria (pasos)
    activity_url = "https://api.fitbit.com/1/user/-/activities/date/today.json"
    response = requests.get(activity_url, headers=headers)
    activity_data = response.json()
    steps = activity_data.get("summary", {}).get("steps", 0)

    # Frecuencia cardíaca promedio diaria
    heart_rate_url = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/40min.json"
    response = requests.get(heart_rate_url, headers=headers)
    heart_rate_data = response.json()
    heart_rate = heart_rate_data.get("activities-heart", [{}])[0].get("value", {}).get("restingHeartRate", 0)

    # Sueño
    sleep_url = "https://api.fitbit.com/1.2/user/-/sleep/date/today.json"
    response = requests.get(sleep_url, headers=headers)
    sleep_data = response.json()
    sleep_minutes = sum([log.get("minutesAsleep", 0) for log in sleep_data.get("sleep", [])])

    # Print data before saving to database
    print(f"Email: {email}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Steps: {steps}")
    print(f"Heart Rate: {heart_rate}")
    print(f"Sleep Minutes: {sleep_minutes}")

    # Guardar en la base de datos
    date = datetime.now().strftime("%Y-%m-%d")
    save_to_db(email, date, steps, heart_rate, sleep_minutes)