import pandas as pd
import numpy as np
from pathlib import Path


class MarketingDataAnalyzer:
    """마케팅 데이터 분석 클래스"""

    def __init__(self, data_dir: str = "./"):
        self.data_dir = Path(data_dir)
        self.data = {}

    def load_data(self, filename: str) -> pd.DataFrame:
        """CSV 파일 로드"""
        filepath = self.data_dir / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            self.data[filename] = df
            return df
        return None

    def load_excel_data(self, filename: str, sheet_name: str = 0) -> pd.DataFrame:
        """Excel 파일 로드"""
        filepath = self.data_dir / filename
        if filepath.exists():
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            self.data[filename] = df
            return df
        return None

    def get_summary_stats(self, df: pd.DataFrame) -> dict:
        """데이터 요약 통계"""
        return {
            "행 수": len(df),
            "열 수": len(df.columns),
            "NULL 값": df.isnull().sum().to_dict(),
            "데이터 타입": df.dtypes.to_dict(),
        }

    def get_numeric_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """수치형 컬럼 요약"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        return df[numeric_cols].describe().round(2)

    def detect_outliers(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """IQR을 사용한 이상치 탐지"""
        outlier_indices = []
        for col in columns:
            if col in df.columns and df[col].dtype in [np.float64, np.int64]:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outlier_indices.extend(df[(df[col] < lower) | (df[col] > upper)].index)

        return df.iloc[list(set(outlier_indices))] if outlier_indices else pd.DataFrame()

    def calculate_growth_rate(self, df: pd.DataFrame, value_col: str, period_col: str = None) -> dict:
        """성장률 계산"""
        if period_col and period_col in df.columns:
            grouped = df.groupby(period_col)[value_col].sum()
            growth_rates = grouped.pct_change() * 100
            return growth_rates.to_dict()
        else:
            total = df[value_col].sum()
            return {"총합": total}

    def segment_analysis(self, df: pd.DataFrame, segment_col: str, metric_col: str) -> pd.DataFrame:
        """세그먼트별 분석"""
        if segment_col in df.columns and metric_col in df.columns:
            return df.groupby(segment_col)[metric_col].agg(['count', 'sum', 'mean', 'std']).round(2)
        return pd.DataFrame()
