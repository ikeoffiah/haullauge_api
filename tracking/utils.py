import uuid
import threading
from .models import TrackLocation
from bookings.models import Locations
from .firebase_func import create_firebase_doc

def generate_track_id():
    track_id =str(uuid.uuid4()).replace("-", "")
    return track_id

def create_track(pickup, delivery, log, lat, distance, time, duration, date, location_name, booking):
    track_id = generate_track_id()
    return CreateTrackThread(pickup, delivery, log, lat, distance, time, duration, date, location_name, booking, track_id).start()




class CreateTrackThread(threading.Thread):
    def __init__(self,pickup, delivery, log, lat, distance, time, duration, date, location_name, booking, track_id):
        self.pickup = pickup
        self.delivery = delivery
        self.distance = distance
        self.time = time
        self.duration = duration
        self.log = log
        self.lat = lat
        self.date = date
        self.location_name = location_name
        self.booking = booking
        self.track_id = track_id
        threading.Thread.__init__(self)

    def run(self):
        currentLocation = Locations.objects.create(
            longitude= self.log,
            latitude = self.lat,
            name= self.location_name
        )
        track = TrackLocation.objects.create(
            pickup_location= self.pickup,
            delivery_location = self.delivery,
            last_location = currentLocation,
            booking = self.booking,
            tracking_id= self.track_id
        )

        create_firebase_doc(self.track_id,self.log,self.lat,self.distance,self.time, self.duration,self.date)

        return track

