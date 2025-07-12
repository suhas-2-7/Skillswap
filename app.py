from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from pymongo import MongoClient
from bson.objectid import ObjectId
from gridfs import GridFS
import bcrypt
import datetime
import os
from dotenv import load_dotenv
import io

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret_key")  # required for session

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["skill_swap_db"]
users_collection = db["users"]
swap_collection = db["swap_requests"]
projects_collection = db["projects"]
fs = GridFS(db)

# Registration Route
@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form.get('location')
        skills_offered = request.form.get('skills_offered', '')
        skills_wanted = request.form.get('skills_wanted', '')
        availability = request.form.getlist('availability')
        public_profile = request.form.get('public_profile') == 'yes'
        profile_picture = request.form.get('profile_picture') or ""
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']

        if users_collection.find_one({"email": email}):
            return render_template('form.html', error="Email already registered!")

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        users_collection.insert_one({
            "name": name,
            "location": location,
            "skills_offered": skills_offered,
            "skills_wanted": skills_wanted,
            "availability": availability,
            "public_profile": public_profile,
            "profile_picture": profile_picture,
            "contact": contact,
            "email": email,
            "password": hashed_pw,
            "ratings": []
        })

        return redirect('/login')
    return render_template('form.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = str(user['_id'])
            session['user_skill'] = user.get('skills_offered', '')
            return redirect('/landing')
        else:
            error_message = "Login failed. Check your credentials."
    return render_template('login.html', error_message=error_message)

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Landing Page with Search
@app.route('/landing', methods=['GET'])
def landing():
    query = request.args.get('query', '').strip().lower()
    filters = request.args.getlist('filter')
    users = []

    if query:
        users = list(users_collection.find({"public_profile": True}))
        filtered = [
            u for u in users
            if query in u.get('name', '').lower() or
               query in u.get('skills_offered', '').lower() or
               query in u.get('skills_wanted', '').lower()
        ]
        for f in filters:
            filtered = [u for u in filtered if f in u.get('skills_offered', '').lower()]
    else:
        filtered = list(users_collection.find({"public_profile": True}))

    return render_template('landing.html', users=filtered)

# Send Swap Request
@app.route('/send_swap', methods=['POST'])
def send_swap():
    if 'user_id' not in session:
        return redirect('/login')

    data = request.form
    swap = {
        "sender_id": session['user_id'],
        "receiver_id": data['receiver_id'],
        "sender_skill": session.get('user_skill', ''),
        "receiver_skill": data['receiver_skill'],
        "status": "Pending",
        "timestamp": datetime.datetime.utcnow()
    }
    swap_collection.insert_one(swap)
    return redirect('/landing')

# View All Swap Requests (Sent + Received)
@app.route('/my_swaps')
def my_swaps():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    received_swaps = list(swap_collection.find({"receiver_id": user_id}))
    sent_swaps = list(swap_collection.find({"sender_id": user_id}))

    # Attach sender/receiver names
    for swap in received_swaps:
        sender = users_collection.find_one({"_id": ObjectId(swap["sender_id"])})
        swap["sender_name"] = sender.get("name") if sender else "Unknown"
        swap["sender_contact"] = sender.get("contact") if sender else "N/A"

    for swap in sent_swaps:
        receiver = users_collection.find_one({"_id": ObjectId(swap["receiver_id"])})
        swap["receiver_name"] = receiver.get("name") if receiver else "Unknown"
        swap["receiver_contact"] = receiver.get("contact") if receiver else "N/A"

    return render_template('my_swaps.html', received=received_swaps, sent=sent_swaps)

# Accept / Reject / Delete Swap
@app.route('/swap_action/<swap_id>/<action>', methods=['POST'])
def swap_action(swap_id, action):
    if action == 'accept':
        swap_collection.update_one({"_id": ObjectId(swap_id)}, {"$set": {"status": "Accepted"}})
    elif action == 'reject':
        swap_collection.update_one({"_id": ObjectId(swap_id)}, {"$set": {"status": "Rejected"}})
    elif action == 'delete':
        swap_collection.delete_one({"_id": ObjectId(swap_id)})
    return redirect('/my_swaps')

# Submit Feedback
@app.route('/submit_feedback/<swap_id>', methods=['POST'])
def submit_feedback(swap_id):
    rating = int(request.form['rating'])
    comment = request.form['comment']
    swap_collection.update_one({"_id": ObjectId(swap_id)}, {"$set": {"feedback": {"rating": rating, "comment": comment}}})
    return redirect('/my_swaps')

# Repository Upload
@app.route("/collaboration", methods=["POST"])
def create_repository():
    try:
        repo_name = request.form.get("name")
        description = request.form.get("description")
        uploaded_files = request.files.getlist("files")
        file_ids = [fs.put(f, filename=f.filename) for f in uploaded_files if f.filename]
        projects_collection.insert_one({
            "repo_name": repo_name,
            "description": description,
            "file_ids": file_ids,
            "created_at": datetime.datetime.utcnow()
        })
        return jsonify({"message": "Repository created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_repositories", methods=["GET"])
def get_repositories():
    try:
        projects = projects_collection.find({})
        repo_list = []
        for project in projects:
            file_details = [
                {"file_id": str(fid), "filename": fs.get(fid).filename}
                for fid in project.get("file_ids", [])
            ]
            repo_list.append({
                "name": project.get("repo_name"),
                "description": project.get("description"),
                "file_types": [f["filename"].split(".")[-1] for f in file_details],
                "files": file_details
            })
        return jsonify(repo_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    try:
        file_obj = fs.get(ObjectId(file_id))
        return send_file(
            io.BytesIO(file_obj.read()),
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name=file_obj.filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Additional Pages
@app.route('/collaborate')
def collaborate():
    return render_template('collaborate.html')

@app.route('/skill_swap')
def skill_swap():
    return render_template('skill_swap.html')

@app.route('/users')
def users_page():
    users = list(users_collection.find({}, {"name": 1, "skills_offered": 1, "skills_wanted": 1, "contact": 1, "profile_picture": 1, "email": 1}))
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
