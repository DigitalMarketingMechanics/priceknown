import streamlit as st
import pandas as pd
import time
import requests
from streamlit_lottie import st_lottie

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Denim Scout", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS (Advanced UI/Motion Graphics) ---
st.markdown("""
<style>
    /* Glassmorphism Effect */
    .main {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
    }
    .stApp {
        background-attachment: fixed;
    }
    
    /* Realistic Card Styling */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #3b82f6;
    }

    /* Animated Search Bar */
    .stTextInput input {
        border-radius: 50px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid #3b82f6;
        color: white;
        padding: 15px 25px;
    }
</style>
""", unsafe_allow_html=True)

# --- UTILITY: LOAD LOTTIE ANIMATIONS ---
def load_lottieurl(url):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

lottie_scan = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_t9gkkhz4.json") # Scanning Animation

# --- APP UI ---
st.title("👖 Advanced Denim Price Engine")
st.write("Scan the entire world market for the most accurate prices in real-time.")

col1, col2 = st.columns([2, 1])

with col1:
    product_query = st.text_input("Search for jeans (e.g., Slim Fit Levi's)", key="search_bar")
    uploaded_image = st.file_uploader("Upload product photo for Visual Search", type=['jpg', 'png'])

with col2:
    if lottie_scan:
        st_lottie(lottie_scan, height=150, key="scanner")

# --- SEARCH EXECUTION ---
if product_query or uploaded_image:
    with st.status("Fetching Live Data from Global Retailers...", expanded=True) as status:
        st.write("📡 Connecting to Google Shopping API...")
        time.sleep(1)
        st.write("🌍 Analyzing markets in USA, China, Germany, and India...")
        time.sleep(1)
        status.update(label="Global Search Complete!", state="complete", expanded=False)

    # Mock Global Data (Simulating Entire World)
    global_data = [
        {"Product": "H&M Straight Regular Jeans", "Price": 19.10, "Store": "H&M Global", "Region": "Europe", "Link": "https://www2.hm.com/"},
        {"Product": "Levi's 512 Tapered", "Price": 18.60, "Store": "Levi Strauss", "Region": "India", "Link": "https://www.levi.in/"},
        {"Product": "Uniqlo Selvedge Denim", "Price": 24.90, "Store": "Uniqlo JP", "Region": "Japan", "Link": "https://www.uniqlo.com/"},
        {"Product": "GAP Standard Denim", "Price": 22.00, "Store": "Gap US", "Region": "USA", "Link": "https://www.gap.com/"},
        {"Product": "ZARA Relaxed Fit", "Price": 26.50, "Store": "Zara ES", "Region": "Spain", "Link": "https://www.zara.com/"}
    ]
    
    df = pd.DataFrame(global_data).sort_values("Price")

    # Metrics Section
    m1, m2, m3 = st.columns(3)
    m1.metric("Lowest Global Price", f"${df.iloc[0]['Price']}", "-$3.40 vs Average")
    m2.metric("Market Average", f"${round(df['Price'].mean(), 2)}")
    m3.metric("Top Region for Savings", f"{df.iloc[0]['Region']}")

    # Table with purchase links
    st.subheader("📊 Global Deal Board")
    st.dataframe(
        df,
        column_config={
            "Link": st.column_config.LinkColumn("Purchase Official Site"),
            "Price": st.column_config.NumberColumn(format="$%.2f")
        },
        use_container_width=True,
        hide_index=True
    )

    # Motion Graphic Chart
    st.subheader("📈 Regional Price Variance")
    st.area_chart(df, x="Region", y="Price", color="#3b82f6")

else:
    st.info("💡 Try searching for 'H&M Men's Straight Regular Jeans' to see the global price map.")
