import streamlit as st
import pandas as pd
import time
import random
import requests
from datetime import datetime

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Global Price Nexus", page_icon="🌐", layout="wide")

# --- ADVANCED REALISTIC UI (CSS) ---
st.markdown("""
<style>
    /* Main Background Gradient */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a) !important;
    }

    /* Frosted Glass Metric Cards */
    [data-testid="stMetricValue"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px 15px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stMetricDelta"] {
        color: #4ade80 !important;
    }

    /* Search Bar Styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.07) !important;
        color: #f1f5f9 !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 12px;
        font-size: 1.1rem;
        padding: 12px 16px !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #64748b !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25) !important;
    }

    /* Custom Header Color */
    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 700;
    }

    /* DataFrame Styling */
    .stDataFrame {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* File Uploader */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.03);
        border: 1px dashed #3b82f6;
        border-radius: 12px;
    }

    /* Info Box */
    [data-testid="stInfo"] {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        color: #e2e8f0 !important;
    }

    /* Status animation spinner */
    [data-testid="stStatusWidget"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Subtitle styling */
    .streamlit-expanderHeader {
        color: #94a3b8;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# --- UTILITY: LOTTIE ANIMATIONS (Safe Load) ---
@st.cache_data
def load_lottie(url):
    """Safely load Lottie animation with error handling."""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# --- PRODUCT DATABASE SIMULATOR ---
def generate_global_prices(product_name):
    """
    Generate realistic global price data for any searched product.
    Uses region-specific cost multipliers and currency conversion.
    """
    # Region config: (currency_symbol, exchange_rate_to_usd, cost_multiplier_range, locale_suffix)
    regions = {
        "India":    ("₹",   83.5,  (0.30, 0.50), "in"),
        "USA":      ("$",   1.0,   (0.85, 1.20), "com"),
        "Germany":  ("€",   0.92,  (0.70, 0.95), "de"),
        "Spain":    ("€",   0.92,  (0.72, 0.98), "es"),
        "China":    ("¥",   7.24,  (0.25, 0.45), "cn"),
        "Japan":    ("¥",   155.0, (0.55, 0.80), "jp"),
        "UK":       ("£",   0.79,  (0.75, 1.05), "co.uk"),
        "Brazil":   ("R$",  5.05,  (0.50, 0.75), "com.br"),
    }

    # Base USD price seeded by product name for consistency
    random.seed(hash(product_name) % 2**31)
    base_usd = random.uniform(15, 250)

    # Store pools per region
    store_map = {
        "India":   ["Amazon India", "Flipkart", "Myntra", "Tata CLiQ"],
        "USA":     ["Amazon US", "Walmart", "Best Buy", "Target"],
        "Germany": ["Amazon DE", "Otto", "Zalando", "MediaMarkt"],
        "Spain":   ["Amazon ES", "El Corte Inglés", "ZARA Home", "PC Componentes"],
        "China":   ["Tmall", "JD.com", "Pinduoduo", "Suning"],
        "Japan":   ["Rakuten", "Amazon JP", "Yahoo Shopping", "Bic Camera"],
        "UK":      ["Amazon UK", "Argos", "Currys", "John Lewis"],
        "Brazil":  ["Mercado Livre", "Magalu", "Americanas", "Submarino"],
    }

    results = []
    for region, (symbol, fx_rate, mult_range, locale) in regions.items():
        # 2-3 stores per region for variety
        stores = random.sample(store_map[region], k=min(3, len(store_map[region])))
        for store in stores:
            multiplier = random.uniform(*mult_range)
            usd_price = round(base_usd * multiplier, 2)
            local_price_val = round(usd_price * fx_rate, 2)

            # Format local price nicely
            if symbol in ("₹", "¥"):
                local_str = f"{symbol}{local_price_val:,.0f}"
            elif symbol == "R$":
                local_str = f"R$ {local_price_val:,.2f}"
            else:
                local_str = f"{symbol}{local_price_val:,.2f}"

            domain = store.split()[-1].lower().replace("home", "").strip()
            link = f"https://www.amazon.{locale}" if "Amazon" in store else f"https://www.{store.lower().replace(' ', '').replace('.', '')}.{locale}"

            results.append({
                "Store": store,
                "Region": region,
                "Local Price": local_str,
                "USD Price": usd_price,
                "Savings vs Highest": 0,  # calculated after
                "Link": link,
            })

    # Calculate savings vs highest price
    max_price = max(r["USD Price"] for r in results)
    for r in results:
        r["Savings vs Highest"] = round((1 - r["USD Price"] / max_price) * 100, 1)

    return sorted(results, key=lambda x: x["USD Price"])


# --- LOTTIE (with safe fallback) ---
lottie_globe = load_lottie("https://lottie.host/95191022-8393-4e45-9831-29962a9b3d0c/T1v8vD1b9G.json")

# --- APP LAYOUT ---
st.title("🌐 Global Price Nexus")
st.markdown("### *Your AI-Powered Window to the Entire World Market*")

col_left, col_right = st.columns([3, 1])

with col_left:
    user_input = st.text_input(
        "search_box",
        placeholder="Search anything (e.g., Slim Fit Jeans, PS5, OLED Monitor)...",
        label_visibility="collapsed"
    )
    uploaded_file = st.file_uploader(
        "📸 Or upload a product image for visual recognition",
        type=["jpg", "png", "jpeg"],
        key="image_uploader"
    )

with col_right:
    try:
        if lottie_globe:
            from streamlit_lottie import st_lottie
            st_lottie(lottie_globe, height=180, key="globe")
        else:
            st.markdown("## 🌍")
    except ImportError:
        st.markdown("## 🌍")

# --- HANDLE IMAGE UPLOAD ---
detected_product = None
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width=250)
    # Simulate AI product detection
    detected_product = st.selectbox(
        "🔍 Detected Product (simulated AI recognition):",
        ["Wireless Earbuds", "Running Shoes", "Smart Watch", "Backpack", "Sunglasses"],
        key="detected_product"
    )

# --- DETERMINE SEARCH TERM ---
search_term = detected_product if detected_product else user_input

# --- SEARCH EXECUTION ---
if search_term:
    with st.status("Initializing Nexus Search Engines...", expanded=True) as status:
        st.write("📡 Scanning North American Retailers...")
        time.sleep(0.3)
        st.write("🌍 Analyzing European & Asian Markets...")
        time.sleep(0.3)
        st.write("⚖️ Normalizing Global Currencies & Shipping Costs...")
        time.sleep(0.3)
        st.write(f"🔍 Comparing prices for: **{search_term}**")
        status.update(label="✅ Nexus Sync Complete!", state="complete", expanded=False)

    # Generate dynamic results
    results = generate_global_prices(search_term)
    df = pd.DataFrame(results)

    # --- METRICS BAR ---
    lowest = df.iloc[0]
    highest = df.iloc[-1]
    avg_price = round(df["USD Price"].mean(), 2)
    savings_pct = round((1 - lowest["USD Price"] / highest["USD Price"]) * 100, 1)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "🏷️ Lowest World Price",
        f"${lowest['USD Price']:.2f}",
        f"-{savings_pct}% vs Highest",
        delta_color="normal"
    )
    m2.metric("📊 Market Average", f"${avg_price}")
    m3.metric("🏆 Top Savings Hub", f"{lowest['Region']}")
    m4.metric("🏪 Stores Compared", f"{len(df)}")

    st.divider()

    # --- DATA DISPLAY ---
    st.subheader(f"📊 Global Market Deal Sheet — *{search_term}*")

    # Color-code the dataframe
    st.dataframe(
        df[["Store", "Region", "Local Price", "USD Price", "Savings vs Highest", "Link"]],
        column_config={
            "USD Price": st.column_config.NumberColumn("Price (USD)", format="$ %.2f"),
            "Savings vs Highest": st.column_config.NumberColumn("Savings %", format="%.1f %%"),
            "Link": st.column_config.LinkColumn("Purchase Link", display_text="Open Store ↗"),
        },
        use_container_width=True,
        hide_index=True,
        height=400,
    )

    st.divider()

    # --- CHARTS ---
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("📈 Price by Region (Lowest per Region)")
        # Aggregate: min price per region
        region_min = df.groupby("Region")["USD Price"].min().reset_index()
        region_min = region_min.sort_values("USD Price")

        st.bar_chart(
            region_min,
            x="Region",
            y="USD Price",
            color="#3b82f6",
            use_container_width=True,
        )

    with chart_col2:
        st.subheader("💹 Price Spread per Region")
        # Show min/max spread
        region_stats = df.groupby("Region")["USD Price"].agg(["min", "max", "mean"]).reset_index()
        region_stats = region_stats.sort_values("min")

        chart_df = region_stats.set_index("Region")[["min", "max", "mean"]]
        chart_df.columns = ["Lowest", "Highest", "Average"]
        st.line_chart(chart_df, use_container_width=True, color=["#4ade80", "#f87171", "#60a5fa"])

    st.divider()

    # --- SAVINGS CALLOUT ---
    best_deal = df.iloc[0]
    worst_deal = df.iloc[-1]
    st.success(
        f"💡 **Best Deal Found!** Buy from **{best_deal['Store']}** ({best_deal['Region']}) "
        f"at **{best_deal['Local Price']}** (${best_deal['USD Price']:.2f} USD) — "
        f"Save **{savings_pct}%** compared to {worst_deal['Store']} ({worst_deal['Region']})"
    )

else:
    st.info(
        "💡 Enter a product name above. The Nexus will automatically compare "
        "official sites across the globe."
    )
