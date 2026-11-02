# Sales Forecasting & Classification Project Report

## 1. Executive Summary
This project presents an end-to-end machine learning system developed for a retail dataset of 10,000 transaction records. It addresses three primary business needs: classifying transactions into high/low sales volume, predicting exact transaction-level revenues, and forecasting aggregate future daily sales. By applying robust preprocessing, chronological splitting, and state-of-the-art tree-based ensemble models, the system delivers highly accurate predictions and actionable insights for business stakeholders.

## 2. Dataset & Preprocessing
The dataset consists of 10,000 records tracking 16 core features including: Store ID, Product ID, Category, Units Sold, Unit Price, Discount, Promotions, Inventory, Weather Score, and Sales Revenue.
- **Data Cleaning**: Handled zero/negative prices/units, sorted chronologically, and removed duplicate rows.
- **Preprocessing Pipeline**: Constructed a leakage-free Scikit-Learn `ColumnTransformer` pipeline. Numerical features are scaled via `StandardScaler` and imputed via median values. Categorical features are encoded via `OneHotEncoder`.

## 3. Methodology & Models
- **Target Definition**: Established a binary target ('Sales_Category') representing High vs. Low sales using the median sales revenue strictly calculated on the training partition ($264.27) to completely eliminate look-ahead leakage.
- **Classification**: Trained Logistic Regression, Decision Trees, Random Forests, HistGradientBoosting, and XGBoost Classifiers. Tree-based ensemble models (XGBoost/HistGradientBoosting) outperformed other baselines significantly.
- **Regression**: Modeled exact continuous transaction revenue comparing Linear Regression, Random Forests, HistGradientBoosting, and XGBoost Regressors.
- **Forecasting**: Aggregated data to a daily level. Sequential lags (Lag 1, 7, 14) and rolling means (7, 30 days) were constructed without look-ahead bias. Trained an XGBoost Regressor to predict future sales for the next 30 days.

## 4. Final Model Performance Comparison

### Classification (Validation vs. Test)
- **Champion Model**: XGBoost
- **Validation F1-Score**: 0.9894 | **Test F1-Score**: 0.9851
- **Validation Accuracy**: 0.9880 | **Test Accuracy**: 0.9827

### Regression (Validation vs. Test)
- **Champion Model**: XGBoost Regressor
- **Validation MAE**: 19.3528 | **Test MAE**: 28.6534
- **Validation R²**: 0.9941 | **Test R²**: 0.9862
- **Validation WAPE**: 0.0425 | **Test WAPE**: 0.0543

### Daily Forecasting (Test - Last 30 Days)
- **XGBoost Forecaster MAE**: 1987.55 | **Naive Baseline MAE**: 1948.12

## 5. Limitations & Future Outlook
- **Limitations**: The model is highly dependent on transaction-level feature density (such as units sold). Daily level forecasting currently lacks external trend features such as holiday events, weather aggregate shifts, or competitor price changes, limiting XGBoost's ability to easily beat a simple Naive Lag-1 baseline.
- **Future Outlook**: Future iterations should incorporate categorical embeddings for high-cardinality features like Store and Product IDs, explore deep learning architectures (LSTMs or Transformers) for multi-horizon forecasting, and ingest live macro-economic indexes to strengthen forecast robustness.
