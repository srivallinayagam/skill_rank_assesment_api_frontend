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
    users = list(db.users.find({}, {'_id': 0, 'id': 1, 'name': 1}))
    return jsonify(users)

# Endpoint 2: Get User by ID
@app.route('/api/users/<int:user_id>')
def get_user_by_id(user_id):
    user = db.users.find_one({"id": user_id}, {'_id': 0})
    return jsonify(user or {})

# Endpoint 3: Get Subjects of a User
@app.route('/api/users/<int:user_id>/subjects')
def get_user_subjects(user_id):
    subjects = list(db.subjects.find({"userId": user_id}, {'_id': 0}))
    return jsonify(subjects)

# Endpoint 4: Update Subjects of a User (overwrite existing subjects)
@app.route('/api/users/<int:user_id>/subjects', methods=['PUT'])
def update_user_subjects(user_id):
    try:
        new_subjects = request.json
        db.subjects.delete_many({"userId": user_id})  # Remove old
        for subj in new_subjects:
            subj["userId"] = user_id  # Assign userId
        if new_subjects:
            db.subjects.insert_many(new_subjects)  # Insert new
        return jsonify({"status": "updated", "count": len(new_subjects)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# --- Run the App ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5055))
    app.run(debug=True, port=port)
