import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition
import os
from rfidReader import getUID
import numpy as np
from pymongo import MongoClient, errors

# Initialize global variables
photos = []
photo_labels = []
face_encodings = []
camera = cv2.VideoCapture(0)
def callme():
    
    print("waiting for RFID tag")
    uid = getUID()
    print(uid)

    def store_name():
        global name
        name = name_entry.get()

    def take_photo():
        global camera, photos, photo_labels, face_encodings

        if len(photos) < 7:  # Check if the limit has not been reached
            ret, frame = camera.read()
            if ret:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img = img.resize((200, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                photos.append(photo)

                photo_label = tk.Label(photo_frame, image=photo)
                photo_label.image = photo
                photo_label.pack(side=tk.LEFT, padx=5)
                photo_labels.append(photo_label)

                img.save(f"photo_{len(photos) - 1}.jpg")

                image = face_recognition.load_image_file(f"photo_{len(photos) - 1}.jpg")
                face_encodings_in_image = face_recognition.face_encodings(image)
                if face_encodings_in_image:
                    face_encoding = face_encodings_in_image[0]
                    face_encodings.append(face_encoding)
                else:
                    print("No faces detected in the image.")
            else:
                print("Error: Failed to capture photo")
        else:
            print(f"Maximum number of photos (7) reached. Number of face encodings: {len(face_encodings)}")
            print("Face Encodings:")
            for encoding in face_encodings:
                print(encoding)
            root.quit()  # Close the interface

    root = tk.Tk()
    root.title("Name Input")
    root.geometry("800x600")

    label = tk.Label(root, text="Enter your name:")
    label.pack()

    name_entry = tk.Entry(root)
    name_entry.pack()

    store_button = tk.Button(root, text="Store Name", command=store_name)
    store_button.pack()

    capture_button = tk.Button(root, text="Take Photo", command=take_photo)
    capture_button.pack()

    photo_frame = tk.Frame(root)
    photo_frame.pack(pady=10)

    root.mainloop()
    return name, face_encodings, uid

name, user_encoding, ID = callme()


client = MongoClient('mongodb+srv://rar29:uiwU4u6ZHBRLryVb@cluster0.e85xuag.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

db = client['mydatabase']
collection = db['users']

encoding_list = [encodings.tolist() for encodings in user_encoding]
users_documents = [
    {
        "name": name,
        "encodings": encoding_list,  
        "ID": ID,
    },
]


try:
    for user in users_documents:
        result = collection.update_one(
            {"ID": user["ID"]},  
            {"$set": user},
            upsert=True
        )
        if result.upserted_id is not None:
            print(f"Inserted user ID: {user['ID']}")
        else:
            print(f"Updated user ID: {user['ID']}")

    print("All users and encodings updated/inserted successfully.")
except errors.BulkWriteError as e:
    print("Error updating/inserting:", e)
    for error_detail in e.details['writeErrors']:
        print(f"Error with user ID {error_detail['op']['ID']}: {error_detail['errmsg']}")
finally:
    client.close()
