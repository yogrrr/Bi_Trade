"""Setup file to force pip installation on Render."""

from setuptools import setup, find_packages

setup(
    name="binary-trading-bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26.0",
        "pandas>=2.1.0",
        "scikit-learn>=1.3.0",
        # River removido para compatibilidade com Render
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "jinja2>=3.1.0",
        "plotly>=5.17.0",
        "requests>=2.31.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "websockets>=12.0",
        "yfinance>=0.2.0",
    ],
    python_requires=">=3.11,<3.13",
)
