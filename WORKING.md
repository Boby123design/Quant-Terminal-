# Model 18 — Working Guide

## Overview

Model 18 is designed to run as an automated BTCUSD trading terminal connected to MetaTrader 5 (MT5). Once the environment and required setup are correct, the user starts the terminal from the Windows batch launcher and monitors activity through the dashboard and MT5.

> **Important:** Automated trading can lose money. First verify the system on an MT5 demo account. A dashboard display alone does not prove that every order, stop-loss, take-profit, or emergency-stop action is working correctly.

## How to Start the Terminal

1. Open the project folder.
2. Double-click `launch_terminal.bat` (Windows may hide the `.bat` extension, so it may appear as `launch_terminal`).
3. Allow the launcher to start the required processes.
4. Open the local dashboard in the browser if it does not open automatically. The dashboard shown in the project screenshots is hosted at `http://localhost:8501`.
5. Keep the required terminal/process windows running while the system is in use.
6. Open MetaTrader 5 and select the correct account and BTCUSD symbol. Confirm Algo Trading/automated trading permissions and any broker-specific settings required by the implementation.
7. Monitor the dashboard and MT5 together.


## Screenshot Reference

The following screenshots are included in the `screenshots/` folder. Keep that folder beside this Markdown file so the images render correctly on GitHub.

### 1. Start the terminal

In the project folder, double-click `launch_terminal.bat`. Windows may hide the `.bat` extension, so the file may appear as `launch_terminal`.

![Project folder showing the launcher file](screenshots/01-project-folder-launcher.png)

### 2. Monitor the dashboard

The dashboard shown below is opened at `http://localhost:8501`. It displays the available live price, spread, AI confidence, execution status, PnL, and emergency-stop control. Values shown in a screenshot are illustrative of that captured moment.

![Model 18 dashboard](screenshots/02-model-18-dashboard.png)

### 3. Verify activity in MT5

The MT5 screenshot shows a chart and an open BTCUSD trade in the Trade tab. Always verify the current position and its SL/TP directly in MT5 rather than relying only on dashboard text. The screenshot does not prove that every trade will open or that every protective order will always be accepted.

![MetaTrader 5 showing chart and trade information](screenshots/03-mt5-live-trade.png)

## Intended Automated Workflow

When all prerequisites and trading conditions are satisfied, the intended workflow is:

1. **Launch:** The user starts the application by double-clicking `launch_terminal.bat`.
2. **Backend starts:** The launcher starts the configured Python execution process and dashboard process.
3. **Market data:** The data-feeder component obtains live BTCUSD tick data from MT5, subject to its configuration and MT5 connection.
4. **Model inference:** The execution engine loads the trained model and evaluates the incoming market data.
5. **Entry decision:** If the model output and the strategy's configured entry conditions qualify, the execution engine may submit an order to MT5.
6. **Risk controls:** Stop-loss and take-profit levels are intended to be attached to the order or managed by the execution logic, depending on how the code is implemented.
7. **MT5 visibility:** Submitted orders and open positions can be inspected in the MT5 Trade tab and on the chart.
8. **Dashboard monitoring:** The dashboard displays the live price, model confidence, active execution information, and PnL/status fields that its code reads from the backend/status files.
9. **User role:** The user primarily monitors the system after launch, but should remain ready to intervene if the connection, order handling, risk controls, or displayed status is abnormal.

The above describes the intended operation. Actual behavior depends on the code, correct configuration, model/data compatibility, MT5 connectivity, broker permissions, and the market conditions. Do not assume that a trade will always be opened or that protective orders are always accepted without checking MT5.

## What the Main Files Do

| File or folder | Intended role |
|---|---|
| `launch_terminal.bat` | Windows launcher for the configured backend and dashboard processes. |
| `auto_executor.py` | Live execution logic: connects to MT5, obtains live inputs, runs model inference, and can submit orders if its conditions pass. |
| `hft_dashboard.py` | Streamlit monitoring interface for price, model confidence, execution status, PnL, and the emergency-stop control. |
| `live_dom_feeder.py` | Collects live market/tick data from MT5 and writes data for the pipeline, as configured. |
| `Abondend_Model_18/` | Contains the project's model/data-processing and training scripts. |
| `train.pth` | Saved PyTorch model weights used by the inference code, if the configured path matches. |
| `training_dataset.csv` | Dataset used by the processing/training workflow. |
| `live_status.csv` | Runtime status data consumed by the dashboard, depending on the implementation. |
| `bot_running.lock` | Runtime lock file used to help indicate or prevent duplicate processes, if implemented by the scripts. |
| `.gitignore` | Tells Git which matching untracked files to ignore; it does not make files private or remove files already committed. |

## How the Components Connect

The intended high-level flow is:

```text
User double-clicks launch_terminal.bat
                 |
                 v
      +-----------------------+
      | Launcher starts       |
      | configured processes  |
      +-----------------------+
            |           |
            v           v
    auto_executor.py  hft_dashboard.py
            |           |
            |           +---- reads live_status.csv (if configured)
            |
            +---- connects to MetaTrader 5
            |          |
            |          +---- live BTCUSD ticks / account / orders
            |
            +---- loads train.pth
            |
            +---- evaluates model and strategy conditions
            |
            +---- submits eligible orders with configured SL/TP logic
                       |
                       v
                 MT5 Trade tab/chart

live_dom_feeder.py ---> live tick/data CSVs ---> processing/training scripts
                                             ---> training_dataset.csv
                                             ---> train.pth
```

The exact live data route depends on the code: the executor may read ticks directly from MT5, while the feeder and training scripts form a separate data/training pipeline. Confirm the actual filenames and paths in the scripts before assuming the feeder is required for every live trade.

## Dashboard Indicators

The dashboard screenshot shows these main areas:

- **Live Price (BTCUSD):** The price value read by the dashboard.
- **Spread:** The spread value available to the dashboard.
- **AI Confidence (Traps):** The BUY/SELL confidence values calculated or reported by the backend.
- **Active Execution:** The currently reported trade side/status.
- **Live PnL:** The profit/loss value read by the dashboard.
- **Emergency Kill Switch:** A control intended to signal a stop to the trading process.

Treat these as monitoring indicators, not independent proof of broker-side state. Cross-check positions, order volume, entry price, SL, TP, and PnL in MT5.

## Startup Checklist

Before starting:

- [ ] Python environment and required packages are installed.
- [ ] MetaTrader 5 is installed, logged in, and connected to the intended account.
- [ ] The broker's BTCUSD symbol name matches the one configured in the code.
- [ ] Automated trading is enabled where required.
- [ ] The expected `train.pth` model file exists at the path used by `auto_executor.py`.
- [ ] The model's input features and normalization match the training pipeline.
- [ ] CSV paths and working directories are consistent.
- [ ] No stale process or lock file is preventing startup.
- [ ] Risk limits, order volume, SL, TP, and duplicate-order protections have been reviewed.
- [ ] The system has been tested on a demo account.

## Emergency Stop and Open Positions

Use the dashboard's Emergency Kill Switch only after verifying what it does in the current implementation. A stop signal may stop new entries without automatically closing an already-open position. After activating it:

1. Confirm that the execution process has stopped submitting new orders.
2. Inspect open positions and pending orders in MT5.
3. Manage or close positions manually if needed and if that is your intended risk response.
4. Verify that the bot cannot restart or resume trading unexpectedly.

Do not rely on the button as a guaranteed close-all mechanism unless the code explicitly implements, and you have tested, that behavior.

## Troubleshooting

### Dashboard does not open
- Check whether the launcher started Streamlit successfully.
- Check the terminal output for errors.
- Try opening `http://localhost:8501` locally if the configured port is 8501.

### Dashboard opens but values do not update
- Check that the backend is running.
- Confirm that `live_status.csv` is being refreshed and that the dashboard reads the same path.
- Confirm MT5 is connected and the configured symbol is available.

### No trade is opened
- This may be normal if entry conditions are not met.
- Check the model file path, inference errors, confidence thresholds, market-data freshness, symbol name, trading permissions, volume rules, and broker rejection messages in MT5/logs.

### Model fails to load or predictions look wrong
- Confirm that the model architecture matches the saved weights.
- Confirm training and live inference use the same feature order and preprocessing/normalization.
- Check the file path to `train.pth`.

### Stop-loss or take-profit is missing
- Check MT5 order/position details and the broker's rejection message.
- Verify the code actually submits SL/TP with the order or modifies the position afterward.
- Do not assume the dashboard can apply protection unless that behavior is implemented and confirmed.

## Safety and Repository Notes

- Do not store broker passwords, API keys, account credentials, or personal account data in source code or GitHub.
- Use `.gitignore` for local datasets, runtime CSVs, logs, lock files, virtual environments, and secrets as appropriate.
- `.gitignore` does not protect files that have already been committed; remove them from Git tracking and rotate any exposed credentials.
- Avoid publishing private or licensed market datasets without checking permissions.
- Use a demo account until order execution, SL/TP, duplicate-order prevention, and emergency-stop behavior have been validated.

## Scope

This guide describes the intended workflow and the visible project layout. If the implementation changes, update this document to match the actual launcher commands, file paths, model input features, risk controls, and order-management behavior.
