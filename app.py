from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
  cred = credentials.Certificate("serviceAccountKey.json")
  firebase_admin.initialize_app(cred)

db = firestore.client()
app = Flask(__name__)


@app.route("/report", methods=["POST"])
def report_server():
  data = request.json
  job_id = data.get("jobId")

  if not job_id:
    return jsonify({"error": "Missing jobId"}), 400

  db.collection("servers").document(job_id).set({
      "jobId": job_id,
      "eggType": data.get("eggType", "Unknown"),
      "rarityScore": data.get("rarityScore", 0),
      "playerCount": data.get("playerCount", 0),
      "timestamp": firestore.SERVER_TIMESTAMP,
  })

  return jsonify({"status": "success", "message": "Server reported!"}), 200


@app.route("/servers", methods=["GET"])
def get_servers():
  servers_ref = db.collection("servers")
  query = servers_ref.order_by(
      "rarityScore", direction=firestore.Query.DESCENDING
  ).limit(20)
  results = query.stream()

  server_list = []
  for doc in results:
    server_list.append(doc.to_dict())

  return jsonify(server_list), 200


import os

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
