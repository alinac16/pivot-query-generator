# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# IMPORTANT: Adjust origins to your frontend URL in production
# For local development, allow all origins
CORS(app, origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8000", "http://localhost:8000"]) # Add your frontend's actual URL here when deployed

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables. Please set it in a .env file.")
    # Exit or handle more gracefully in production

@app.route('/generate-query', methods=['POST'])
def generate_query_proxy():
    if not GEMINI_API_KEY:
        return jsonify({"error": "API Key not configured on server."}), 500

    try:
        # Get the payload (chat history) from the frontend request
        frontend_payload = request.get_json()
        if not frontend_payload or 'contents' not in frontend_payload:
            return jsonify({"error": "Invalid request payload."}), 400

        # Prepare the payload for the Gemini API
        # The prompt is expected to be in frontend_payload['contents']
        gemini_payload = {
            "contents": frontend_payload['contents']
        }

        # Make the request to the Gemini API
        headers = {
            'Content-Type': 'application/json'
        }
        params = {
            'key': GEMINI_API_KEY
        }

        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=gemini_payload)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Return the Gemini API's response directly to the frontend
        return jsonify(response.json()), 200

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": f"Failed to connect to AI service: {e}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500

if __name__ == '__main__':
    # You might want to use a production-ready WSGI server like Gunicorn for deployment
    app.run(debug=True, port=5000) # debug=True is for development only
