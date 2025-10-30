"""Geração de relatórios HTML para backtest."""

from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
from jinja2 import Template


class ReportGenerator:
    """Gerador de relatórios HTML para backtest."""
    
    def generate(self, results: dict[str, Any], output_path: str) -> None:
        """Gera relatório HTML.
        
        Args:
            results: Resultados do backtest.
            output_path: Caminho para salvar o relatório.
        """
        metrics = results["metrics"]
        trades = results["trades"]
        equity_curve = results["equity_curve"]
        
        # Criar gráficos
        equity_chart = self._create_equity_chart(equity_curve)
        drawdown_chart = self._create_drawdown_chart(equity_curve)
        
        # Criar tabela de trades
        trades_df = pd.DataFrame(trades)
        if len(trades_df) > 0:
            trades_df["timestamp"] = pd.to_datetime(trades_df["timestamp"])
            trades_table = trades_df.tail(20).to_html(index=False, classes="table table-striped")
        else:
            trades_table = "<p>Nenhum trade executado.</p>"
        
        # Template HTML
        html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Backtest - Binary Trading Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .metric-card.positive {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .metric-card.negative {
            background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        }
        .metric-label {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }
        .chart {
            margin: 30px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #007bff;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Backtest</h1>
        <p><strong>Data de geração:</strong> {{ timestamp }}</p>
        
        <h2>📈 Métricas de Performance</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Total de Trades</div>
                <div class="metric-value">{{ metrics.total_trades }}</div>
            </div>
            <div class="metric-card {{ 'positive' if metrics.win_rate >= 0.5 else 'negative' }}">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{{ "%.2f"|format(metrics.win_rate * 100) }}%</div>
            </div>
            <div class="metric-card {{ 'positive' if metrics.total_return >= 0 else 'negative' }}">
                <div class="metric-label">Retorno Total</div>
                <div class="metric-value">{{ "%.2f"|format(metrics.total_return * 100) }}%</div>
            </div>
            <div class="metric-card {{ 'positive' if metrics.expectancy >= 0 else 'negative' }}">
                <div class="metric-label">Expectância</div>
                <div class="metric-value">{{ "%.4f"|format(metrics.expectancy) }}</div>
            </div>
            <div class="metric-card negative">
                <div class="metric-label">Max Drawdown</div>
                <div class="metric-value">{{ "%.2f"|format(metrics.max_drawdown * 100) }}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Brier Score</div>
                <div class="metric-value">{{ "%.4f"|format(metrics.brier_score) }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Saldo Final</div>
                <div class="metric-value">${{ "%.2f"|format(metrics.final_balance) }}</div>
            </div>
        </div>
        
        <h2>📉 Curva de Equity</h2>
        <div class="chart">
            {{ equity_chart | safe }}
        </div>
        
        <h2>📉 Drawdown</h2>
        <div class="chart">
            {{ drawdown_chart | safe }}
        </div>
        
        <h2>📋 Últimos Trades</h2>
        {{ trades_table | safe }}
    </div>
</body>
</html>
        """
        
        # Renderizar template
        template = Template(html_template)
        html_content = template.render(
            timestamp=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            metrics=metrics,
            equity_chart=equity_chart,
            drawdown_chart=drawdown_chart,
            trades_table=trades_table,
        )
        
        # Salvar relatório
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Relatório salvo em: {output_path}")
    
    def _create_equity_chart(self, equity_curve: list[float]) -> str:
        """Cria gráfico de curva de equity."""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            y=equity_curve,
            mode="lines",
            name="Equity",
            line=dict(color="#007bff", width=2),
        ))
        
        fig.update_layout(
            title="Curva de Equity",
            xaxis_title="Trade #",
            yaxis_title="Saldo ($)",
            hovermode="x unified",
            template="plotly_white",
            height=400,
        )
        
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
    
    def _create_drawdown_chart(self, equity_curve: list[float]) -> str:
        """Cria gráfico de drawdown."""
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            y=drawdown,
            mode="lines",
            name="Drawdown",
            line=dict(color="#dc3545", width=2),
            fill="tozeroy",
        ))
        
        fig.update_layout(
            title="Drawdown",
            xaxis_title="Trade #",
            yaxis_title="Drawdown (%)",
            hovermode="x unified",
            template="plotly_white",
            height=400,
        )
        
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
