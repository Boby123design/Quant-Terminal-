# Decision Engine Liquidity

A Windows-based Streamlit research prototype that analyzes trading-chart snapshots with a multi-modal PyTorch model to estimate **TP / SL / CTC** probabilities and log actual trade outcomes for post-trade analysis.
strategy for which this model gives verdict is Liquidity strategy.

---

## Demo

![Model_7 terminal](screenshots/02-terminal-home.png)
*Main terminal interface for chart capture and setup selection.*

![AI verdict](screenshots/04-ai-verdict.png)
*Real-time probability breakdown (TP, SL, CTC) and rule-based trade verdict.*

---

## Key Features

* **Multi-Modal Deep Learning:** Combines a **ResNet-18 CNN** image branch (224 × 224 chart snapshots) with a tabular branch (setup quality and trade direction) via a fusion classifier.
* **Three-Class Probability Estimation:** Predicts likelihoods for **Take Profit (TP)**, **Stop Loss (SL)**, and **Cost-to-Cost (CTC)**.
* **Automated Action Verdicts:** Generates rule-based `SKIP`, `CAUTION`, or `ENTRY` signals from estimated probabilities.
* **Flexible Chart Input:** Supports automatic Windows screen capture, clipboard image paste, or manual file upload.
* **Live Outcome Logging:** Records actual post-trade results directly into `live_cleaned_dataset.csv` for dataset expansion and evaluation.

---

## Tech Stack

* **Language & Environment:** Python (Windows)
* **Frontend UI:** Streamlit
* **Machine Learning:** PyTorch, Torchvision, Scikit-learn
* **Data & Image Processing:** Pandas, Pillow, OpenPyXL
* **System Integration:** PyWin32 (Windows screen/window APIs)

---

## Installation & Quick Start

1. **Clone the repository and navigate to the project folder:**
   ```powershell
   git clone <your-repository-url>
   cd Model_7
   ```

2. **Create a virtual environment and install dependencies:**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install streamlit torch torchvision pandas pillow pywin32 openpyxl scikit-learn
   ```

3. **Launch the application:**
   ```powershell
   python -m streamlit run app_model7.py --server.port 8507
   ```
   *(Alternatively, double-click `run_model7.bat` to start the terminal directly on Windows.)*

---

## Usage

* **Inputs:** 
  * Trading chart image (auto-captured, pasted, or uploaded)
  * Setup Quality (`Blind`, `Good`, `Best`)
  * Trade Direction (`Buy`, `Sell`)
* **Outputs:** 
  * Estimated probabilities for `TP`, `SL`, and `CTC`
  * Action verdict (`SKIP` / `CAUTION` / `ENTRY`)

**Example Workflow:**
1. Run `run_model7.bat` to open the Streamlit interface.
2. Capture a chart automatically, paste it from the clipboard, or upload an image file.
3. Select the setup quality and trade direction.
4. Click **Analyze Probability** to view the `TP`, `SL`, and `CTC` estimates along with the app's verdict.
5. After the trade finishes, select its actual outcome in the UI and save the record to `live_cleaned_dataset.csv`.

---

## Project Structure

| File | Purpose |
| :--- | :--- |
| `app_model7.py` | Main Streamlit application, inference pipeline, verdict logic, and outcome logger |
| `model_architecture.py` | Multi-modal PyTorch architecture (ResNet-18 + tabular fusion) |
| `train_model.py` | Model training script |
| `dataset_loader.py` | Custom image and tabular dataset loader |
| `forex_model.pth` | Trained PyTorch model weights used for inference |
| `live_cleaned_dataset.csv` | Dataset containing user-logged live trade outcomes |
| `working.md` | Detailed technical workflow and system documentation |
| `result.md` | Dataset breakdown and experimental performance metrics |

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

> **Disclaimer:** This software is an experimental research tool for decision support, not financial advice or a guarantee of profitable trading. Always validate models out-of-sample and account for live execution costs.
