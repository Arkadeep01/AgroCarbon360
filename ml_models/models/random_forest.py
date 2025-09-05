# ml_models/models/random_forest.py
from sklearn.ensemble import RandomForestRegressor

def build_random_forest(n_estimators=400, max_depth=None, min_samples_leaf=2, random_state=42):
    return RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
        n_jobs=-1
    )
