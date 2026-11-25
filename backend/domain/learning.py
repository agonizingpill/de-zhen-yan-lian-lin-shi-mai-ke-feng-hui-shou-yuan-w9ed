from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import RobustScaler
from domain.states import FEATURES, Finding, HERTZ_TOLERANCE, MIN_SHARED_POINTS, SCORE_LIMIT


def vector(row):
    return [float(row[field]) for field in FEATURES]


def relative_to(focus, clips):
    return [row["point"] for row in clips if row["channel"] == focus["channel"]
            and abs(row["frequency"] - focus["frequency"]) <= HERTZ_TOLERANCE
            and row["peak_share"] >= .62 and row["ring_index"] >= .52]


def calculate(payload):
    base=payload["baseline"]
    focus=payload["focus"]
    if len(base)<12:
        raise ValueError("基线不足 12 个声检窗")
    scale = RobustScaler()
    samples = scale.fit_transform([vector(row) for row in base])
    neighbors = min(8, len(base)-1)
    model = LocalOutlierFactor(n_neighbors=neighbors,novelty=True)
    model.fit(samples)
    score=float(model.score_samples(scale.transform([vector(focus)]))[0])
    shared=sorted(set(relative_to(focus,payload["simultaneous"])))
    if score>=SCORE_LIMIT:
        category=Finding.NORMAL
    elif len(shared)>=MIN_SHARED_POINTS and focus["point"] in shared:
        category=Finding.COORDINATED
    else:
        category=Finding.LOCAL
    return {"algorithm":"LOF","reference_windows":len(base),"neighbors":neighbors,"score":score,
            "threshold":SCORE_LIMIT,"shared_points":shared,"category":str(category)}
