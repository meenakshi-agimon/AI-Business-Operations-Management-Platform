import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------
class MLModelError(Exception):
    """Base exception for ML service errors."""
    pass


class ModelFileNotFoundError(MLModelError, FileNotFoundError):
    """Raised when a specified model file does not exist on disk."""
    pass


class ModelLoadError(MLModelError):
    """Raised when a model file exists but fails to deserialize or load."""
    pass


# ---------------------------------------------------------------------------
# Path Resolution
# ---------------------------------------------------------------------------
def get_models_dir() -> Path:
    """
    Resolve the absolute path to the root-level models/ directory.
    Checks Django settings first if available, falling back to relative navigation
    from this file: <root>/backend/api/ml_services.py -> <root>/models.
    """
    try:
        from django.conf import settings
        if hasattr(settings, 'MODELS_DIR') and settings.MODELS_DIR:
            candidate = Path(settings.MODELS_DIR).resolve()
            if candidate.exists():
                return candidate
        if hasattr(settings, 'BASE_DIR') and settings.BASE_DIR:
            candidate = (Path(settings.BASE_DIR).parent / 'models').resolve()
            if candidate.exists():
                return candidate
    except Exception as exc:
        logger.debug("Could not resolve models directory from django.conf.settings: %s", exc)

    # Fallback based on file location: backend/api/ml_services.py -> ../../models
    fallback = (Path(__file__).resolve().parent.parent.parent / 'models').resolve()
    return fallback


# ---------------------------------------------------------------------------
# ML Model Service (Thread-safe, Singleton with In-Memory Caching)
# ---------------------------------------------------------------------------
class MLModelService:
    """
    Service responsible for loading and caching machine learning models in memory.
    Each model file is loaded on demand only once and cached for subsequent calls.
    """

    MODEL_FILENAMES = {
        'risk_model': 'risk_prediction_xgboost.pkl',
        'delay_model': 'project_delay_random_forest.pkl',
        'delay_features': 'project_delay_features.pkl',
    }

    _instance: Optional['MLModelService'] = None
    _singleton_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, models_dir: Optional[Path] = None):
        if getattr(self, '_initialized', False):
            return
        self._models_dir: Path = models_dir or get_models_dir()
        self._cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("Initialized MLModelService with models_dir: %s", self._models_dir)

    @property
    def models_dir(self) -> Path:
        return self._models_dir

    def _load_model_file(self, model_key: str, filename: str) -> Any:
        """
        Thread-safe loader with caching and detailed error handling.
        """
        # Return cached instance if available
        if model_key in self._cache:
            return self._cache[model_key]

        with self._lock:
            # Double-check cache inside lock
            if model_key in self._cache:
                return self._cache[model_key]

            file_path = self._models_dir / filename

            if not file_path.exists() or not file_path.is_file():
                error_msg = (
                    f"Model file '{filename}' was not found at expected path: '{file_path}'. "
                    f"Please ensure the file exists in the root-level 'models/' directory."
                )
                logger.error(error_msg)
                raise ModelFileNotFoundError(error_msg)

            logger.info("Loading model '%s' from %s using joblib...", model_key, file_path)
            try:
                loaded_object = joblib.load(file_path)
            except ModuleNotFoundError as e:
                error_msg = (
                    f"Failed to load '{filename}' from '{file_path}': missing required dependency module '{e.name}'. "
                    f"Please ensure packages such as 'scikit-learn', 'xgboost', 'numpy', and 'pandas' are installed."
                )
                logger.error(error_msg)
                raise ModelLoadError(error_msg) from e
            except Exception as e:
                error_msg = (
                    f"Failed to load model file '{filename}' from '{file_path}'. "
                    f"Error details [{type(e).__name__}]: {e}"
                )
                logger.error(error_msg, exc_info=True)
                raise ModelLoadError(error_msg) from e

            self._cache[model_key] = loaded_object
            logger.info("Successfully loaded and cached '%s' in memory.", model_key)
            return loaded_object

    def get_risk_model(self) -> Any:
        """
        Load and return the cached Risk Prediction model (XGBoost).
        File: models/risk_prediction_xgboost.pkl
        """
        return self._load_model_file('risk_model', self.MODEL_FILENAMES['risk_model'])

    def get_delay_model(self) -> Any:
        """
        Load and return the cached Project Delay model (Random Forest).
        File: models/project_delay_random_forest.pkl
        """
        return self._load_model_file('delay_model', self.MODEL_FILENAMES['delay_model'])

    def get_delay_feature_list(self) -> List[str]:
        """
        Load and return the cached Project Delay feature list.
        File: models/project_delay_features.pkl
        """
        return self._load_model_file('delay_features', self.MODEL_FILENAMES['delay_features'])

    def load_all_models(self) -> Dict[str, Any]:
        """
        Eagerly load and cache models in memory.
        Returns a dictionary mapping model keys to loaded objects.
        """
        return {
            'risk_model': self.get_risk_model(),
            'delay_model': self.get_delay_model(),
            'delay_features': self.get_delay_feature_list(),
        }

    def clear_cache(self) -> None:
        """
        Clear in-memory cached models. Useful for unit testing or reloading.
        """
        with self._lock:
            self._cache.clear()
            logger.info("Cleared in-memory ML model cache.")

    def is_cached(self, model_key: str) -> bool:
        """Check if a given model is currently cached in memory."""
        return model_key in self._cache


# ---------------------------------------------------------------------------
# Module-level Convenience Functions & Singleton Instance
# ---------------------------------------------------------------------------
ml_service = MLModelService()


def get_risk_model() -> Any:
    """Retrieve the cached risk prediction XGBoost model."""
    return ml_service.get_risk_model()


def get_delay_model() -> Any:
    """Retrieve the cached project delay Random Forest model."""
    return ml_service.get_delay_model()


def get_delay_feature_list() -> List[str]:
    """Retrieve the cached project delay feature list."""
    return ml_service.get_delay_feature_list()


def get_delay_features() -> List[str]:
    """Alias for get_delay_feature_list()."""
    return ml_service.get_delay_feature_list()


def load_all_models() -> Dict[str, Any]:
    """Eagerly load and return all ML models."""
    return ml_service.load_all_models()
