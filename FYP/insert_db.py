from pymongo import MongoClient, errors
import face_recognition
import numpy as np
import face_recognition
from anas_encodings import anas_encodings
from rahaf_encodings import rahaf_encodings  
 
from assaad_encodings import assaad_encodings 
from atieh_encodings import atieh_encodings 
from hamza_encodings import hamza_encodings 
from kaddoura_encodings import kaddoura_encodings





client = MongoClient('mongodb+srv://rar29:uiwU4u6ZHBRLryVb@cluster0.e85xuag.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

db = client['mydatabase']
collection = db['users']



rahaf_encodings_list = [encoding.tolist() for encoding in rahaf_encodings]
anas_encodings_list = [encoding.tolist() for encoding in anas_encodings]
assaad_encodings_list = [encoding.tolist() for encoding in assaad_encodings]
atieh_encodings_list = [encoding.tolist() for encoding in atieh_encodings]
hamza_encodings_list = [encoding.tolist() for encoding in hamza_encodings]
kaddoura_encodings_list = [encoding.tolist() for encoding in kaddoura_encodings]






users_documents = [
    {
        "name": "Rahaf",
        "encodings": rahaf_encodings_list,  
        "ID": "1",
    },
    {
        "name": "Atieh",
        "encodings": atieh_encodings_list, 
        "ID": "2",
    },
    {
        "name": "Hamza",
        "encodings": hamza_encodings_list,  
        "ID": "3",
    },
    {
        "name": "Kaddoura",
        "encodings": kaddoura_encodings_list,  
        "ID": "4",
    },
    {
        "name": "Hamza",
        "encodings": hamza_encodings_list,  
        "ID": "5",
    },
    {
        "name": "Anas",
        "encodings": anas_encodings_list,  
        "ID": "6",
    },
    {
        "name": "Assaad",
        "encodings": assaad_encodings_list,  
        "ID": "7",
    },
]

try:
    for user in users_documents:
        result = collection.update_one(
            {"ID": user["ID"]},  # Use the correct field for lookup
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
