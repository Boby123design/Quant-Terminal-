import MetaTrader5 as mt5
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import time
from datetime import datetime
from collections import deque
import os
import sys

# ⚠️ Configuration
SYMBOL = "BTCUSD"
MODEL_PATH = "train.pth"
STATUS_FILE = "live_status.csv"
LOCK_FILE = "bot_running.lock" 
LOT_SIZE = 0.01
MAGIC_NUMBER = 181818

# 🚨 THE MACRO QUANT SHIFT (The real fix to stop instant exits)
# BTC ko saans lene ke liye badi jagah de rahe hain. Noise mein SL hit nahi hoga.
SL_DISTANCE_USD = 150.0  
TP_DISTANCE_USD = 300.0  

# 🧠 PyTorch Architecture
class Quant_HFT_Net(nn.Module):
    def __init__(self):
        super(Quant_HFT_Net, self).__init__()
        self.fc1 = nn.Linear(5, 64) 
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 3) 
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        return self.fc3(x)

def connect_mt5():
    if not mt5.initialize():
        return False
    mt5.symbol_select(SYMBOL, True)
    return True

def execute_trade(action_type):
    tick = mt5.symbol_info_tick(SYMBOL)
    
    if action_type == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
        sl = price - SL_DISTANCE_USD
        tp = price + TP_DISTANCE_USD
    else: 
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
        sl = price + SL_DISTANCE_USD
        tp = price - TP_DISTANCE_USD

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": MAGIC_NUMBER,
        "comment": "AI_Macro_Sniper",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"🚀 MACRO EXECUTION: {action_type} @ {price:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
        return True
    return False

def update_live_status(mid_price, spread, buy_conf, sell_conf, active_trade="NONE", pnl=0.0):
    dt_str = datetime.now().strftime('%H:%M:%S')
    df = pd.DataFrame([{
        "Time": dt_str,
        "Price": round(mid_price, 2),
        "Spread": round(spread, 2),
        "Buy_Conf": round(buy_conf, 2),
        "Sell_Conf": round(sell_conf, 2),
        "Trade_Active": active_trade,
        "PnL": round(pnl, 2)
    }])
    df.to_csv(STATUS_FILE, index=False)

def run_live_bot():
    if os.path.exists(LOCK_FILE):
        try: os.remove(LOCK_FILE)
        except: sys.exit()
            
    with open(LOCK_FILE, "w") as f: f.write("LOCKED")

    model = Quant_HFT_Net()
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()
    
    print(f"🚀 AI Macro-Quant Engine Running...")
    print(f"🛡️ WIDE BANDS ACTIVE: SL ${SL_DISTANCE_USD} / TP ${TP_DISTANCE_USD}")
    
    vel_buffer, spread_buffer, dir_buffer = deque(maxlen=50), deque(maxlen=50), deque(maxlen=50)
    last_time_ms = 0
    last_mid_price = 0
    memory_trade_locked = False 
    
    try:
        while True:
            if os.path.exists("kill_switch.txt"): break

            tick = mt5.symbol_info_tick(SYMBOL)
            if tick is None or tick.time_msc == last_time_ms:
                time.sleep(0.01)
                continue
                
            velocity = tick.time_msc - last_time_ms if last_time_ms != 0 else 0
            spread = tick.ask - tick.bid
            mid_price = (tick.bid + tick.ask) / 2
            price_change = mid_price - last_mid_price if last_mid_price != 0 else 0
            
            vel_buffer.append(velocity)
            spread_buffer.append(spread)
            dir_buffer.append(np.sign(price_change))
            
            last_time_ms = tick.time_msc
            last_mid_price = mid_price

            buy_conf, sell_conf = 0.0, 0.0
            
            positions = mt5.positions_get(symbol=SYMBOL)
            our_positions = [p for p in positions if p.magic == MAGIC_NUMBER] if positions else []
            live_pnl = 0.0
            
            if positions is None:
                active_trade = "API_LAG"
                memory_trade_locked = True
            elif len(our_positions) > 0:
                active_trade = "BUY" if our_positions[0].type == mt5.ORDER_TYPE_BUY else "SELL"
                live_pnl = sum([p.profit for p in our_positions])
                memory_trade_locked = True 
            else:
                active_trade = "NONE"
                memory_trade_locked = False

            if len(vel_buffer) == 50:
                vel_std, spread_std = np.std(vel_buffer) + 1e-9, np.std(spread_buffer) + 1e-9
                vel_z = (velocity - np.mean(vel_buffer)) / vel_std
                spread_z = (spread - np.mean(spread_buffer)) / spread_std
                tick_imbalance = sum(dir_buffer) 
                
                live_features = np.array([[price_change, vel_z, spread_z, spread, tick_imbalance]], dtype=np.float32)
                X_tensor = torch.from_numpy(live_features)
                
                with torch.no_grad():
                    probs = torch.softmax(model(X_tensor), dim=1).numpy()[0]
                    buy_conf, sell_conf = probs[1] * 100, probs[2] * 100
                    
                    if active_trade == "NONE" and memory_trade_locked == False:
                        if buy_conf > 85.0:
                            memory_trade_locked = True 
                            if execute_trade("BUY"): time.sleep(10)
                            else: memory_trade_locked = False 
                                
                        elif sell_conf > 85.0:
                            memory_trade_locked = True 
                            if execute_trade("SELL"): time.sleep(10)
                            else: memory_trade_locked = False 

            update_live_status(mid_price, spread, buy_conf, sell_conf, active_trade, live_pnl)
            time.sleep(0.01)

    except KeyboardInterrupt: pass
    finally:
        if os.path.exists(LOCK_FILE): os.remove(LOCK_FILE)
        mt5.shutdown()

if __name__ == "__main__":
    if connect_mt5(): run_live_bot()