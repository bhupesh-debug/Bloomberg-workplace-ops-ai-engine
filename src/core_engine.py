"""
Bloomberg Workplace Operations & Real Estate FP&A Core Engine
Author: Bhupesh Chandra Dimri
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class FacilityMetric:
    facility_id: str
    location: str
    region: str
    total_sqft: float
    usable_desks: int
    occupied_desks: int
    monthly_rent: float
    monthly_opex: float
    monthly_capex: float

    @property
    def occupancy_rate(self) -> float:
        if self.usable_desks == 0:
            return 0.0
        return self.occupied_desks / self.usable_desks

    @property
    def total_monthly_cost(self) -> float:
        return self.monthly_rent + self.monthly_opex + self.monthly_capex

    @property
    def cost_per_desk(self) -> float:
        if self.usable_desks == 0:
            return 0.0
        return self.total_monthly_cost / self.usable_desks

    @property
    def cost_per_occupied_desk(self) -> float:
        if self.occupied_desks == 0:
            return 0.0
        return self.total_monthly_cost / self.occupied_desks


class WorkplaceFPnAEngine:
    """Enterprise financial planning & variance analytics for workplace facilities."""

    def __init__(self, facilities: Optional[List[FacilityMetric]] = None):
        self.facilities: Dict[str, FacilityMetric] = {}
        if facilities:
            for f in facilities:
                self.add_facility(f)

    def add_facility(self, facility: FacilityMetric):
        self.facilities[facility.facility_id] = facility

    def calculate_portfolio_kpis(self) -> Dict[str, float]:
        if not self.facilities:
            return {
                "total_sqft": 0.0,
                "total_desks": 0,
                "total_occupied": 0,
                "avg_occupancy_rate": 0.0,
                "total_monthly_spend": 0.0,
                "portfolio_cost_per_desk": 0.0
            }

        total_sqft = sum(f.total_sqft for f in self.facilities.values())
        total_desks = sum(f.usable_desks for f in self.facilities.values())
        total_occupied = sum(f.occupied_desks for f in self.facilities.values())
        total_spend = sum(f.total_monthly_cost for f in self.facilities.values())

        avg_occ = (total_occupied / total_desks) if total_desks > 0 else 0.0
        cost_per_desk = (total_spend / total_desks) if total_desks > 0 else 0.0

        return {
            "total_sqft": total_sqft,
            "total_desks": total_desks,
            "total_occupied": total_occupied,
            "avg_occupancy_rate": round(avg_occ, 4),
            "total_monthly_spend": round(total_spend, 2),
            "portfolio_cost_per_desk": round(cost_per_desk, 2)
        }

    def variance_decomposition(
        self, budget: float, actual: float, volume_budget: float, volume_actual: float
    ) -> Dict[str, float]:
        """Decomposes total budget variance into rate (price) variance and volume (usage) variance."""
        total_variance = actual - budget
        rate_budget = budget / volume_budget if volume_budget > 0 else 0.0
        rate_actual = actual / volume_actual if volume_actual > 0 else 0.0

        # Rate Variance = (Rate_Actual - Rate_Budget) * Volume_Actual
        rate_variance = (rate_actual - rate_budget) * volume_actual
        # Volume Variance = (Volume_Actual - Volume_Budget) * Rate_Budget
        volume_variance = (volume_actual - volume_budget) * rate_budget

        unexplained = total_variance - (rate_variance + volume_variance)

        return {
            "total_variance": round(total_variance, 2),
            "rate_variance": round(rate_variance, 2),
            "volume_variance": round(volume_variance, 2),
            "unexplained_delta": round(unexplained, 2),
            "is_favorable": total_variance < 0
        }

    def detect_spend_anomalies(self, spend_series: List[float], threshold_z: float = 2.0) -> List[Dict[str, any]]:
        """Identifies outlier cost center spends using dynamic Z-score filtering."""
        arr = np.array(spend_series)
        if len(arr) < 3:
            return []

        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return []

        anomalies = []
        for idx, val in enumerate(arr):
            z = (val - mean) / std
            if abs(z) >= threshold_z:
                anomalies.append({
                    "period_index": idx,
                    "spend_amount": float(val),
                    "z_score": round(float(z), 2),
                    "direction": "HIGH" if z > 0 else "LOW"
                })
        return anomalies

    def forecast_rolling_opex(self, historical_spend: List[float], periods_ahead: int = 3, growth_rate: float = 0.02) -> List[float]:
        """Projects future monthly facility run-rate with compounding inflation/growth."""
        if not historical_spend:
            return []
        recent_baseline = float(np.mean(historical_spend[-3:])) if len(historical_spend) >= 3 else float(historical_spend[-1])
        forecast = []
        current = recent_baseline
        for _ in range(periods_ahead):
            current *= (1.0 + growth_rate)
            forecast.append(round(current, 2))
        return forecast
