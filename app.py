from flask import Flask, render_template, request, abort
import pickle
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# Try loading scaler (try common filenames), then model
scaler = None
for name in ("scalar.pkl", "scaler.pkl"):
    if os.path.exists(name):
        try:
            scaler = pickle.load(open(name, "rb"))
            scaler_path = name
            break
        except Exception:
            scaler = None
            scaler_path = None

model = None
model_path = None
for candidate in ("newmodel.pkl", "model.pkl"):
    if os.path.exists(candidate):
        try:
            model = pickle.load(open(candidate, "rb"))
            model_path = candidate
            break
        except Exception:
            model = None
            model_path = None

# Minimal location premiums (extend as needed)
location_premium = {
    "Dwarka": 1.10,
    "Rohini": 1.05,
    "Saket": 1.20,
    "Vasant Kunj": 1.30,
    "Janakpuri": 1.15,
    "Karol Bagh": 1.25
}


def to_bool_int(val):
    """Convert form checkbox/string to 0/1 integer."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).strip().lower()
    if s in ("1", "true", "yes", "on"): 
        return 1
    return 0


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return "Model not found on server. Place 'newmodel.pkl' or 'model.pkl' in the app folder.", 500

    # Gather basic inputs with safe defaults
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
    security = to_bool_int(request.form.get("24X7Security"))
    power = to_bool_int(request.form.get("PowerBackup"))

    location = request.form.get("Location", "")
    sector = request.form.get("Sector", "")
    full_location = f"{location} {sector}".strip()
    location_value = np.log(location_premium.get(location, 1.0))

    # Use a local copy of scaler so assignments won't shadow the module-level variable
    local_scaler = scaler

    # Build a feature vector that matches the scaler/model training features
    feature_names = None
    # determine model feature names
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is None and hasattr(model, "best_estimator_"):
        feature_names = getattr(model.best_estimator_, "feature_names_in_", None)

    if feature_names is None:
        # fall back to n_features_in_ -> create generic names
        n_feat = getattr(model, "n_features_in_", None)
        if n_feat is None:
            return (
                "Model does not expose feature names or n_features_in_. Re-create model with pandas DataFrame so feature names are stored.",
                500,
            )
        # create integer column names if no names available
        feature_names = [f"f_{i}" for i in range(n_feat)]

    # If a scaler was found, ensure it's compatible with this model. If not, ignore scaler.
    if local_scaler is not None:
        scaler_feat = getattr(local_scaler, "feature_names_in_", None)
        scaler_n = getattr(local_scaler, "n_features_in_", None)
        model_n = getattr(model, "n_features_in_", None)
        compatible = False
        if scaler_feat is not None and list(scaler_feat) == list(feature_names):
            compatible = True
        elif scaler_n is not None and model_n is not None and scaler_n == model_n:
            compatible = True
        if not compatible:
            # ignore incompatible scaler
            local_scaler = None

    # Build a Series with default 0 values
    X = pd.Series(0, index=feature_names, dtype=float)

    # Set known numeric features if present in the training columns
    for col, val in {
        "Area": area,
        "Bedrooms": bedrooms,
        "CarParking": car_parking,
        "Gymnasium": gym,
        "SwimmingPool": pool,
        "24X7Security": security,
        "PowerBackup": power,
        "LogPremium": location_value,
        "FeatureScore": float(request.form.get("FeatureScore", 0)),
        "Resale": to_bool_int(request.form.get("Resale", 0)),
    }.items():
        if col in X.index:
            X[col] = val

    # If the model used one-hot location columns (e.g. Location_<name>), try to set that column
    loc_col = None
    if location:
        # exact match
        if location in X.index:
            loc_col = location
        else:
            # try common patterns
            loc_pattern = f"Location_{location}"
            if loc_pattern in X.index:
                loc_col = loc_pattern
    if loc_col:
        X[loc_col] = 1

    # Convert to DataFrame with single row, preserve column order
    X_df = pd.DataFrame([X.values], columns=X.index)

    # Scale if scaler is available and compatible
    if local_scaler is not None:
        try:
            X_scaled = local_scaler.transform(X_df)
        except Exception as e:
            return f"Error while scaling features: {e}", 500
    else:
        X_scaled = X_df.values

    # Predict
    try:
        prediction = model.predict(X_scaled)[0]
    except Exception as e:
        return f"Prediction error: {e}", 500

    return render_template(
        "index.html",
        prediction_text=f"🏠 Estimated Price in {full_location}: ₹{round(float(prediction), 2)}",
    )


# if __name__ == "__main__":
#     # Run without the auto-reloader to avoid interpreter shutdown issues
#     app.run(debug=False, use_reloader=False)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
