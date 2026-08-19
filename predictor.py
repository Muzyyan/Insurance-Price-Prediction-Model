
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


FEATURE_ORDER = ["age", "is_female", "bmi", "children", "is_smoker", "region_southeast", "bmi_category_Obese"]
FIRST_SCALE_COLS = ["age", "bmi", "children"]

BMI_BINS = [0, 18.5, 24.9, 29.9, float("inf")]
BMI_LABELS = ["Underweight", "Normal", "Overweight", "Obese"]


class InsurancePredictor:
    def __init__(self) -> None:
        self.model = joblib.load("lnre.pkl")
        self.final_scaler: StandardScaler = joblib.load("scaler1.pkl")
        self.columns: list[str] = joblib.load("columns1.pkl")
        self.first_scaler = self._fit_first_scaler()

        if self.columns != FEATURE_ORDER:
            raise RuntimeError(
                f"columns1.pkl order {self.columns} does not match expected {FEATURE_ORDER}"
            )

    def _fit_first_scaler(self) -> StandardScaler:
        """Reproduce the notebook's first (unsaved) StandardScaler by
        refitting it on insurance.csv using the identical cleaning steps."""
        df = pd.read_csv("insurance.csv")
        df = df.drop_duplicates()
        scaler = StandardScaler()
        scaler.fit(df[FIRST_SCALE_COLS])
        return scaler

    @staticmethod
    def bmi_category(bmi: float) -> str:
        cat = pd.cut([bmi], bins=BMI_BINS, labels=BMI_LABELS)[0]
        return str(cat)

    def predict(
        self,
        age: int,
        sex: str,
        bmi: float,
        children: int,
        smoker: str,
        region: str,
    ) -> tuple[float, str]:
        is_female = 1 if sex == "female" else 0
        is_smoker = 1 if smoker == "yes" else 0
        region_southeast = 1 if region == "southeast" else 0
        category = self.bmi_category(bmi)
        bmi_category_obese = 1 if category == "Obese" else 0

        # Step 4: first standardization of age/bmi/children (fit on full CSV)
        first_scaled = self.first_scaler.transform([[age, bmi, children]])[0]
        scaled_age, scaled_bmi, scaled_children = first_scaled

        # Step 5: assemble the 7-feature vector in the exact trained order
        raw_vector = np.array(
            [
                [
                    scaled_age,
                    is_female,
                    scaled_bmi,
                    scaled_children,
                    is_smoker,
                    region_southeast,
                    bmi_category_obese,
                ]
            ]
        )

        # Step 6: second standardization with the persisted scaler
        final_vector = self.final_scaler.transform(raw_vector)

        # Step 7: predict
        prediction = float(self.model.predict(final_vector)[0])
        prediction = max(prediction, 0.0)  # charges can't be negative
        return round(prediction, 2), category


# Singleton instance loaded once at import time
predictor = InsurancePredictor()
