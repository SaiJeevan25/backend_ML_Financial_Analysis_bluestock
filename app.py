from flask import Flask, request, jsonify
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from config import API_KEY, BASE_URL
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

# ----------------- DATABASE SETUP -----------------
engine = create_engine("mysql+mysqlconnector://root:Saijeevan%405689@localhost:3306/bluestockcomp")

# ----------------- FETCH DATA -----------------
def fetch_company_data(company_id):
    url = f"{BASE_URL}?id={company_id}&api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for company ID {company_id}: {response.status_code}")
        return None

# ----------------- ANALYZE DATA -----------------
def analyze_financials(data):
    pros_list = []
    cons_list = []

    pros_cons_data = data.get("data", {}).get("prosandcons", [])

    if pros_cons_data:
        pros_raw = pros_cons_data[0].get("pros", "")
        cons_raw = pros_cons_data[0].get("cons", "")

        pros_list = [line.strip() for line in pros_raw.split('\n') if line.strip()]
        cons_list = [line.strip() for line in cons_raw.split('\n') if line.strip()]

    return pros_list[:3], cons_list[:3]

# ----------------- STORE RESULTS -----------------
def store_results(company_id, pros, cons):
    df = pd.DataFrame([{
        "company_id": company_id,
        "pros": ",".join(pros),
        "cons": ",".join(cons)
    }])

    with engine.begin() as conn:
        # Delete old record safely (does nothing if not present)
        conn.execute(text("DELETE FROM ml WHERE company_id = :cid"), {"cid": company_id})
        
        # Insert new record
        df.to_sql('ml', con=conn, if_exists='append', index=False)

    print(f"Stored/Updated Analysis for company ID {company_id} in the database.")


# ----------------- API ENDPOINT -----------------
@app.route("/get_company_data", methods=["POST"])
def get_company_data():
    data = request.get_json()
    company_id = data.get("id")

    if not company_id:
        return jsonify({"error": "No company ID provided"}), 400

    raw_data = fetch_company_data(company_id)
    if not raw_data:
        return jsonify({"error": f"Could not fetch data for company ID {company_id}"}), 404

    pros, cons = analyze_financials(raw_data)
    print(f"Pros: {pros},\n Cons: {cons}")
    store_results(company_id, pros, cons)

    return jsonify(raw_data)

# ----------------- RUN SERVER -----------------
if __name__ == "__main__":
    app.run(debug=True)
