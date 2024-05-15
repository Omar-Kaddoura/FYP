from pymongo import MongoClient, errors
from interface import databaseEntry


client = MongoClient('mongodb+srv://rar29:uiwU4u6ZHBRLryVb@cluster0.e85xuag.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

db = client['mydatabase']
collection = db['users']


name, user_encoding, ID = databaseEntry()

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
