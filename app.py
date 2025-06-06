from flask import Flask, render_template, request, jsonify, Response
import json
import re
import threading
import os
from datetime import datetime
import pytz  # For Indian Standard Time (IST)

app = Flask(__name__)

# Lock to prevent simultaneous file writes
lock = threading.Lock()

# Load College Data
def load_college_data():
    with open("data/college_data.json", "r") as file:
        return json.load(file)

data = load_college_data()

# Extract keywords from user input
def extract_keywords(user_input):
    user_input = user_input.lower()
    words = re.findall(r'\b\w+\b', user_input)
    return " ".join(words)

# Function to store unknown queries in a single line with IST time
def store_unknown_query(query):
    unknown_file = "data/unknown_queries.json"

    # Ensure file exists
    if not os.path.exists(unknown_file):
        with open(unknown_file, "w") as file:
            json.dump([], file)

    with lock:  # Prevent multiple users from writing at the same time
        with open(unknown_file, "r+") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
            
            # Convert time to Indian Standard Time (IST)
            ist = pytz.timezone("Asia/Kolkata")
            now = datetime.now(ist)
            
            entry = f"{query} | {now.strftime('%Y-%m-%d %H:%M:%S')}"  # Single-line format
            
            if entry not in data:  # Avoid duplicate entries
                data.append(entry)
                file.seek(0)
                json.dump(data, file, indent=4)

# Function to get response with priority matching
def get_response(user_query):
    user_query = user_query.lower()

    for key in sorted(data.keys(), reverse=True):
        if key == "responses":
            continue

        if any(keyword in user_query for keyword in data[key]):
            return data["responses"][key]

    # If no match, store unknown query
    store_unknown_query(user_query)
    return "Sorry, I don't understand. Can you rephrase your question?"

# Route for UI
@app.route("/")
def home():
    return render_template("index.html")

# API Route for chatbot response
@app.route("/get_response", methods=["GET"])
def chatbot_response():
    user_input = request.args.get("query", "")
    if user_input:
        response = get_response(user_input)
        return jsonify({"response": response})
    return jsonify({"response": "Please ask a question."})

# Endpoint to view unknown queries
@app.route("/view-file")
def view_file():
    unknown_file = "data/unknown_queries.json"
    try:
        with open(unknown_file, "r") as file:
            content = file.read()
        return Response(content, mimetype="application/json")
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
