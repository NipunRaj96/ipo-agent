"""Walk-forward evaluation: for each test year, train only on earlier years."""
import numpy as np

from model import LABELS, bucket, bucket_probs, fit, load

TARGETS = {"listing open": "gain_open_pct", "day-1 close": "gain_close_pct"}
YEARS = (2023, 2024, 2025)
PBINS = [0, 0.1, 0.25, 0.5, 1.0001]


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def walk_forward(df, target):
    probs, ys, base = [], [], []
    for year in YEARS:
        tr, te = df[df.listing_date.dt.year < year], df[df.listing_date.dt.year == year]
        probs.append(bucket_probs(fit(tr, target), te.sub_x))
        ys.append(bucket(te[target].to_numpy()))
        freq = np.bincount(bucket(tr[target].to_numpy()), minlength=len(LABELS)) / len(tr)
        base.append(np.tile(freq, (len(te), 1)))
    return np.vstack(probs), np.concatenate(ys), np.vstack(base)


def brier(p, y):
    return np.mean(np.sum((p - np.eye(len(LABELS))[y]) ** 2, axis=1))


def main():
    df = load()
    for name, target in TARGETS.items():
        p, y, base = walk_forward(df, target)
        print(f"\n=== {name} | n={len(y)} out-of-sample ({YEARS[0]}-{YEARS[-1]}) ===")
        print(f"Brier model={brier(p, y):.3f} vs base-rate={brier(base, y):.3f} (lower is better)")
        print("actual share per bucket:", {l: round(float((y == i).mean()), 2) for i, l in enumerate(LABELS)})
        print("reliability (predicted prob bin: n, mean predicted, actual freq)")
        for i, label in enumerate(LABELS):
            cells = []
            for lo, hi in zip(PBINS[:-1], PBINS[1:]):
                m = (p[:, i] >= lo) & (p[:, i] < hi)
                if m.sum() >= 5:
                    cells.append(f"[{lo:.2f},{min(hi, 1):.2f}) n={m.sum()} pred={p[m, i].mean():.2f} act={(y[m] == i).mean():.2f}")
            print(f"  {label:7s}", " | ".join(cells))
        not_loss = 1 - p[:, 0]
        for thr in (0.8, 0.9):
            m = not_loss >= thr
            if m.sum():
                k, n = int((y[m] > 0).sum()), int(m.sum())
                lo, hi = wilson(k, n)
                print(f"apply if P(not loss)>={thr}: {n}/{len(y)} picks, precision {k/n:.3f} (95% CI {lo:.2f}-{hi:.2f})")


if __name__ == "__main__":
    main()
