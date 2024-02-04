import face_recognition
import cv2
import numpy as np 
video_capture = cv2.VideoCapture(0)

class Person:
    def __init__(self, name, image_path):
        self.name = name
        self.image = face_recognition.load_image_file(image_path)
        self.encoding = face_recognition.face_encodings(self.image)[0]

Omar = Person("Omar Kaddoura", "C:\FYP\Face Detection & Recognition\myslef.jpg")
Jad = Person("Jad", "C:\FYP\jad.jpg")
people = [Omar, Jad]

people_encoding = [person.encoding for person in people]

face_locations = []
face_encodings = []
face_names = []
process=True
while True:
    ret, frame = video_capture.read()
    if process:
        resized = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)
        face_encodings = face_recognition.face_encodings(rgb, face_locations)
        face_names = []
        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            match = face_recognition.compare_faces(people_encoding, face_encoding)
            name = "Unknown"
            
            for person, m in zip(people, match):
                if m:
                    name = person.name
            face_names.append((name, (top, right, bottom, left)))
    process = not process
    
    
    
    # display
    for name, (top, right, bottom, left) in face_names:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
video_capture.release()
cv2.destroyAllWindows()