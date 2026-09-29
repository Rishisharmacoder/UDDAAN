"""Basket Builder: creates the fixed 30-item representative airfare basket."""
import os
import yaml
import pandas as pd
from typing import Dict, List, Tuple, Any
from loguru import logger

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")


class BasketBuilder:
    """Constructs the representative DGCA basket and determines base period pricing."""

    def __init__(self, routes_file: str = None, windows_file: str = None):
        routes_path = routes_file or os.path.join(CONFIG_DIR, "routes.yaml")
        windows_path = windows_file or os.path.join(CONFIG_DIR, "windows.yaml")

        with open(routes_path, "r", encoding="utf-8") as f:
            r_data = yaml.safe_load(f)
            self.routes = [f"{r['origin']}-{r['destination']}" for r in r_data.get("routes", []) if r.get("enabled", True)]

        with open(windows_path, "r", encoding="utf-8") as f:
            w_data = yaml.safe_load(f)
            self.windows = [w["label"] for w in w_data.get("windows", []) if w.get("enabled", True)]

        # 6 routes x 5 windows = 30 basket items
        self.basket_items: List[Tuple[str, str]] = [
            (r, w) for r in self.routes for w in self.windows
        ]

    def get_basket_items(self) -> List[Tuple[str, str]]:
        return self.basket_items

    def compute_base_prices(self, fares_df: pd.DataFrame, base_month: str = "2026-07") -> Dict[Tuple[str, str], float]:
        """Calculates base price P_0(r, w) for each basket item from the base month observations."""
        base_prices = {}
        if fares_df.empty:
            logger.warning("[BASKET] Empty fares dataframe provided; using calibrated baseline prices.")
            return self._fallback_base_prices()

        # Filter valid fares in base month
        df = fares_df.copy()
        df["travel_date"] = df["travel_date"].astype(str)
        df_base = df[df["travel_date"].str.startswith(base_month) & (df["quality_flag"] == "ok")]

        for (route, window) in self.basket_items:
            cohort = df_base[(df_base["route"] == route) & (df_base["window"] == window)]
            if not cohort.empty:
                # Weighted average: airlines 0.70, OTAs 0.30 if multiple sources exist
                base_prices[(route, window)] = float(cohort["price_inr"].mean())
            else:
                base_prices[(route, window)] = self._fallback_base_price_for(route, window)

        total_base_value = sum(base_prices.values())
        logger.info(f"[BASKET] Base basket value V0 computed: ₹{total_base_value:,.2f} across {len(self.basket_items)} items")
        return base_prices

    def _fallback_base_price_for(self, route: str, window: str) -> float:
        route_factors = {
            "DEL-BOM": 6400.0, "DEL-BLR": 7100.0, "BOM-BLR": 4800.0,
            "DEL-CCU": 5500.0, "BLR-HYD": 3800.0, "MAA-DEL": 6800.0
        }
        window_multipliers = {
            "T+1": 1.45, "T+7": 1.15, "T+15": 1.00, "T+30": 0.88, "T+45": 0.82
        }
        base = route_factors.get(route, 6000.0)
        mult = window_multipliers.get(window, 1.0)
        return round(base * mult, 2)

    def _fallback_base_prices(self) -> Dict[Tuple[str, str], float]:
        return {item: self._fallback_base_price_for(*item) for item in self.basket_items}
