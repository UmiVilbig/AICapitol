import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the model
with open('model v3.pkl', 'rb') as file:
    model = pickle.load(file)


# Define feature categories
categorical_features = ["member", "Ticker", "Type", "State", "Country", "Sector"]
numerical_features = ['BuyPrice', 'Bought', 'Filed', 'Delta', 'Amount', 'FilePrice',
                      'NM', 'OM', 'ROA', 'RGR', 'EGR', 'CLR', 'DER',
                      "Assets", "Liabilities", "Equity", "Net Cashflow", "Earnings Per Share", "Operating Income"]

all_features = categorical_features + numerical_features

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not all(feature in data for feature in all_features):
            return jsonify({"error": "Missing required features in request"}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame([data], columns=all_features)
        
        # Make prediction
        prediction = model.predict(df)
        
        # Get confidence scores if model supports predict_proba
        if hasattr(model, "predict_proba"):
            confidence = model.predict_proba(df).max(axis=1).tolist()
        else:
            confidence = None
        
        return jsonify({"prediction": prediction.tolist(), "confidence": confidence})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(port=5000)