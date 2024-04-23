from flask import Flask, request, jsonify
import requests
import json
app = Flask(__name__)

from appwrite.client import Client
from appwrite.input_file import InputFile
from appwrite.services.storage import Storage
from appwrite.id import ID

import os
import dotenv
dotenv.load_dotenv()

def uploadToAppwrite(data, use, filename, project_id=None):

    client = Client()

    (client
    .set_endpoint(os.getenv("APPWRITE_ENDPOINT")) # Your API Endpoint
    .set_project(os.getenv("APPWRITE_PROJECT_ID")) # Your project ID
    .set_key(os.getenv("APPWRTIE_API_KEY")) # Your secret API key
    )

    if use == 'profile-pictures':
        storage = Storage(client)

        try:
            # delete the file if it exists
            storage.delete_file(os.getenv("APPWRITE_BUCKET_ID"), filename)
        except:
            pass

        data = data.read()
        id = filename
        storage.create_file(os.getenv("APPWRITE_BUCKET_ID"), id , InputFile.from_bytes(data, filename=filename))
        bucket = os.getenv("APPWRITE_BUCKET_ID")
        appwrite_project_id = os.getenv("APPWRITE_PROJECT_ID")
        file_url = f"https://cloud.appwrite.io/v1/storage/buckets/{bucket}/files/{id}/view?project={appwrite_project_id}"

        return file_url

    elif use == 'project-documents':
        storage = Storage(client)
        try:
            # delete the file if it exists
            storage.delete_file(os.getenv("APPWRITE_BUCKET_ID"), filename)
        except:
            pass

        data = data.read()
        id = filename
        storage.create_file(os.getenv("APPWRITE_BUCKET_ID"), id , InputFile.from_bytes(data, filename=filename))
        bucket = os.getenv("APPWRITE_BUCKET_ID")
        appwrite_project_id = os.getenv("APPWRITE_PROJECT_ID")
        file_url = f"https://cloud.appwrite.io/v1/storage/buckets/{bucket}/files/{id}/view?project={appwrite_project_id}"

        return file_url


@app.route('/upload', methods=['POST'])
def upload_file():
    project_id = request.form['project_id']
    document = request.files['document']
    filename = document.filename
    data = {    
        "project_id": project_id
    }
    project = requests.get(f'http://localhost:5000/helper-1-for-upload-document', data=data)

    if project.status_code == 404:
        return jsonify({'message': 'Project not found', 'status': 'failed'}), 404
    
    
    filename = f"{project_id}_pdf"

    public_url = uploadToAppwrite(document, 'project-documents', filename, project_id)
    print(public_url)
    data = {
        'project_id': project_id,
        'document_url': public_url
    }
    requests.post('http://localhost:5000/helper-2-for-upload-document', data=data)

    return jsonify({'message': 'Document added','url':public_url, 'status': 'success'}), 200


if __name__ == '__main__':
    app.run(port=8001, debug=True)
