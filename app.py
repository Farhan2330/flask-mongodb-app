from flask import Flask, request, jsonify
from pymongo import MongoClient, errors
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

# Get environment variables
mongodb_uri = os.getenv("MONGODB_URI")
username = os.getenv("MONGODB_USERNAME")
password = os.getenv("MONGODB_PASSWORD") 
flask_run_host = os.getenv("FLASK_RUN_HOST")
flask_run_port = os.getenv("FLASK_RUN_PORT")

# Check if all required environment variables are set
required_env_vars = [mongodb_uri, username, password, flask_run_host, flask_run_port]
if None in required_env_vars:
    missing_vars = [var for var, value in zip(
        ["MONGODB_URI", "MONGODB_USERNAME", "MONGODB_PASSWORD", "FLASK_RUN_HOST", "FLASK_RUN_PORT"],
        required_env_vars
    ) if value is None]
    print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

try:
    client = MongoClient(mongodb_uri, username=username, password=password, authSource="admin")
    db = client.mydatabase
    collection = db.data
except errors.PyMongoError as e:
    print(f"MongoDB connection error: {e}")
    sys.exit(1)

@app.route('/')
def index():
    return f"Welcome to the Flask app! The current time is: {datetime.now()}"

@auth.verify_password
def verify_password(input_username, input_password):
    print(f"Verifying: {input_username}, {input_password}")
    return input_username == username and input_password == password

@app.route('/data', methods=['GET', 'POST'])
@auth.login_required
def data():
    if request.method == 'POST':
        data = request.get_json()
        try:
            collection.insert_one(data)
            return jsonify({"status": "Data inserted"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'GET':
        try:
            data = list(collection.find({}, {"_id": 0}))
            return jsonify(data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host=flask_run_host, port=int(flask_run_port))
