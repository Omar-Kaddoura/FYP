from pymongo import MongoClient
import face_recognition
import numpy as np
import cv2
from rfidReader import getUID
import threading


client = MongoClient('mongodb+srv://rar29:uiwU4u6ZHBRLryVb@cluster0.e85xuag.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['mydatabase']
collection = db['users']


user_encodings = []
user_name = "Unknown"


def load_encodings_from_db(uid):
    global user_encodings, user_name
    user_encodings = []
    user_name = "Unknown"
    user = collection.find_one({"ID": uid}) 
    if user:
        user_name = user['name']
        for enc in user['encodings']:
            user_encodings.append(np.array(enc))


def recognize_face(frame, list_encodings, list_names, tolerance=0.6):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    face_names = []
    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        match = face_recognition.compare_faces(list_encodings, face_encoding, tolerance)
        name = "Unknown"
        for n, m in zip(list_names, match):
            if m:
                name = n
        face_names.append((name, (top, right, bottom, left)))
    return face_names


def rfid_scanning():
    while True:
        print("Waiting for RFID tag...")
        uid = getUID()
        print(uid)
        load_encodings_from_db(uid)
        print("User:", user_name)


def camera_feed():
    video_capture = cv2.VideoCapture(0)
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error reading frame from the video capture.")
            break

        face_names = recognize_face(frame, user_encodings, [user_name])


        for name, (top, right, bottom, left) in face_names:
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)


        cv2.imshow('Video', frame)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    
    video_capture.release()
    cv2.destroyAllWindows()


def main():
    rfid_thread = threading.Thread(target=rfid_scanning)
    camera_thread = threading.Thread(target=camera_feed)

    rfid_thread.start()
    camera_thread.start()

    rfid_thread.join()
    camera_thread.join()

if __name__ == "__main__":
    main()
