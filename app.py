import streamlit as st
import pandas as pd
import numpy as np
import asyncio
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="Global Price Vision", layout="wide")

st.title("📸 AI Product Price Scout")
st.write("Upload a photo or enter text to find the best prices globally.")

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("Global Filters")
    currency = st.selectbox("Preferred Currency", ["USD", "EUR", "GBP", "JPY", "INR"])
    max_shipping = st.slider("Max Shipping Days", 1, 30, 7)

# --- STEP 1: INPUT ---
col_in1, col_in2 = st.columns([1, 2])

with col_in1:
    uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Product to Search", use_container_width=True)

with col_in2:
    product_name = st.text_input("Product Name/Details", placeholder="e.g. Sony WH-1000XM5 Black")
    search_btn = st.button("🔍 Find World-Wide Prices", use_container_width=True)

# --- STEP 2: GLOBAL SEARCH LOGIC ---
if search_btn and product_name:
    with st.spinner("Scanning Global Markets..."):
        # Mock Data with Coordinates for the Map
        # In 2026, you'd fetch this via a Global Price API
        world_data = [
            {"Store": "Amazon US", "Price": 348.00, "lat": 37.09, "lon": -95.71, "Link": "https://amazon.com", "Country": "USA"},
            {"Store": "Alibaba CN", "Price": 290.00, "lat": 35.86, "lon": 104.19, "Link": "https://alibaba.com", "Country": "China"},
            {"Store": "MediaMarkt DE", "Price": 315.00, "lat": 51.16, "lon": 10.45, "Link": "https://mediamarkt.de", "Country": "Germany"},
            {"Store": "Flipkart IN", "Price": 340.00, "lat": 20.59, "lon": 78.96, "Link": "https://flipkart.com", "Country": "India"},
            {"Store": "Currys UK", "Price": 310.00, "lat": 55.37, "lon": -3.43, "Link": "https://currys.co.uk", "Country": "UK"},
        ]
        
        df = pd.DataFrame(world_data)
        df = df.sort_values("Price") # Low to High

        # Display Metrics
        m1, m2 = st.columns(2)
        m1.metric("Lowest Global Price", f"${df.iloc[0]['Price']}")
        m2.metric("Market Average", f"${round(df['Price'].mean(), 2)}")

        # --- STEP 3: WORLD MAP VISUAL ---
        st.subheader("🌍 World Market Distribution")
        # st.map requires columns 'lat' and 'lon'
        st.map(df, size=20, color='#00ff00')

        # --- STEP 4: PURCHASE LINKS ---
        st.subheader("🛒 Purchase Links (Sorted: Low to High)")
        
        # Display as a clean data editor/table
        st.dataframe(
            df[['Store', 'Country', 'Price', 'Link']],
            column_config={
                "Link": st.column_config.LinkColumn("Official Site"),
                "Price": st.column_config.NumberColumn(format="$%.2f")
            },
            hide_index=True,
            use_container_width=True
        )

elif search_btn and not product_name:
    st.error("Please enter a product name or upload an image with a description.")
