import pandas as pd
import numpy as np
from typing import List, Dict, Any


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """컬럼명을 소문자 및 언더스코어로 정규화"""
    df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
    return df


def fill_missing_values(df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
    """결측값 처리"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    if strategy == 'mean':
        for col in numeric_cols:
            df[col].fillna(df[col].mean(), inplace=True)
    elif strategy == 'median':
        for col in numeric_cols:
            df[col].fillna(df[col].median(), inplace=True)
    elif strategy == 'forward_fill':
        df.fillna(method='ffill', inplace=True)

    return df


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """중복 제거"""
    return df.drop_duplicates(subset=subset, keep='first')


def normalize_column(series: pd.Series, method: str = 'minmax') -> pd.Series:
    """컬럼 정규화"""
    if method == 'minmax':
        return (series - series.min()) / (series.max() - series.min())
    elif method == 'zscore':
        return (series - series.mean()) / series.std()
    return series


def categorize_numeric_data(series: pd.Series, bins: int = 5, labels: List[str] = None) -> pd.Series:
    """수치형 데이터 범주화"""
    if labels is None:
        labels = [f'Category_{i}' for i in range(1, bins + 1)]
    return pd.cut(series, bins=bins, labels=labels)


def get_top_values(df: pd.DataFrame, column: str, n: int = 5) -> pd.Series:
    """상위 N개 값 추출"""
    return df[column].value_counts().head(n)


def calculate_percentile(series: pd.Series, percentile: float) -> float:
    """백분위수 계산"""
    return np.percentile(series, percentile)


def group_and_aggregate(df: pd.DataFrame, groupby_col: str, agg_cols: Dict[str, List[str]]) -> pd.DataFrame:
    """그룹화 및 집계"""
    return df.groupby(groupby_col).agg(agg_cols)
