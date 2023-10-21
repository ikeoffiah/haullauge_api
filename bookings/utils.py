import requests
from authentication.models import User
from core.settings import FCM_SERVER_KEY
import math
from datetime import datetime

#this would be used to calculate the distance of a truck from the a location it is booked

def haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Differences in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate the distance
    distance = R * c

    return distance


def format_string_datetime(date_value, time_value):
    print(date_value)
    print(time_value)
    print("----------------------------------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    combined_datetime = datetime.strptime(date_value + " " + f"{time_value}", "%Y-%m-%d %I:%M %p")
    formatted_datetime = combined_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return formatted_datetime

def calculatePrice(distance, load, fuel_price):
    if load < 10:
        return round(lessthan10(distance, load, fuel_price)/2)
    else:
        return round(others(distance, load, fuel_price)/2)

def lessthan10(distance, load, fuel_price):
    if distance < 50:
        price = (load * distance * fuel_price) / 4
        return price
    if distance >49 and distance < 100:
        price = (load * distance * fuel_price) / 6
        return price
    if distance >99 and distance < 200:
        price = (load * distance * fuel_price) / 8
        return price
    if distance > 199 and distance < 400:
        price = (load * distance * fuel_price) / 10
        return price
    if distance > 399 and distance < 800:
        price = (load * distance * fuel_price) / 12
        return price
    if distance > 799:
        price = (load * distance * fuel_price) / 14
        return price


def others(distance, load, fuel_price):
    if distance < 50:
        price = (load * distance * fuel_price) / 6
        return price
    if distance >49 and distance < 100:
        price = (load * distance * fuel_price) / 12
        return price
    if distance >99 and distance < 200:
        price = (load * distance * fuel_price) / 15
        return price
    if distance > 199 and distance < 400:
        price = (load * distance * fuel_price) / 18
        return price
    if distance > 399 and distance < 800:
        price = (load * distance * fuel_price) / 20
        return price
    if distance > 799:
        price = (load * distance * fuel_price) / 22
        return price



def send_push_notification(user_id,message, Title):
    user = User.objects.get(id=user_id)
    print("here----------")
    device_token = user.device_token
    fcm_url = 'https://fcm.googleapis.com/fcm/send'
    print(device_token)
    headers = {
        'Authorization': f'key={FCM_SERVER_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'to': device_token,
        'notification': {
            'title': Title,
            'body': message,
            'sound': 'default',
        },
    }

    response = requests.post(fcm_url, headers=headers, json=data)
    response_data = response.json()
    if 'error' in response_data:
        return False
    print("Trueeee")
    return True


