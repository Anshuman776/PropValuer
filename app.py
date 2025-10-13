from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# Load scaler
scaler = None
for name in ("scalar.pkl", "scaler.pkl"):
    if os.path.exists(name):
        try:
            scaler = pickle.load(open(name, "rb"))
            break
        except:
            scaler = None

# Load model
model = None
for candidate in ("newmodel.pkl", "model.pkl"):
    if os.path.exists(candidate):
        try:
            model = pickle.load(open(candidate, "rb"))
            break
        except:
            model = None

# Location premiums
location_premium = {
    "Dwarka": 1.10,
    "Rohini": 1.05,
    "Saket": 1.20,
    "Vasant Kunj": 1.30,
    "Janakpuri": 1.15,
    "Karol Bagh": 1.25
}

def to_bool_int(val):
    if val is None: return 0
    if isinstance(val, (int, float)): return int(val)
    return 1 if str(val).strip().lower() in ("1","true","yes","on") else 0

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return "Model not found on server.", 500

    # Gather form inputs
    try:
        area = float(request.form.get("Area", 0))
    except ValueError:
        area = 0.0
    try:
        bedrooms = float(request.form.get("Bedrooms", 0))
    except ValueError:
        bedrooms = 0.0

    car_parking = to_bool_int(request.form.get("CarParking"))
    gym = to_bool_int(request.form.get("Gymnasium"))
    pool = to_bool_int(request.form.get("SwimmingPool"))

    location = request.form.get("Location", "")
    sector = request.form.get("Sector", "")
    full_location = f"{location} {sector}".strip()
    location_value = np.log(location_premium.get(location, 1.0))

    # Build feature vector
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is None and hasattr(model, "best_estimator_"):
        feature_names = getattr(model.best_estimator_, "feature_names_in_", None)
    if feature_names is None:
        n_feat = getattr(model, "n_features_in_", None)
        if n_feat is None:
            return "Model lacks feature info", 500
        feature_names = [f"f_{i}" for i in range(n_feat)]

    X = pd.Series(0, index=feature_names, dtype=float)
    for col, val in {
        "Area": area,
        "Bedrooms": bedrooms,
        "CarParking": car_parking,
        "Gymnasium": gym,
        "SwimmingPool": pool,
        "LogPremium": location_value
    }.items():
        if col in X.index:
            X[col] = val

    # One-hot location
    loc_col = f"Location_{location}"
    if loc_col in X.index:
        X[loc_col] = 1

    X_df = pd.DataFrame([X.values], columns=X.index)

    # Scale if available
    X_scaled = scaler.transform(X_df) if scaler else X_df.values

    try:
        prediction = model.predict(X_scaled)[0]
    except Exception as e:
        return f"Prediction error: {e}", 500

    prediction_text = f"🏠 Estimated Price in {full_location}: ₹{int(prediction):,}"
    return render_template("index.html", prediction_text=prediction_text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
