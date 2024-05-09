import pyotp
import requests
from .models import User
from core.settings import CLIENT_ID, CLIENT_SECRET
import threading
from django.utils import timezone
import uuid
import cloudinary.uploader


def upload_to_cloudinary(photo):
    upload_result = cloudinary.uploader.upload(photo)
    return upload_result['secure_url']


def generate_send_otp(phone_number):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret, interval=300)
    otp = totp.now()
    content = f"Your otp is {otp}. It expires in 5 minutes"
    send_sms(phone_number, content)
    return {'secret': secret}


def send_drivers_msg(driver_details, messenger):

    for driver in driver_details:
        content = f"Hi {driver['first_name']}, {messenger} just registered you as a driver on the Hallauge platform \n" \
                  f"Login with\n " \
                  f"Phone number: {driver['phone_number']}\n Password:{driver['first_name']}_{driver['last_name']}"
        # send_sms(driver['phone_number'], content)
    return True




def send_sms(phone_number, content):
    url = f"https://smsc.hubtel.com/v1/messages/send?clientsecret={CLIENT_SECRET}&clientid={CLIENT_ID}&from=haullauge&to={phone_number}&content={content}"
    SMSThread(url).start()



def verify_otp(secret_key, otp, validity=300):
    totp = pyotp.TOTP(secret_key, interval=validity)
    return totp.verify(otp)


def success_message_helper(data,message):
    return {
        'data':data,
        'detail':message
    }

def error_message_helper(error,message):
    return {
        'error':error,
        'detail':message
    }


def system_error_message_helper(errors):
    error_message = ""
    print(errors)
    for key, value in errors.items():

        if isinstance(value, list):
            error_message = error_message + f'{value[0]},'
        elif isinstance(value, dict):
            for key, valuez in value.items():
                error_message = error_message + f'{valuez[0]},'
        else:
            error_message = error_message + f'{value},'
    return error_message_helper(errors,error_message)


def authenticate_user_with_password(phone_number, password, device_token):

    user = User.objects.get(phone_number=phone_number)

    if user.check_password(password):
        user.last_login = timezone.now()
        user.device_token = device_token
        user.save()
        return True
    else:
        return False

def active_user_verification(phone_number):
    user = User.objects.get(phone_number=phone_number)

    if not user.is_active:
        return False
    return True

def get_user_token(phone_number):
    user =  User.objects.get(phone_number=phone_number)
    token = user.tokens()
    return token

def generateReferenceId():
    reference = 'haul_book_' + str(uuid.uuid4())
    return reference


class SMSThread(threading.Thread):
    def __init__(self,url):
        self.url = url
        threading.Thread.__init__(self)

    def run(self):
        return requests.get(self.url)
