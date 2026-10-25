import streamlit as st
import pandas as pd
import time
import os

# Page Config
st.set_page_config(page_title="Model 18 Command Center", layout="wide")

# Custom CSS for Dark Hacker/Quant Theme
st.markdown("""
    <style>
    body {background-color: #0E1117; color: white;}
    .metric-card {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid #334155;
    }
    .conf-buy { color: #10B981; font-size: 24px; font-weight: bold;}
    .conf-sell { color: #EF4444; font-size: 24px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

st.title("🛡️Quant Terminal")
st.caption("Live High-Frequency Trading Bot (BTCUSD)")

# 🚨 Kill Switch Button
col_kill, _ = st.columns([1, 3])
with col_kill:
    if st.button("🔴 EMERGENCY KILL SWITCH", type="primary", use_container_width=True):
        # Create a file that tells the backend to stop
        with open("kill_switch.txt", "w") as f:
            f.write("STOP")
        st.error("KILL SIGNAL SENT TO BACKEND ENGINE!")

st.markdown("---")

# Layout for Data
col1, col2, col3 = st.columns(3)

# Data Loader
try:
    if os.path.exists("live_status.csv"):
        df = pd.read_csv("live_status.csv")
        data = df.iloc[-1]
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <p>Live Price (BTCUSD)</p>
                <h2>${data['Price']}</h2>
                <p>Spread: {data['Spread']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <p>AI Confidence (Traps)</p>
                <p class='conf-buy'>BUY: {data['Buy_Conf']}%</p>
                <p class='conf-sell'>SELL: {data['Sell_Conf']}%</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            pnl_color = "#10B981" if data['PnL'] >= 0 else "#EF4444"
            st.markdown(f"""
            <div class='metric-card'>
                <p>Active Execution</p>
                <h3>{data['Trade_Active']}</h3>
                <p style='color: {pnl_color}; font-weight: bold;'>Live PnL: ${data['PnL']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.caption(f"Last Ping: {data['Time']}")
    else:
        st.warning("⏳ Waiting for Backend Engine to start... No data found.")
        
except Exception as e:
    pass # Ignore read errors while file is updating

# Auto-Refresh Page every 1 second
time.sleep(1)
st.rerun()