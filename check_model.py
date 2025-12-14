import pickle
import traceback
import sys
import os

MODEL_PATH = os.path.join("models", "model.pkl")

print("Checking model file:", MODEL_PATH)
print("Exists:", os.path.exists(MODEL_PATH))
if not os.path.exists(MODEL_PATH):
    sys.exit(1)

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("Loaded model type:", type(model))
    print("feature_names_in_:", getattr(model, "feature_names_in_", None))
    print("n_features_in_:", getattr(model, "n_features_in_", None))
    print("Has attribute 'predict':", hasattr(model, "predict"))
except Exception:
    traceback.print_exc()
    sys.exit(2)

print("OK")
