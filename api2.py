from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import io
from openai import OpenAI
from flask import Flask, request, jsonify, render_template
# ... (rest of your imports and config)



app = Flask(__name__)

# ---- Configuration ----
PAT_NAME = "test"
PAT_SECRET = "MMPfXGM1SiiimTQoRV7HTA==:cSqLgPrazgDIvtrl5wlPB9GKdZTTMFTH"
SITE_CONTENT_URL = "multinetpakistanpvtltd"
TABLEAU_SERVER = "https://prod-apnortheast-a.online.tableau.com"
VIEW_ID = "6bcc2ce9-60e5-4c42-9ff1-e38b14e82f74"
OPENAI_API_KEY = "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"  # Replace with your valid key

# ---- Helper: Sign in to Tableau ----
def get_tableau_data():
    signin_url = f"{TABLEAU_SERVER}/api/3.18/auth/signin"
    signin_payload = {
        "credentials": {
            "personalAccessTokenName": PAT_NAME,
            "personalAccessTokenSecret": PAT_SECRET,
            "site": {"contentUrl": SITE_CONTENT_URL}
        }
    }

    headers = {"Content-Type": "application/json"}
    resp = requests.post(signin_url, json=signin_payload, headers=headers)

    if resp.status_code != 200:
        return None, f"Sign-in failed: {resp.text}"

    root = ET.fromstring(resp.text)
    ns = {'t': 'http://tableau.com/api'}
    credentials = root.find('t:credentials', ns)
    token = credentials.attrib['token']
    site_id = credentials.find('t:site', ns).attrib['id']
    auth_headers = {"X-Tableau-Auth": token}

    data_url = f"{TABLEAU_SERVER}/api/3.18/sites/{site_id}/views/{VIEW_ID}/data"
    data_resp = requests.get(data_url, headers=auth_headers)

    if data_resp.status_code != 200:
        return None, f"Failed to get view data: {data_resp.text}"

    df = pd.read_csv(io.StringIO(data_resp.text))
    return df.to_csv(index=False), None
@app.route("/")
def index():
    return render_template("chat.html")

# ---- OpenAI Client ----
client = OpenAI(api_key=OPENAI_API_KEY)

# ---- API Route ----
@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Missing 'question' in request."}), 400

    data_str, error = get_tableau_data()
    if error:
        return jsonify({"error": error}), 500

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the provided CSV data to answer questions."},
        {"role": "user", "content": f"Here is the data:\n{data_str}"},
        {"role": "user", "content": question}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        assistant_reply = response.choices[0].message.content
        return jsonify({"response": assistant_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---- Run Flask App ----
if __name__ == "__main__":
    app.run(debug=True)
