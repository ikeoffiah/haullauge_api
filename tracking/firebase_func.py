import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def create_firebase_doc(document_id, log, lat, distance, time, duration, date):
    location_data = {
      'currentLocation': {
        "latitude": lat,
        "longitude": log
      },
      'date': date,
      'distance': distance,
      'time': time,
      'duration': duration
    }

    collection_name = "user"
    doc_ref = db.collection(collection_name).document(document_id)
    subcollection_ref = doc_ref.collection("location")
    subcollection_ref.add(location_data)
    return True
