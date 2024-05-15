import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition
import os
from rfidReader import getUID
import numpy as np
from pymongo import MongoClient, errors



photos = []
photo_labels = []
face_encodings = []
camera = cv2.VideoCapture(0)
name = ""  

def callme():
    print("waiting for RFID tag")
    uid = getUID()
    print(uid)

    def take_photo():
        global camera, photos, photo_labels, face_encodings

        if len(photos) < 7:
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
            warning_label.config(text="Maximum number of photos (7) reached. Click 'Register User' to proceed.")
            capture_button.config(state=tk.DISABLED)

    def register_user():
        global name
        name = name_entry.get()
        print(f"Number of face encodings: {len(face_encodings)}")
        print("Face Encodings:")
        for encoding in face_encodings:
            print(encoding)
        root.quit()

    root = tk.Tk()
    root.title("Name Input")
    root.configure(bg='white')
    root.geometry("800x600")

    top_frame = tk.Frame(root, height=50, bg='white')
    top_frame.pack(side=tk.TOP, fill=tk.X)

    label = tk.Label(root, text="Enter your name:", font=('Helvetica', 14), bg='white')
    label.pack(pady=(20, 10))

    name_entry = tk.Entry(root, font=('Helvetica', 14), width=30, bd=1, highlightbackground='black', highlightthickness=2, relief='solid')
    name_entry.pack(pady=10)

    uid_label = tk.Label(root, text=f"UID: {uid}", font=('Helvetica', 14), bg='white')
    uid_label.pack(pady=10)

    warning_label = tk.Label(root, text="", font=('Helvetica', 14), bg='white', fg='red')
    warning_label.pack(pady=10)

    button_style = {'font': ('Helvetica', 16), 'bg': 'black', 'fg': 'white', 'padx': 10, 'pady': 10, 'width': 15}

    capture_button = tk.Button(root, text="Take Photo", command=take_photo, **button_style)
    capture_button.pack(pady=20)

    register_button = tk.Button(root, text="Register User", command=register_user, **button_style)
    register_button.pack(pady=20)

    photo_frame = tk.Frame(root, bg='white')
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
