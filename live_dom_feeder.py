import MetaTrader5 as mt5
import pandas as pd
import time
import os
from datetime import datetime

# ⚠️ Locked Symbol
SYMBOL = "BTCUSD"
DATA_FILE = "hft_crypto_dataset.csv"

def connect_mt5():
    """MT5 se connection establish karta hai"""
    print("⏳ MT5 se connect ho raha hai...")
    if not mt5.initialize():
        print(f"❌ MT5 Initialization Failed.")
        return False
    
    mt5.symbol_select(SYMBOL, True)
    print(f"✅ MT5 Connected. '{SYMBOL}' is Active!\n")
    return True

def collect_hft_data():
    """Live Ticks aur Velocity calculate karke CSV mein save karta hai"""
    print(f"🚀 Launching HFT Data Logger for {SYMBOL}...")
    print(f"📁 Data will be saved to: {DATA_FILE}\n")
    
    # Agar file nahi hai, toh headers ke sath naye file banayein
    if not os.path.exists(DATA_FILE):
        df_empty = pd.DataFrame(columns=["Time", "Bid", "Ask", "Spread", "Velocity_ms"])
        df_empty.to_csv(DATA_FILE, index=False)

    buffer = []
    last_time_ms = 0
    last_tick_ms_for_velocity = 0
    total_saved = 0

    try:
        while True:
            tick = mt5.symbol_info_tick(SYMBOL)
            if tick is None: continue

            if tick.time_msc != last_time_ms:
                # 1. Calculate Tick Velocity (Speed of Market)
                if last_tick_ms_for_velocity == 0:
                    velocity = 0
                else:
                    velocity = tick.time_msc - last_tick_ms_for_velocity

                last_tick_ms_for_velocity = tick.time_msc
                last_time_ms = tick.time_msc

                # 2. Extract Data
                dt = datetime.fromtimestamp(tick.time)
                time_str = f"{dt.strftime('%H:%M:%S')}.{str(tick.time_msc)[-3:]}"
                spread = round((tick.ask - tick.bid), 2)

                # 3. Add to Buffer
                buffer.append({
                    "Time": time_str,
                    "Bid": tick.bid,
                    "Ask": tick.ask,
                    "Spread": spread,
                    "Velocity_ms": velocity
                })

                # Terminal par live status dikhana (Overwriting single line)
                print(f"📡 Live: {time_str} | Bid: {tick.bid} | Vel: {velocity}ms | Buffer: {len(buffer)}/100", end="\r")

                # 4. Save to CSV in batches of 100 (To save RAM and avoid disk overload)
                if len(buffer) >= 100:
                    df = pd.DataFrame(buffer)
                    df.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    total_saved += 100
                    print(f"\n💾 [SAVED] Total {total_saved} ticks written to CSV...")
                    buffer = [] # Agle 100 ticks ke liye buffer khali

            time.sleep(0.01) # 10ms rest for CPU

    except KeyboardInterrupt:
        # Stop karne par bacha hua data save karna
        if len(buffer) > 0:
            pd.DataFrame(buffer).to_csv(DATA_FILE, mode='a', header=False, index=False)
        print(f"\n🛑 System Stopped. Total data points saved: {total_saved + len(buffer)}")
        mt5.shutdown()

if __name__ == "__main__":
    if connect_mt5():
        collect_hft_data()