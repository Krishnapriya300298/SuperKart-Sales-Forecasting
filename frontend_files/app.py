import os

import pandas as pd
import requests
import streamlit as st

# Address of the Flask backend (inside the Docker network it is reached by its container name)
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860").rstrip("/")
CURRENT_YEAR = 2025
PERISHABLES = ["Dairy", "Meat", "Fruits and Vegetables", "Breakfast", "Breads", "Seafood"]
PRODUCT_TYPES = ["Baking Goods", "Breads", "Breakfast", "Canned", "Dairy", "Frozen Foods",
                 "Fruits and Vegetables", "Hard Drinks", "Health and Hygiene", "Household",
                 "Meat", "Others", "Seafood", "Snack Foods", "Soft Drinks", "Starchy Foods"]
REQUIRED_COLUMNS = ["Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area",
                    "Product_MRP", "Store_Size", "Store_Location_City_Type", "Store_Type",
                    "Product_Id_char", "Store_Age_Years", "Product_Type_Category"]

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒", layout="wide")
st.title("🛒 SuperKart Sales Forecast")
st.write("Predict the total sales of a product in a SuperKart store.")

single_tab, batch_tab = st.tabs(["Single Prediction", "Batch Prediction"])

with single_tab:
    with st.form("single_prediction"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Product details")
            product_code = st.selectbox("Product code (first two letters of Product Id)", ["FD", "DR", "NC"],
                                        help="FD = Food, DR = Drinks, NC = Non-consumable")
            product_type = st.selectbox("Product type", PRODUCT_TYPES)
            sugar = st.selectbox("Sugar content", ["Low Sugar", "Regular", "No Sugar"])
            weight = st.number_input("Product weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
            area = st.number_input("Allocated display area (ratio)", min_value=0.0, max_value=1.0,
                                   value=0.027, step=0.001, format="%.3f")
            mrp = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=117.08, step=0.01)
        with col2:
            st.subheader("Store details")
            store_type = st.selectbox("Store type", ["Supermarket Type1", "Supermarket Type2",
                                                     "Departmental Store", "Food Mart"])
            store_size = st.selectbox("Store size", ["Small", "Medium", "High"])
            city_type = st.selectbox("City type", ["Tier 1", "Tier 2", "Tier 3"])
            est_year = st.number_input("Store establishment year", min_value=1950,
                                       max_value=CURRENT_YEAR, value=2009, step=1)
        submitted = st.form_submit_button("Predict Sales")

    if submitted:
        payload = {
            "Product_Weight": weight,
            "Product_Sugar_Content": sugar,
            "Product_Allocated_Area": area,
            "Product_MRP": mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_code,
            "Store_Age_Years": int(CURRENT_YEAR - est_year),
            "Product_Type_Category": "Perishables" if product_type in PERISHABLES else "Non Perishables",
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                sales = response.json()["Predicted_Sales"]
                st.success("Prediction received from the API")
                st.metric("Predicted Product Store Sales Total", f"{sales:,.2f}")
                with st.expander("Data sent to the API"):
                    st.json(payload)
            else:
                st.error(f"API error ({response.status_code}): {response.json().get('error', response.text)}")
        except requests.exceptions.RequestException as err:
            st.error(f"Could not connect to the backend at {BACKEND_URL}: {err}")

with batch_tab:
    st.write("Upload a CSV file with these columns:")
    st.code(", ".join(REQUIRED_COLUMNS))
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded is not None:
        batch_df = pd.read_csv(uploaded)
        st.write(f"Preview of the uploaded file ({len(batch_df)} rows):")
        st.dataframe(batch_df.head(10), use_container_width=True)

        missing = [c for c in REQUIRED_COLUMNS if c not in batch_df.columns]
        if missing:
            st.error(f"These columns are missing in the file: {missing}")
        elif st.button("Predict Batch"):
            try:
                files = {"file": ("batch.csv", batch_df.to_csv(index=False).encode("utf-8"), "text/csv")}
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files, timeout=120)
                if response.status_code == 200:
                    preds = response.json()
                    result = batch_df.copy()
                    result["Predicted_Sales"] = [preds[str(i)] for i in batch_df.index]
                    st.success(f"Predictions received for {len(result)} rows")
                    c1, c2 = st.columns(2)
                    c1.metric("Total predicted sales", f"{result['Predicted_Sales'].sum():,.2f}")
                    c2.metric("Average predicted sales", f"{result['Predicted_Sales'].mean():,.2f}")
                    st.dataframe(result, use_container_width=True)
                    st.download_button("Download predictions as CSV", result.to_csv(index=False),
                                       file_name="superkart_predictions.csv", mime="text/csv")
                else:
                    st.error(f"API error ({response.status_code}): {response.json().get('error', response.text)}")
            except requests.exceptions.RequestException as err:
                st.error(f"Could not connect to the backend at {BACKEND_URL}: {err}")
