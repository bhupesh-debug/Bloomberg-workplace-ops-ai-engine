"""
Bloomberg Workplace Operations & Real Estate FP&A Streamlit Portal
Author: Bhupesh Chandra Dimri
"""

import streamlit as st
import pandas as pd
import numpy as np
from src.core_engine import FacilityMetric, WorkplaceFPnAEngine

st.set_page_config(page_title="Bloomberg Workplace Operations FP&A Portal", layout="wide")

st.title("Bloomberg Finance L.P. — Workplace Operations & Real Estate FP&A Engine")
st.markdown("**Enterprise Cost Center Governance, Capex/Opex Decomposition & Predictive Analytics**")

engine = WorkplaceFPnAEngine()
engine.add_facility(FacilityMetric("FAC-731-LEX", "731 Lexington Ave, New York", "AMER", 250000, 1800, 1550, 1850000, 450000, 200000))
engine.add_facility(FacilityMetric("FAC-399-PARK", "399 Park Ave, New York", "AMER", 120000, 900, 780, 950000, 220000, 90000))
engine.add_facility(FacilityMetric("FAC-3-QUEEN", "3 Queen Victoria St, London", "EMEA", 180000, 1400, 1200, 1400000, 380000, 150000))
engine.add_facility(FacilityMetric("FAC-MARUNOUCHI", "Marunouchi Building, Tokyo", "APAC", 95000, 700, 620, 850000, 190000, 80000))

kpis = engine.calculate_portfolio_kpis()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Usable Desks", f"{kpis['total_desks']:,}")
col2.metric("Portfolio Occupancy", f"{kpis['avg_occupancy_rate']*100:.1f}%")
col3.metric("Total Monthly Spend", f"${kpis['total_monthly_spend']:,.2f}")
col4.metric("Avg Cost Per Desk", f"${kpis['portfolio_cost_per_desk']:,.2f}")

st.subheader("Regional Facility Cost & Occupancy Breakdown")
facility_rows = [
    {
        "Facility ID": f.facility_id,
        "Location": f.location,
        "Region": f.region,
        "SqFt": f.total_sqft,
        "Desks": f.usable_desks,
        "Occupied": f.occupied_desks,
        "Occupancy": f"{f.occupancy_rate*100:.1f}%",
        "Total Monthly Cost": f"${f.total_monthly_cost:,.2f}",
        "Cost / Desk": f"${f.cost_per_desk:,.2f}"
    }
    for f in engine.facilities.values()
]
st.dataframe(pd.DataFrame(facility_rows), use_container_width=True)

st.subheader("Variance Decomposition Simulator (Rate vs. Volume)")
vcol1, vcol2 = st.columns(2)
with vcol1:
    budget_spend = st.number_input("Budget Allocated ($)", value=2500000.0, step=50000.0)
    budget_desks = st.number_input("Budgeted Headcount / Desks", value=2000.0, step=50.0)
with vcol2:
    actual_spend = st.number_input("Actual Spend ($)", value=2720000.0, step=50000.0)
    actual_desks = st.number_input("Actual Headcount / Desks", value=2100.0, step=50.0)

decomp = engine.variance_decomposition(budget_spend, actual_spend, budget_desks, actual_desks)
st.write(f"**Total Variance:** ${decomp['total_variance']:,.2f} ({'Favorable' if decomp['is_favorable'] else 'Unfavorable'})")
st.write(f"• **Rate (Cost-per-Unit) Variance:** ${decomp['rate_variance']:,.2f}")
st.write(f"• **Volume (Capacity Usage) Variance:** ${decomp['volume_variance']:,.2f}")
