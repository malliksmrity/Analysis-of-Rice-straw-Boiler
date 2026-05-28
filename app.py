import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Rice Straw Boiler Analysis", layout="wide")

st.title("🔥 Rice Straw Boiler Performance Dashboard")
st.subheader("Combustion Efficiency Prediction & Analysis")
st.markdown("Based on Design and Simulation research — Published at RDME-2025")

# Training data
df = pd.DataFrame({
    'Load (%)': [60, 70, 80, 90, 100],
    'Excess Air (%)': [40, 50, 60, 65, 70],
    'Air Flow Rate (kg/hr)': [10214, 12585, 15175, 17455, 19845],
    'O2 in Flue Gas (%)': [6.00, 7.00, 7.88, 8.27, 8.65],
    'Combustion Efficiency (%)': [93.2, 92.4, 91.7, 91.4, 91.1]
})

# Train model
X = df[['Load (%)', 'Excess Air (%)', 
        'Air Flow Rate (kg/hr)', 'O2 in Flue Gas (%)']]
y = df['Combustion Efficiency (%)']
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Sidebar inputs
st.sidebar.header("Input Boiler Parameters")
load = st.sidebar.slider("Boiler Load (%)", 60, 100, 80)
excess_air = st.sidebar.slider("Excess Air (%)", 40, 70, 55)

# Calculate dependent values
stoich_afr = 3.6479
fuel_qty = 2000 + (load - 60) * 30
afr = stoich_afr * (1 + excess_air/100)
air_flow = afr * fuel_qty
o2 = excess_air / (excess_air + 100) * 21

# Predict
efficiency = model.predict([[load, excess_air, air_flow, o2]])[0]

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Boiler Load", f"{load}%")
col2.metric("Excess Air", f"{excess_air}%")
col3.metric("Air Flow Rate", f"{air_flow:.0f} kg/hr")
col4.metric("Predicted Efficiency", f"{efficiency:.2f}%")

# Efficiency gauge
st.subheader("Predicted Combustion Efficiency")
fig, ax = plt.subplots(figsize=(10, 3))
ax.barh(['Efficiency'], [efficiency], color='green' if efficiency > 92 else 'orange')
ax.barh(['Efficiency'], [100 - efficiency], left=[efficiency], color='lightgray')
ax.set_xlim(0, 100)
ax.set_xlabel('Efficiency (%)')
ax.axvline(x=92, color='red', linestyle='--', label='Target (92%)')
ax.legend()
ax.set_title(f'Current Efficiency: {efficiency:.2f}%')
st.pyplot(fig)

# Two columns for charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Load vs Combustion Efficiency")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(df['Load (%)'], df['Combustion Efficiency (%)'], 
             marker='o', color='blue', label='Simulated')
    ax2.axvline(x=load, color='red', linestyle='--', label=f'Current: {load}%')
    ax2.set_xlabel('Load (%)')
    ax2.set_ylabel('Efficiency (%)')
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

with col_right:
    st.subheader("Excess Air vs Predicted Efficiency")
    ea_range = np.linspace(40, 80, 50)
    preds = []
    for ea in ea_range:
        afr_t = stoich_afr * (1 + ea/100)
        af_t = afr_t * fuel_qty
        o2_t = ea / (ea + 100) * 21
        preds.append(model.predict([[load, ea, af_t, o2_t]])[0])
    
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(ea_range, preds, color='darkgreen', linewidth=2)
    ax3.axvline(x=excess_air, color='red', linestyle='--', 
                label=f'Current: {excess_air}%')
    ax3.set_xlabel('Excess Air (%)')
    ax3.set_ylabel('Predicted Efficiency (%)')
    ax3.legend()
    ax3.grid(True)
    st.pyplot(fig3)

# Optimization tip
st.subheader("💡 Optimization Recommendation")
optimal_ea = ea_range[np.argmax(preds)]
max_eff = max(preds)

if excess_air > optimal_ea + 5:
    st.warning(f"⚠️ Excess air is too high ({excess_air}%). "
               f"Reduce to {optimal_ea:.0f}% to improve efficiency "
               f"to {max_eff:.2f}%")
elif efficiency > 92:
    st.success(f"✅ Boiler operating efficiently at {efficiency:.2f}%. "
               f"Current parameters are optimal.")
else:
    st.info(f"ℹ️ Optimal excess air for this load: {optimal_ea:.0f}%. "
            f"Potential efficiency: {max_eff:.2f}%")

# Data table
st.subheader("Simulation Data")
st.dataframe(df)

st.markdown("---")
st.markdown("**Smrity Mallik** | MSc AI & Data Science | "
            "Mechanical Engineering | Published Researcher")