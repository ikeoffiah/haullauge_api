import threading
from .models import Account
from authentication.models import User
from datetime import timedelta
from django.utils import timezone
from bookings.models import Bookings


def create_account(driver_id, pickUp_price, delivery_price, booking):
    total_price = pickUp_price + delivery_price

    debt = int(0.1 * total_price)
    today = timezone.now().date()
    new_date = today + timedelta(days=7)
    user = User.objects.get(id=driver_id)
    avaliable_booking = Account.objects.filter(latest_booking=booking, user=user)
    user_account = Account.objects.filter(user=user)

    if user_account.exists() and not avaliable_booking.exists():

        return NewUserUpdateAccountThread(total_price,debt, new_date, booking, user).start()
    if avaliable_booking.exists():
        if avaliable_booking[0].is_paid:
            new_date = avaliable_booking[0].deadline
            UpdateAccountThread(total_price,debt, new_date, user).start()
        else:
            return UpdateAccountThread(total_price, debt, new_date,user).start()

    if user and not avaliable_booking.exists():
        return CreateAccountThread(user, total_price,debt, new_date, booking).start()

class CreateAccountThread(threading.Thread):
    def __init__(self,user, total_price,debt, new_date, booking):
        self.user = user
        self.total_price = total_price
        self.debt = debt
        self.new_date = new_date
        self.booking = booking
        threading.Thread.__init__(self)

    def run(self):
        account = Account.objects.create(
        user = self.user,
        amount= self.total_price,
        debt = self.debt,
        deadline = self.new_date,
        latest_booking= self.booking
        )
        return account


class UpdateAccountThread(threading.Thread):
    def __init__(self,total_price,debt, new_date, user):

        self.total_price = total_price
        self.debt = debt
        self.new_date = new_date
        self.user = user
        threading.Thread.__init__(self)

    def run(self):
        user_account = Account.objects.get(user=self.user)

        user_account.amount = self.total_price
        user_account.debt = self.debt
        user_account.deadline = self.new_date

        user_account.save()

        return user_account

class NewUserUpdateAccountThread(threading.Thread):
    def __init__(self, total_price,debt, new_date, booking, user):

        self.total_price = total_price
        self.debt = debt
        self.new_date = new_date
        self.booking = booking
        self.user = user

        threading.Thread.__init__(self)

    def run(self):
        user_account = Account.objects.get(user=self.user)

        user_account.amount= self.total_price
        user_account.debt = self.debt
        user_account.deadline = self.new_date
        user_account.latest_booking= self.booking
        user_account.save()

        return user_account