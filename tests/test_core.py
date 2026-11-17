"""Unit tests for Bloomberg Workplace Operations FP&A Engine."""

import pytest
from src.core_engine import FacilityMetric, WorkplaceFPnAEngine


def test_facility_metric_properties():
    f = FacilityMetric(
        facility_id="FAC-NYC-731",
        location="731 Lexington Ave, NY",
        region="AMER",
        total_sqft=150000.0,
        usable_desks=1000,
        occupied_desks=850,
        monthly_rent=850000.0,
        monthly_opex=250000.0,
        monthly_capex=100000.0
    )
    assert f.occupancy_rate == 0.85
    assert f.total_monthly_cost == 1200000.0
    assert f.cost_per_desk == 1200.0
    assert round(f.cost_per_occupied_desk, 2) == 1411.76


def test_portfolio_kpis_calculation():
    engine = WorkplaceFPnAEngine()
    f1 = FacilityMetric("F1", "NYC", "AMER", 100000, 500, 400, 400000, 100000, 50000)
    f2 = FacilityMetric("F2", "LON", "EMEA", 80000, 400, 300, 300000, 80000, 40000)
    engine.add_facility(f1)
    engine.add_facility(f2)

    kpis = engine.calculate_portfolio_kpis()
    assert kpis["total_sqft"] == 180000.0
    assert kpis["total_desks"] == 900
    assert kpis["total_occupied"] == 700
    assert round(kpis["avg_occupancy_rate"], 2) == 0.78
    assert kpis["total_monthly_spend"] == 970000.0


def test_variance_decomposition():
    engine = WorkplaceFPnAEngine()
    # Budget: $500k for 500 desks ($1,000/desk)
    # Actual: $570k for 520 desks ($1,096.15/desk)
    decomp = engine.variance_decomposition(
        budget=500000.0,
        actual=570000.0,
        volume_budget=500.0,
        volume_actual=520.0
    )
    assert decomp["total_variance"] == 70000.0
    assert decomp["is_favorable"] is False
    assert abs(decomp["unexplained_delta"]) < 1.0


def test_spend_anomaly_detection():
    engine = WorkplaceFPnAEngine()
    history = [100000, 102000, 99000, 101000, 103000, 250000, 100500]  # Outlier spike at 250k
    anomalies = engine.detect_spend_anomalies(history, threshold_z=2.0)
    assert len(anomalies) >= 1
    assert anomalies[0]["spend_amount"] == 250000.0
    assert anomalies[0]["direction"] == "HIGH"


def test_forecast_rolling_opex():
    engine = WorkplaceFPnAEngine()
    history = [100000, 102000, 104000]
    forecast = engine.forecast_rolling_opex(history, periods_ahead=3, growth_rate=0.03)
    assert len(forecast) == 3
    assert forecast[0] > 102000
    assert forecast[1] > forecast[0]
    assert forecast[2] > forecast[1]
