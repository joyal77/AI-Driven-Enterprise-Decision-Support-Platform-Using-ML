import os
import json
import warnings
import joblib
import sklearn.compose._column_transformer

warnings.filterwarnings("ignore", message=".*unpickle estimator.*")
warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")

# Monkeypatch missing class for scikit-learn version unpickling compatibility
class _RemainderColsList(list):
    pass

sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList

def patch_preprocessor(prep):
    for name, trans, cols in getattr(prep, 'transformers_', []):
        if hasattr(trans, 'steps'):
            for step_name, step_obj in trans.steps:
                if hasattr(step_obj, '_fit_dtype') and not hasattr(step_obj, '_fill_dtype'):
                    setattr(step_obj, '_fill_dtype', getattr(step_obj, '_fit_dtype'))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

def find_artifact(filename, subfolders=["churn", ""]):
    candidates = []
    for sub in subfolders:
        candidates.append(os.path.join(MODELS_DIR, sub, filename))
        candidates.append(os.path.join(PROJECT_ROOT, sub, filename))
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]

# Artifact Paths
rf_model_path = find_artifact("random_forest_model.joblib", ["churn", ""])
preprocessor_path = find_artifact("preprocessor.joblib", ["churn", ""])
metadata_path = find_artifact("model_metadata.json", ["churn", ""])
raw_features_path = find_artifact("raw_features_list.json", ["churn", ""])

rf_model = None
preprocessor = None
metadata = {}
raw_features = []

# Load Artifacts
if os.path.exists(rf_model_path):
    try:
        rf_model = joblib.load(rf_model_path)
        print(f"[ML Loader] Loaded Random Forest model from {rf_model_path}")
    except Exception as e:
        print(f"[ML Loader Error] Failed to load Random Forest model: {e}")

if os.path.exists(preprocessor_path):
    try:
        preprocessor = joblib.load(preprocessor_path)
        patch_preprocessor(preprocessor)
        print(f"[ML Loader] Loaded Preprocessor from {preprocessor_path}")
    except Exception as e:
        print(f"[ML Loader Error] Failed to load Preprocessor: {e}")

if os.path.exists(metadata_path):
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        print(f"[ML Loader] Loaded Metadata: {metadata}")
    except Exception as e:
        print(f"[ML Loader Error] Failed to load Metadata: {e}")

if os.path.exists(raw_features_path):
    try:
        with open(raw_features_path, 'r') as f:
            raw_features = json.load(f)
        print(f"[ML Loader] Loaded {len(raw_features)} raw feature names.")
    except Exception as e:
        print(f"[ML Loader Error] Failed to load Raw Features List: {e}")

def get_ml_artifacts():
    return rf_model, preprocessor, metadata, raw_features
