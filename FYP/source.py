from pymongo import MongoClient
import face_recognition
import numpy as np
import cv2
from rfidReader import getUID

uid = None
while (uid == None):
    print("Waiting for RFID tag...")
    uid = getUID()
    print (uid)

# MongoDB client setup
client = MongoClient('mongodb+srv://rar29:uiwU4u6ZHBRLryVb@cluster0.e85xuag.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['mydatabase']
collection = db['users']

def load_encodings_from_db():
    user_list_encodings = []
    
    users = collection.find()  # Retrieve all users
    name = "Unknown"
    for user in users:
        # Decode encodings stored as lists in the database
        if uid == user['ID']:
            name = user['name']
            for enc in user['encodings']:
                user_list_encodings.append(np.array(enc))
        
                
    
    return user_list_encodings, name

UserEncodings, userName = load_encodings_from_db()
print(userName)


def recognize_face2(frame, list_encodings, list_namnes,tolereance=0.6):
    
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    face_names = []
    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        match = face_recognition.compare_faces(list_encodings, face_encoding, tolereance)
        name = "Unknown"
        for n, m in zip(list_namnes, match):
            if m:
                name = n
        face_names.append((name, (top, right, bottom, left)))
    return face_names

video_capture = cv2.VideoCapture(1) # 0 for the built-in camera, 1 for an external camera
process = True

while True:
    ret, frame = video_capture.read()
    if process:
        face_names = recognize_face2(frame, UserEncodings, [userName])
    process = not process
    for name, (top, right, bottom, left) in face_names:
        cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
video_capture.release()









































    
