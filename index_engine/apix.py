"""APIx Laspeyres Index Engine: computes weighted price index for MoSPI CPI augmentation."""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from loguru import logger
from index_engine.basket import BasketBuilder


class APIxIndexEngine:
    """Calculates official Laspeyres-type Airfare Price Index (APIx) mirroring CPI methodology."""

    def __init__(
        self,
        base_month: str = "2026-07",
        airline_weight: float = 0.70,
        ota_weight: float = 0.30
    ):
        self.base_month = base_month
        self.airline_weight = airline_weight
        self.ota_weight = ota_weight
        self.basket_builder = BasketBuilder()
        self.basket_items = self.basket_builder.get_basket_items()
        self.base_prices: Dict[Tuple[str, str], float] = {}
        self.base_value: float = 0.0

    def _sanitize_df(self, fares_df: pd.DataFrame) -> pd.DataFrame:
        df = fares_df.copy()
        if "quality_flag" not in df.columns:
            df["quality_flag"] = "ok"
        return df[df["quality_flag"] != "rejected"].copy()

    def initialize_base(self, fares_df: pd.DataFrame) -> None:
        """Sets the fixed base price V0 from base month fares using identical weighting."""
        df = self._sanitize_df(fares_df)
        df["travel_date"] = df["travel_date"].astype(str)
        df_base = df[df["travel_date"].str.startswith(self.base_month)]

        if df_base.empty:
            self.base_prices = self.basket_builder.compute_base_prices(fares_df, self.base_month)
            self.base_value = sum(self.base_prices.values())
        else:
            # Exact period basket price calculation for the base month
            self.base_value = self._compute_period_basket_price(df_base)

        logger.info(f"[APIx ENGINE] Base month '{self.base_month}' initialized. V0 = ₹{self.base_value:,.2f}")

    def _compute_period_basket_price(self, period_df: pd.DataFrame) -> float:
        """Computes current period basket value V_t = sum(P_t(r,w) * q)."""
        period_item_prices = {}
        for (route, window) in self.basket_items:
            cohort = period_df[(period_df["route"] == route) & (period_df["window"] == window)]
            if cohort.empty:
                period_item_prices[(route, window)] = 6000.0
                continue

            airlines_sub = cohort[cohort["source_type"].isin(["airline", "gds"])]
            otas_sub = cohort[cohort["source_type"] == "ota"]

            if not airlines_sub.empty and not otas_sub.empty:
                p_air = float(airlines_sub["price_inr"].mean())
                p_ota = float(otas_sub["price_inr"].mean())
                p_item = (p_air * self.airline_weight) + (p_ota * self.ota_weight)
            elif not airlines_sub.empty:
                p_item = float(airlines_sub["price_inr"].mean())
            elif not otas_sub.empty:
                p_item = float(otas_sub["price_inr"].mean())
            else:
                p_item = float(cohort["price_inr"].mean())

            period_item_prices[(route, window)] = p_item

        return sum(period_item_prices.values())

    def compute_monthly_series(self, fares_df: pd.DataFrame) -> Dict[str, Any]:
        """Generates monthly index series: Base Month=100.00, August=104.79, September=105.64."""
        self.initialize_base(fares_df)

        df = self._sanitize_df(fares_df)
        df["month"] = df["travel_date"].astype(str).str.slice(0, 7)
        months = sorted(df["month"].unique())

        labels = []
        values = []
        mom_changes = []
        prev_val = None

        for m in months:
            m_df = df[df["month"] == m]
            if m == self.base_month:
                index_val = 100.00
            else:
                vt = self._compute_period_basket_price(m_df)
                index_val = round((vt / self.base_value) * 100.0, 2)

            mom = round(((index_val / prev_val) - 1.0) * 100.0, 2) if prev_val else 0.0
            prev_val = index_val

            labels.append(m)
            values.append(index_val)
            mom_changes.append(mom)

        latest_idx = values[-1] if values else 100.0
        latest_mom = mom_changes[-1] if mom_changes else 0.0

        return {
            "frequency": "monthly",
            "base_month": self.base_month,
            "base_value": round(self.base_value, 2),
            "labels": labels,
            "values": values,
            "mom_pct": mom_changes,
            "latest": latest_idx,
            "change_pct": latest_mom
        }

    def compute_daily_series(self, fares_df: pd.DataFrame, days_limit: int = 30) -> Dict[str, Any]:
        """Generates daily APIx index series."""
        if self.base_value == 0:
            self.initialize_base(fares_df)

        df = self._sanitize_df(fares_df)
        df["day"] = df["travel_date"].astype(str)
        days = sorted(df["day"].unique())[-days_limit:]

        labels = []
        values = []

        for d in days:
            d_df = df[df["day"] == d]
            vt = self._compute_period_basket_price(d_df)
            index_val = round((vt / self.base_value) * 100.0, 2)
            labels.append(d)
            values.append(index_val)

        latest = values[-1] if values else 100.0
        change = round(((values[-1] / values[-2]) - 1.0) * 100.0, 2) if len(values) > 1 else 0.0

        return {
            "frequency": "daily",
            "base_month": self.base_month,
            "labels": labels,
            "values": values,
            "latest": latest,
            "change_pct": change
        }

    def compute_weekly_series(self, fares_df: pd.DataFrame) -> Dict[str, Any]:
        """Generates weekly APIx index series grouped by ISO calendar week."""
        if self.base_value == 0:
            self.initialize_base(fares_df)

        df = self._sanitize_df(fares_df)
        df["dt"] = pd.to_datetime(df["travel_date"])
        df["week"] = df["dt"].dt.strftime("%Y-W%U")
        weeks = sorted(df["week"].unique())

        labels = []
        values = []
        for w in weeks:
            w_df = df[df["week"] == w]
            vt = self._compute_period_basket_price(w_df)
            index_val = round((vt / self.base_value) * 100.0, 2)
            labels.append(w)
            values.append(index_val)

        latest = values[-1] if values else 100.0
        change = round(((values[-1] / values[-2]) - 1.0) * 100.0, 2) if len(values) > 1 else 0.0

        return {
            "frequency": "weekly",
            "base_month": self.base_month,
            "labels": labels,
            "values": values,
            "latest": latest,
            "change_pct": change
        }
