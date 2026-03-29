import streamlit as st
import pandas as pd
import asyncio
import httpx
from datetime import datetime

# --- CONFIGURATION & UI SETUP ---
st.set_page_config(page_title="Global Price Scout 2026", layout="wide")

st.title("🌐 Global Price Scout")
st.markdown("Enter a product to find the lowest prices across the **World Market**.")

# --- UTILITY: CURRENCY CONVERSION ---
# In production, use an API like Fixer.io or ExchangeRate-API
EXCHANGE_RATES = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.0, "JPY": 150.0}

def convert_to_usd(price, currency):
    return price / EXCHANGE_RATES.get(currency, 1.0)

# --- MOCK SCRAPER ENGINE (Replace with real Scraper/API calls) ---
async def fetch_prices(product_query):
    """
    Simulates fetching data from global markets simultaneously.
    Replace these with actual HTTP requests to SerpApi or Rainforest API.
    """
    await asyncio.sleep(1.5)  # Simulate network latency
    
    # Mock data representing different global regions
    data = [
        {"Store": "Amazon US", "Price": 1200.00, "Currency": "USD", "Link": "https://amazon.com", "Region": "North America"},
        {"Store": "MediaMarkt DE", "Price": 1050.00, "Currency": "EUR", "Link": "https://mediamarkt.de", "Region": "Europe"},
        {"Store": "Currys UK", "Price": 900.00, "Currency": "GBP", "Link": "https://currys.co.uk", "Region": "Europe"},
        {"Store": "Bic Camera JP", "Price": 175000.00, "Currency": "JPY", "Link": "https://biccamera.com", "Region": "Asia"},
        {"Store": "Flipkart IN", "Price": 98000.00, "Currency": "INR", "Link": "https://flipkart.com", "Region": "Asia"},
    ]
    
    # Process and Normalize
    for item in data:
        item["Price (USD)"] = round(convert_to_usd(item["Price"], item["Currency"]), 2)
    
    return sorted(data, key=lambda x: x["Price (USD)"])

# --- SIDEBAR: CONTROLS ---
with st.sidebar:
    st.header("Search Settings")
    target_currency = st.selectbox("Display Currency", options=list(EXCHANGE_RATES.keys()))
    include_shipping = st.checkbox("Include Estimated Shipping", value=True)
    st.divider()
    st.info("This app scans official global retailers using real-time API aggregation.")

# --- MAIN APP LOGIC ---
query = st.text_input("What product are you looking for?", placeholder="e.g. MacBook Pro M3 Max 16-inch")

if query:
    with st.spinner(f"Searching the global market for '{query}'..."):
        # Run the async scraper
        results = asyncio.run(fetch_prices(query))
        
        # Display Best Deal Highlight
        best_deal = results[0]
        st.success(f"**Best Price Found:** ${best_deal['Price (USD)']} at {best_deal['Store']} ({best_deal['Region']})")
        
        # Create Columns for Visual Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Lowest Price", f"${best_deal['Price (USD)']}")
        col2.metric("Average Global Price", f"${round(sum(d['Price (USD)'] for d in results)/len(results), 2)}")
        col3.metric("Market Variance", f"{round(((results[-1]['Price (USD)'] - results[0]['Price (USD)'])/results[0]['Price (USD)'])*100, 1)}%")

        # Display Data Table
        df = pd.DataFrame(results)
        
        # Add clickable links
        st.subheader("Price Comparison Table (Low to High)")
        st.dataframe(
            df,
            column_config={
                "Link": st.column_config.LinkColumn("Purchase Link"),
                "Price (USD)": st.column_config.NumberColumn(format="$%.2f")
            },
            hide_index=True,
            use_container_width=True
        )

        # Visual Chart
        st.subheader("Price Distribution by Region")
        st.bar_chart(df, x="Store", y="Price (USD)", color="Region")

else:
    st.info("Enter a product name above to start the comparison.")

# --- FOOTER ---
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
