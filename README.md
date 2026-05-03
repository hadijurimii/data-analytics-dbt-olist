# 🚀 Lance Data Engineering Project  
**End-to-End Analytics Pipeline on Olist E-commerce Dataset**

---

## 🌟 Overview

This project builds a **production-style data platform (locally!)** to analyze the Olist Brazilian e-commerce dataset.

Instead of overengineering, the focus is on:
- ✅ Clean architecture  
- ✅ Reproducibility  
- ✅ Business-driven insights  
- ✅ Interview-ready explanations  

💡 *Think of this as a “mini data platform” you can confidently defend in front of senior engineers.*

---

## 🧱 Architecture

<img width="2948" height="540" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/9dcd8f6b-9b3d-425a-b386-169388c13527" />

---

## 📈 Business Insights

### 💰 Revenue & Seasonality

- Strong revenue growth observed in **health_beauty** and **watches_gifts** categories  
- Monthly GMV trends show consistent upward momentum with occasional spikes  
- Anomaly detection (z-score) highlights unusual peaks in specific categories  

💡 **Key Insight:**  
Public holidays alone do **not strongly explain revenue spikes**.  
Promotions, campaigns, and marketplace dynamics are more likely drivers.

---

### 🔁 Customer Retention

- Overall repeat purchase rate (within 90 days) is **low (~1–1.6%)**
- Indicates a **transactional marketplace behavior** with many one-time buyers  
- States with relatively higher retention:
  - ES  
  - MT  
  - SP  

💡 **Key Insight:**  
Retention is not evenly distributed across regions.

---

### 🚚 Delivery vs Customer Satisfaction

- Late deliveries strongly correlate with **low review scores**
- Worst-performing segments:
  - Cross-state shipments  
  - High-volume categories like *toys, baby, stationery*  

- Late deliveries often exceed **8–11 days delay**, significantly impacting satisfaction  

💡 **Key Insight:**  
Delivery performance is a **critical driver of customer experience**

---

### 💳 Payment Behavior

- **Credit card** is the dominant payment method, contributing the majority of total transaction value  
- Customers frequently use **installments**, with an average of ~3.5 payments per order  
- **Boleto** (bank transfer) is the second most used method but limited to single payments  
- **Voucher** and **debit card** usage remain relatively low  

💡 **Key Insight:**  
Brazilian e-commerce shows strong reliance on **credit-based purchasing with installments**

---

### 🌍 Customer Value by Region

- Customer value varies significantly across different states  
- High-value states include:
  - PB  
  - PA  
  - MT  

- Larger states (e.g., SP, RJ) generate high total GMV but not necessarily the highest **per-customer value**  

💡 **Key Insight:**  
High transaction volume ≠ high customer value  

---

## 📦 Outputs

The pipeline generates the following analytical outputs:

- `output/q1_top_monthly_category_gmv.csv`  
- `output/q1_anomaly_months.csv`  
- `output/q2_best_repeat_states.csv`  
- `output/q2_recent_cohorts.csv`  
- `output/q3_delivery_review_segments.csv`  
- `output/q4_payment_mix.csv`  
- `output/q5_customer_ltv_state.csv`  

💡 These outputs are designed to be:
- Easily consumable for analysis  
- Ready for dashboards or reporting  
- Structured for business decision-making  
