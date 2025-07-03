from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
from flask_cors import CORS
import os

# --- Flask App Configuration ---
app = Flask(__name__, template_folder='.', static_folder='static')
CORS(app)

# --- MongoDB Connection ---
MONGO_URI = "mongodb+srv://ss1:TQDnimkIDHRf14iH@cluster0.hgmufho.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["ss1"]

# --- Routes ---
# Home Route - serves index.html
@app.route('/')
def index():
    return render_template("index.html")

# Endpoint 1: Get All Users
@app.route('/api/users')
def get_all_users():
    try:
        users = list(db.users.find({}, {'_id': 0, 'id': 1, 'name': 1}))
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 2: Get User by ID
@app.route('/api/users/<int:user_id>')
def get_user_by_id(user_id):
    try:
        user = db.users.find_one({"id": user_id}, {'_id': 0})
        return jsonify(user or {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 3: Get Subjects of a User
@app.route('/api/users/<int:user_id>/subjects')
def get_user_subjects(user_id):
    try:
        subjects = list(db.subjects.find({"userId": user_id}, {'_id': 0}))
        return jsonify(subjects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 4: Append new subjects (without removing existing ones)
@app.route('/api/users/<int:user_id>/subjects', methods=['PUT'])
def update_user_subjects(user_id):
    try:
        new_subjects = request.json

        # Validate input
        if not isinstance(new_subjects, list):
            return jsonify({"status": "error", "message": "Expected a list of subjects"}), 400

        for subj in new_subjects:
            if not isinstance(subj, dict) or 'subject' not in subj:
                return jsonify({"status": "error", "message": "Each subject must have a 'subject' field"}), 400
            subj["userId"] = user_id

        # Avoid inserting duplicate subjects
        existing_subjects = set(
            s['subject'] for s in db.subjects.find({"userId": user_id}, {'subject': 1, '_id': 0})
        )
        unique_subjects = [s for s in new_subjects if s['subject'] not in existing_subjects]

        if unique_subjects:
            db.subjects.insert_many(unique_subjects)

        return jsonify({
            "status": "appended",
            "inserted": len(unique_subjects),
            "skipped_duplicates": len(new_subjects) - len(unique_subjects)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Optional: Get all subjects (for debugging)
@app.route('/api/subjects')
def get_all_subjects():
    try:
        subjects = list(db.subjects.find({}, {'_id': 0}))
        return jsonify(subjects)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run the App ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5055))
    app.run(debug=True, port=port)
