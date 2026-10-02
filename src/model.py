"""Bucket-probability model: multinomial logistic on log(1 + final subscription)."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent
EDGES = [0, 10, 30]
LABELS = ["<=0%", "0-10%", "10-30%", "30%+"]


def load():
    cols = ["sub_x", "gain_open_pct", "gain_close_pct"]
    return pd.read_csv(ROOT / "data/ipos.csv", parse_dates=["listing_date"]).dropna(subset=cols)


def bucket(gain_pct):
    return np.digitize(gain_pct, EDGES, right=True)


def fit(df, target):
    return LogisticRegression(max_iter=1000).fit(np.log1p(df[["sub_x"]].to_numpy()), bucket(df[target].to_numpy()))


def bucket_probs(model, sub_x):
    p = model.predict_proba(np.log1p(np.asarray(sub_x, float).reshape(-1, 1)))
    out = np.zeros((len(p), len(LABELS)))
    out[:, model.classes_] = p  # classes absent from training stay at 0
    return out


if __name__ == "__main__":
    assert list(bucket(np.array([-5, 0, 0.1, 10, 10.1, 30, 31]))) == [0, 0, 1, 1, 2, 2, 3]
    df = load()
    p = bucket_probs(fit(df, "gain_open_pct"), [0.5, 5, 50, 200])
    assert np.allclose(p.sum(axis=1), 1) and p[3, 0] < p[0, 0]  # more subscription, less loss
    print("model self-check ok")
