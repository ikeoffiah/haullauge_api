import requests
from authentication.models import User
from core.settings import FCM_SERVER_KEY
from notification.utils import create_notification
import math
from datetime import datetime
import re

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




def is_valid_time_format(time_value):
    # Regular expression to match "4:30 pm" format
    pattern =  r'\d{1,2}:\d{2} [aApP][mM]'
    return re.match(pattern, time_value) is not None

def format_string_datetime(date_value, time_value):
    # Convert the time_value to a 12-hour format with 'am' or 'pm'
    is_proper = is_valid_time_format(time_value)
    if not is_proper:

        time_obj = datetime.strptime(time_value, "%H:%M").strftime("%I:%M %p")
    else:
        time_obj = time_value
    combined_datetime = datetime.strptime(date_value + " " + time_obj, "%Y-%m-%d %I:%M %p")
    formatted_datetime = combined_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return formatted_datetime

def calculatePrice(distance, load, fuel_price):
    if load < 5:
        return round(lessthan5(distance, load, fuel_price)/2)
    elif load == 5:
        return round(is5(distance, load, fuel_price)/2)
    elif load == 10:
        return round(is10(distance, load, fuel_price) / 2)
    else:
        return round(is20(distance, load, fuel_price) / 2)

def lessthan5(distance, load, fuel_price):
    if distance < 50:
        price = (load * distance * fuel_price)
        if price < 100:
            return 100
        return price
    if distance >49 and distance < 100:
        price = (load * distance * fuel_price)
        if price < 100:
            return 100
        return price
    if distance >99 and distance < 200:
        price = (load * distance * fuel_price)/1.5
        if price < 100:
            return 100
        return price
    if distance > 199 and distance < 400:
        price = (load * distance * fuel_price)/1.5
        if price < 100:
            return 100
        return price
    if distance > 399 and distance < 800:
        price = (load * distance * fuel_price)/1.5
        if price < 100:
            return 100
        return price
    if distance > 799:
        price = (load * distance * fuel_price)/1.5
        if price < 100:
            return 100
        return price


def is5(distance, load, fuel_price):
    if distance < 50:
        price = (load * distance * fuel_price) / 2.7
        return price
    if distance > 49 and distance < 100:
        price = (load * distance * fuel_price) / 4.7
        return price
    if distance > 99 and distance < 200:
        price = (load * distance * fuel_price) / 6.7
        return price
    if distance > 199 and distance < 400:
        price = (load * distance * fuel_price) / 8.7
        return price
    if distance > 399 and distance < 800:
        price = (load * distance * fuel_price) / 10.7
        return price
    if distance > 799:
        price = (load * distance * fuel_price) / 12.7
        return price

def is10(distance, load, fuel_price):
    if distance < 50:
        price = (load * distance * fuel_price) / 3.7
        return price
    if distance > 49 and distance < 100:
        price = (load * distance * fuel_price) / 5.7
        return price
    if distance > 99 and distance < 200:
        price = (load * distance * fuel_price) / 7.7
        return price
    if distance > 199 and distance < 400:
        price = (load * distance * fuel_price) / 9.7
        return price
    if distance > 399 and distance < 800:
        price = (load * distance * fuel_price) / 11.7
        return price
    if distance > 799:
        price = (load * distance * fuel_price) / 13.7
        return price


def is20(distance, load, fuel_price):
    if distance < 50:
        price = (load * distance * fuel_price) / 4.7
        return price
    if distance > 49 and distance < 100:
        price = (load * distance * fuel_price) / 6.7
        return price
    if distance > 99 and distance < 200:
        price = (load * distance * fuel_price) / 8.7
        return price
    if distance > 199 and distance < 400:
        price = (load * distance * fuel_price) / 10.7
        return price
    if distance > 399 and distance < 800:
        price = (load * distance * fuel_price) / 12.7
        return price
    if distance > 799:
        price = (load * distance * fuel_price) / 14.7
        return price

def send_push_notification(user_id,message, Title):
    user = User.objects.get(id=user_id)
    device_token = user.device_token
    fcm_url = 'https://fcm.googleapis.com/fcm/send'

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
    create_notification(user_id,message, Title)
    return True


