"""Testes para modelos de IA."""

import numpy as np
import pytest

from app.models.online import RiverModel, SklearnModel, create_model


def test_create_model_river():
    """Testa criação de modelo River."""
    model = create_model("river")
    assert isinstance(model, RiverModel)


def test_create_model_sklearn():
    """Testa criação de modelo sklearn."""
    model = create_model("sklearn")
    assert isinstance(model, SklearnModel)


def test_create_model_invalid():
    """Testa criação de modelo inválido."""
    with pytest.raises(ValueError):
        create_model("invalid")


def test_river_model_predict_proba():
    """Testa predição de probabilidade com River."""
    model = RiverModel()
    X = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    # Primeira predição (sem treino)
    p_win = model.predict_proba(X)
    assert 0.0 <= p_win <= 1.0


def test_river_model_update():
    """Testa atualização do modelo River."""
    model = RiverModel()
    X = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    # Treinar com alguns exemplos
    for _ in range(10):
        model.update(X, 1)
    
    assert model.n_samples == 10


def test_sklearn_model_predict_proba():
    """Testa predição de probabilidade com sklearn."""
    model = SklearnModel()
    X = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    # Primeira predição (sem treino)
    p_win = model.predict_proba(X)
    assert p_win == 0.5  # Valor padrão sem treino


def test_sklearn_model_update():
    """Testa atualização do modelo sklearn."""
    model = SklearnModel()
    X = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    # Treinar com alguns exemplos
    for _ in range(10):
        model.update(X, 1)
    
    assert model.is_fitted
    assert model.n_samples == 10


def test_model_learning():
    """Testa aprendizado do modelo."""
    model = create_model("sklearn")
    
    # Features que indicam vitória
    X_win = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    # Features que indicam derrota
    X_loss = np.array([-1.0, -1.0, -1.0, -1.0, -1.0])
    
    # Treinar com padrão
    for _ in range(50):
        model.update(X_win, 1)
        model.update(X_loss, 0)
    
    # Verificar aprendizado
    p_win_high = model.predict_proba(X_win)
    p_win_low = model.predict_proba(X_loss)
    
    # Modelo deve ter aprendido o padrão
    assert p_win_high > p_win_low
