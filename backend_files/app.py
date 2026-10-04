import joblib
import pandas as pd
from flask import Flask, jsonify, request

# The Flask app is created
superkart_api = Flask("SuperKart Sales Predictor")

# The trained pipeline (preprocessing + model) is loaded once when the app starts
model = joblib.load("superkart_model.joblib")

NUMERIC_FEATURES = ["Product_Weight", "Product_Allocated_Area", "Product_MRP", "Store_Age_Years"]
CATEGORICAL_FEATURES = ["Product_Sugar_Content", "Store_Size", "Store_Location_City_Type",
                        "Store_Type", "Product_Id_char", "Product_Type_Category"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def prepare_input(df):
    """Checks the input columns and converts them to the right data types."""
    missing = [col for col in FEATURES if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    df = df[FEATURES].copy()
    try:
        df[NUMERIC_FEATURES] = df[NUMERIC_FEATURES].astype(float)
    except (ValueError, TypeError):
        raise ValueError(f"These fields must be numbers: {NUMERIC_FEATURES}")
    if df[FEATURES].isnull().any().any():
        raise ValueError("Input contains empty values")
    df[CATEGORICAL_FEATURES] = df[CATEGORICAL_FEATURES].astype(str)
    return df


@superkart_api.get("/")
def home():
    """Health check endpoint."""
    return jsonify({"message": "Welcome to the SuperKart Sales Prediction API", "status": "ok"})


@superkart_api.post("/v1/predict")
def predict_sales():
    """Predicts sales for one product-store record sent as JSON."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400
    try:
        features = prepare_input(pd.DataFrame([payload]))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    prediction = float(model.predict(features)[0])
    return jsonify({"Predicted_Sales": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Predicts sales for many records sent as a CSV file."""
    uploaded_file = request.files.get("file")
    if uploaded_file is None:
        return jsonify({"error": "Please upload a CSV file in the 'file' field"}), 400
    try:
        batch = pd.read_csv(uploaded_file)
    except Exception:
        return jsonify({"error": "The uploaded file could not be read as CSV"}), 400
    if batch.empty:
        return jsonify({"error": "The uploaded CSV file has no rows"}), 400
    try:
        features = prepare_input(batch)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    predictions = model.predict(features)
    return jsonify({str(idx): round(float(pred), 2) for idx, pred in zip(batch.index, predictions)})


@superkart_api.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint not found"}), 404


@superkart_api.errorhandler(500)
def server_error(_):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
