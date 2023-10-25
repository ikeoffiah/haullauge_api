import threading
from .models import Notifications
from authentication.models import User

def create_notification(user_id,message, Title):
    return CreateNoficationThread(user_id,message,Title)

class CreateNoficationThread(threading.Thread):

    def __init__(self,user_id, message, Title):
        self.user_id = user_id
        self.message = message
        self.Title = Title
        threading.Thread.__init__(self)

    def run(self):
        user = User.objects.get(id= self.user_id)
        notification = Notifications.objects.create(
            user = user,
            message = self.message,
            title = self.Title
        )
        return notification