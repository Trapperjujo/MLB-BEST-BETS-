---
description: How to Deploy the PRO BALL PREDICTOR Terminal
---

# 🛰️ Workflow: Deploying to the AppDeploy Cloud

This guide explains how to move your local Streamlit code to a high-availability cloud URL using the provided institutional scripts.

## 📋 Step 0: Prerequisites 
Before deploying, ensure you have the following files in your root directory:
- `app.py`: The primary Streamlit frontend.
- `requirements.txt`: The dependency list (including `pybaseball`).
- `deploy_master.py`: The deployment orchestration script.
- `.appdeploy`: Your secure configuration file (automatically created).

---

## 🏗️ Step 1: Local Verification
Always verify that your app runs correctly on your local machine before pushing "to the cloud."

1. Open your terminal in the project root.
2. Run:
```bash
streamlit run app.py
```
3. Ensure the **2026 Situational Matrix** and **Pitcher Matrix** are loading correctly.

---

## 🚀 Step 2: The Master Push
Once you are satisfied with your local changes, execute the "Master Push" to migrate your code to the production environment.

// turbo
1. Execute the deployment script:
```powershell
python deploy_master.py
```
2. The script will bundle your assets and return a **New App ID** (e.g., `bd113bc4a9f442e68f`).

---

## 🛰️ Step 3: Readiness Polling
AppDeploy takes 2–3 minutes to provision your instance (installing libraries like `pybaseball`, `xgboost`, and `duckdb`).

// turbo
1. Check the status of your rollout:
```powershell
python check_status.py
```
2. Wait for the terminal to report `Status: ready`.
3. Once ready, the script will provide your **Live Terminal URL**.

---

## 🏛️ Summary of Best Practices
- **Persistence**: Your Google Sheets cloud-ledger for betting logs is persistent across deployments.
- **Data Sync**: The 2026 scraper automatically hydrates your cloud instance's memory.
- **Rollback**: If a build fails, you can always reference your previous "READY" App ID.

> [!TIP]
> **Dynamic Alpha**: Deploy whenever you update the `core/scraper_engine.py` logic to ensure your cloud terminal has the absolute latest 2026 situational coefficients.
