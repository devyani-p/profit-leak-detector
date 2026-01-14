import streamlit as st
from logic import compute_metrics, detect_leaks, recommend_actions

st.set_page_config(page_title="Profit Leak Detector", layout="wide")

st.title("🧮 Profit Leak Detector")
st.caption("A calculator-style business analytics tool to find hidden profit leaks and suggest fixes.")

# -------- Sidebar Inputs --------
st.sidebar.header("📥 Enter your monthly business numbers")

units_sold = st.sidebar.number_input("Units sold (monthly)", min_value=0, value=1000, step=50)
price = st.sidebar.number_input("Selling price per unit (₹)", min_value=0.0, value=500.0, step=10.0)
cost = st.sidebar.number_input("Cost per unit (₹)", min_value=0.0, value=300.0, step=10.0)

discount_pct = st.sidebar.slider("Average discount (%)", 0, 70, 15)
return_pct = st.sidebar.slider("Return rate (%)", 0, 40, 6)

avg_stock_units = st.sidebar.number_input("Average stock held (units)", min_value=0, value=1500, step=50)
storage_cost_per_unit = st.sidebar.number_input("Storage cost per unit per month (₹)", min_value=0.0, value=5.0, step=1.0)

st.sidebar.divider()
st.sidebar.caption("Tip: If you don't know exact values, use best estimates. The app is meant for quick decision-making.")

# -------- Compute --------
metrics = compute_metrics(
    units_sold=units_sold,
    price=price,
    cost=cost,
    discount_pct=discount_pct,
    return_pct=return_pct,
    avg_stock_units=avg_stock_units,
    storage_cost_per_unit=storage_cost_per_unit,
)

leaks = detect_leaks(metrics)
actions = recommend_actions(leaks)

# -------- Layout --------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Key Metrics")
    st.metric("Revenue (₹)", f"{metrics['revenue']:,.0f}")
    st.metric("Gross Profit (₹)", f"{metrics['gross_profit']:,.0f}")
    st.metric("True Profit after leaks (₹)", f"{metrics['true_profit']:,.0f}")
    st.metric("Gross Margin (%)", f"{metrics['gross_margin_pct']:.1f}")

    with st.expander("See cost breakdown"):
        st.write(f"Discount loss: ₹{metrics['discount_loss']:,.0f}")
        st.write(f"Return loss: ₹{metrics['return_loss']:,.0f}")
        st.write(f"Inventory holding cost: ₹{metrics['inventory_cost']:,.0f}")

with col2:
    st.subheader("🚨 Biggest Profit Leaks")
    if not leaks:
        st.success("No major profit leaks detected based on the current thresholds.")
    else:
        for i, (name, amount) in enumerate(leaks[:5], start=1):
            st.warning(f"**{i}. {name}** — ₹{amount:,.0f}")

    st.subheader("✅ Recommended Actions")
    if not actions:
        st.info("No actions required right now.")
    else:
        for a in actions[:5]:
            st.write("•", a)

st.divider()

# -------- Scenario Simulator --------
st.subheader("🔁 Scenario Simulator (What if?)")
st.caption("Try small changes to discount and returns and see profit impact instantly.")

sim_col1, sim_col2, sim_col3 = st.columns([1, 1, 1])

with sim_col1:
    new_discount = st.slider("Try a new discount (%)", 0, 70, max(0, discount_pct - 5))
with sim_col2:
    new_return = st.slider("Try a new return rate (%)", 0, 40, max(0, return_pct - 1))
with sim_col3:
    new_storage = st.number_input("Try new storage cost (₹/unit/month)", min_value=0.0, value=storage_cost_per_unit, step=1.0)

scenario_metrics = compute_metrics(
    units_sold=units_sold,
    price=price,
    cost=cost,
    discount_pct=new_discount,
    return_pct=new_return,
    avg_stock_units=avg_stock_units,
    storage_cost_per_unit=new_storage,
)

delta = scenario_metrics["true_profit"] - metrics["true_profit"]

st.write(f"**Profit change if applied:** ₹{delta:,.0f}")
st.write(f"**New True Profit:** ₹{scenario_metrics['true_profit']:,.0f}")

# -------- Footer --------
st.divider()
st.caption("Note: This is a heuristic decision-support tool. Thresholds and formulas can be customized for your business.")
