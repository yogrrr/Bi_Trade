"""Modelos de aprendizado online."""

from typing import Any, Optional

import numpy as np
# River removido para compatibilidade com Render
try:
    from river import linear_model, preprocessing
    RIVER_AVAILABLE = True
except ImportError:
    RIVER_AVAILABLE = False
    
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import SGDClassifier


class OnlineModel:
    """Classe base para modelos de aprendizado online."""
    
    def predict_proba(self, X: np.ndarray) -> float:
        """Prediz a probabilidade de vitória.
        
        Args:
            X: Vetor de features.
        
        Returns:
            Probabilidade de vitória (0-1).
        """
        raise NotImplementedError
    
    def update(self, X: np.ndarray, y: int) -> None:
        """Atualiza o modelo com um novo exemplo.
        
        Args:
            X: Vetor de features.
            y: Label (1 para vitória, 0 para derrota).
        """
        raise NotImplementedError


class RiverModel(OnlineModel):
    """Modelo de aprendizado online usando River."""
    
    def __init__(self, calibration: Optional[str] = None) -> None:
        """Inicializa o modelo River.
        
        Args:
            calibration: Tipo de calibração ('isotonic', 'platt' ou None).
        """
        self.scaler = preprocessing.StandardScaler()
        self.model = linear_model.LogisticRegression()
        self.calibration = calibration
        self.n_samples = 0
    
    def predict_proba(self, X: np.ndarray) -> float:
        """Prediz a probabilidade de vitória.
        
        Args:
            X: Vetor de features.
        
        Returns:
            Probabilidade de vitória (0-1).
        """
        # Converter para dict (formato do River)
        x_dict = {f"f{i}": float(v) for i, v in enumerate(X)}
        
        # Escalar
        x_scaled = self.scaler.transform_one(x_dict)
        
        # Predizer
        proba = self.model.predict_proba_one(x_scaled)
        
        # Retornar probabilidade da classe positiva (1)
        return proba.get(1, 0.5)
    
    def update(self, X: np.ndarray, y: int) -> None:
        """Atualiza o modelo com um novo exemplo.
        
        Args:
            X: Vetor de features.
            y: Label (1 para vitória, 0 para derrota).
        """
        # Converter para dict
        x_dict = {f"f{i}": float(v) for i, v in enumerate(X)}
        
        # Escalar (learn_one retorna None, então precisamos chamar separadamente)
        self.scaler.learn_one(x_dict)
        x_scaled = self.scaler.transform_one(x_dict)
        
        # Atualizar modelo
        self.model.learn_one(x_scaled, y)
        self.n_samples += 1


class SklearnModel(OnlineModel):
    """Modelo de aprendizado online usando scikit-learn."""
    
    def __init__(self, calibration: Optional[str] = None) -> None:
        """Inicializa o modelo scikit-learn.
        
        Args:
            calibration: Tipo de calibração ('isotonic', 'platt' ou None).
        """
        self.model = SGDClassifier(
            loss="log_loss",
            penalty="l2",
            alpha=0.0001,
            max_iter=1,
            warm_start=True,
            random_state=42,
        )
        self.calibration = calibration
        self.calibrator: Optional[CalibratedClassifierCV] = None
        self.n_samples = 0
        self.is_fitted = False
    
    def predict_proba(self, X: np.ndarray) -> float:
        """Prediz a probabilidade de vitória.
        
        Args:
            X: Vetor de features.
        
        Returns:
            Probabilidade de vitória (0-1).
        """
        if not self.is_fitted:
            return 0.5
        
        X_reshaped = X.reshape(1, -1)
        
        # Usar calibrador se disponível
        if self.calibrator is not None:
            proba = self.calibrator.predict_proba(X_reshaped)[0, 1]
        else:
            proba = self.model.predict_proba(X_reshaped)[0, 1]
        
        return float(proba)
    
    def update(self, X: np.ndarray, y: int) -> None:
        """Atualiza o modelo com um novo exemplo.
        
        Args:
            X: Vetor de features.
            y: Label (1 para vitória, 0 para derrota).
        """
        X_reshaped = X.reshape(1, -1)
        y_reshaped = np.array([y])
        
        # Primeira atualização
        if not self.is_fitted:
            self.model.partial_fit(X_reshaped, y_reshaped, classes=[0, 1])
            self.is_fitted = True
        else:
            self.model.partial_fit(X_reshaped, y_reshaped)
        
        self.n_samples += 1


def create_model(model_type: str = "sklearn", calibration: Optional[str] = None) -> OnlineModel:
    """Cria um modelo de aprendizado online.
    
    Args:
        model_type: Tipo de modelo ('river' ou 'sklearn').
        calibration: Tipo de calibração ('isotonic', 'platt' ou None).
    
    Returns:
        Instância do modelo.
    """
    if model_type == "river":
        if not RIVER_AVAILABLE:
            print("⚠️  River não disponível, usando sklearn")
            return SklearnModel(calibration=calibration)
        return RiverModel(calibration=calibration)
    elif model_type == "sklearn":
        return SklearnModel(calibration=calibration)
    else:
        raise ValueError(f"Tipo de modelo inválido: {model_type}")
