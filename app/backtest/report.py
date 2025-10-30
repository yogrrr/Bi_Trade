"""Gerador de relatórios HTML para backtest."""

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
        opportunities = results.get("opportunities", [])
        equity_curve = results["equity_curve"]
        
        # Criar gráficos
        equity_chart = self._create_equity_chart(equity_curve)
        drawdown_chart = self._create_drawdown_chart(equity_curve)
        prob_dist_chart = self._create_probability_distribution(opportunities)
        
        # Criar tabela de trades
        trades_df = pd.DataFrame(trades)
        if len(trades_df) > 0:
            trades_df["timestamp"] = pd.to_datetime(trades_df["timestamp"])
            trades_table = trades_df.tail(20).to_html(index=False, classes="table table-striped")
        else:
            trades_table = "<p>Nenhum trade executado.</p>"
        
        # Criar tabela de oportunidades
        opp_df = pd.DataFrame(opportunities)
        if len(opp_df) > 0:
            opp_df["timestamp"] = pd.to_datetime(opp_df["timestamp"])
            # Estatísticas de oportunidades
            total_opps = len(opp_df)
            executed = opp_df["should_trade"].sum()
            rejected = total_opps - executed
            avg_p_win = opp_df["p_win"].mean()
            
            # Motivos de rejeição
            rejection_reasons = opp_df[~opp_df["should_trade"]]["reason"].value_counts().to_dict()
            
            opportunities_table = opp_df.tail(50).to_html(index=False, classes="table table-striped table-sm")
        else:
            total_opps = 0
            executed = 0
            rejected = 0
            avg_p_win = 0
            rejection_reasons = {}
            opportunities_table = "<p>Nenhuma oportunidade analisada.</p>"
        
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
            max-width: 1400px;
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
        .metric-card.success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .metric-card.danger {
            background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        }
        .metric-card.warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .metric-label {
            font-size: 14px;
            opacity: 0.9;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            margin-top: 10px;
        }
        .chart-container {
            margin: 30px 0;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .table th, .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .table-striped tbody tr:nth-child(odd) {
            background-color: #f8f9fa;
        }
        .table-sm th, .table-sm td {
            padding: 8px;
            font-size: 13px;
        }
        .alert {
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
        }
        .rejection-reasons {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .rejection-reasons ul {
            margin: 10px 0;
            padding-left: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Backtest</h1>
        <p><strong>Gerado em:</strong> {{ timestamp }}</p>
        
        <h2>📈 Métricas de Performance</h2>
        <div class="metrics">
            <div class="metric-card success">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{{ "%.2f"|format(metrics.win_rate * 100) }}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total de Trades</div>
                <div class="metric-value">{{ metrics.total_trades }}</div>
            </div>
            <div class="metric-card {{ 'success' if metrics.total_return > 0 else 'danger' }}">
                <div class="metric-label">Retorno Total</div>
                <div class="metric-value">{{ "%.2f"|format(metrics.total_return * 100) }}%</div>
            </div>
            <div class="metric-card danger">
                <div class="metric-label">Max Drawdown</div>
                <div class="metric-value">{{ "%.2f"|format(metrics.max_drawdown * 100) }}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Expectância</div>
                <div class="metric-value">{{ "%.4f"|format(metrics.expectancy) }}</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">Saldo Final</div>
                <div class="metric-value">${{ "%.2f"|format(metrics.final_balance) }}</div>
            </div>
        </div>
        
        <h2>🎯 Análise de Oportunidades</h2>
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Total Analisadas</div>
                <div class="metric-value">{{ total_opps }}</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">Executadas</div>
                <div class="metric-value">{{ executed }}</div>
            </div>
            <div class="metric-card warning">
                <div class="metric-label">Rejeitadas</div>
                <div class="metric-value">{{ rejected }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">P(win) Médio</div>
                <div class="metric-value">{{ "%.2f"|format(avg_p_win * 100) }}%</div>
            </div>
        </div>
        
        {% if rejection_reasons %}
        <div class="rejection-reasons">
            <strong>🚫 Motivos de Rejeição:</strong>
            <ul>
            {% for reason, count in rejection_reasons.items() %}
                <li>{{ reason }}: <strong>{{ count }}</strong> vezes</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <div class="chart-container">
            {{ prob_dist_chart|safe }}
        </div>
        
        <div class="chart-container">
            {{ equity_chart|safe }}
        </div>
        
        <div class="chart-container">
            {{ drawdown_chart|safe }}
        </div>
        
        <h2>💼 Últimas 20 Trades Executados</h2>
        {{ trades_table|safe }}
        
        <h2>🔍 Últimas 50 Oportunidades Analisadas</h2>
        <div style="overflow-x: auto;">
            {{ opportunities_table|safe }}
        </div>
        
        <div class="alert">
            <strong>⚠️ Aviso:</strong> Este é um projeto educacional. Opções binárias são de alto risco. 
            Sempre teste em modo demo antes de qualquer operação real.
        </div>
    </div>
</body>
</html>
        """
        
        # Renderizar template
        template = Template(html_template)
        html_content = template.render(
            timestamp=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            metrics=metrics,
            total_opps=total_opps,
            executed=executed,
            rejected=rejected,
            avg_p_win=avg_p_win,
            rejection_reasons=rejection_reasons,
            equity_chart=equity_chart,
            drawdown_chart=drawdown_chart,
            prob_dist_chart=prob_dist_chart,
            trades_table=trades_table,
            opportunities_table=opportunities_table,
        )
        
        # Salvar relatório
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Relatório salvo em: {output_path}")
    
    def _create_probability_distribution(self, opportunities: list[dict[str, Any]]) -> str:
        """Cria gráfico de distribuição de probabilidades."""
        if not opportunities:
            return "<p>Sem dados para gráfico de distribuição.</p>"
        
        opp_df = pd.DataFrame(opportunities)
        
        # Separar executadas e rejeitadas
        executed = opp_df[opp_df["should_trade"]]
        rejected = opp_df[~opp_df["should_trade"]]
        
        fig = go.Figure()
        
        # Histograma de probabilidades rejeitadas
        if len(rejected) > 0:
            fig.add_trace(go.Histogram(
                x=rejected["p_win"],
                name="Rejeitadas",
                marker_color="rgba(255, 99, 132, 0.7)",
                nbinsx=30,
            ))
        
        # Histograma de probabilidades executadas
        if len(executed) > 0:
            fig.add_trace(go.Histogram(
                x=executed["p_win"],
                name="Executadas",
                marker_color="rgba(75, 192, 192, 0.7)",
                nbinsx=30,
            ))
        
        fig.update_layout(
            title="Distribuição de Probabilidades P(win)",
            xaxis_title="P(win)",
            yaxis_title="Frequência",
            barmode="overlay",
            height=400,
            template="plotly_white",
        )
        
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
    
    def _create_equity_chart(self, equity_curve: list[float]) -> str:
        """Cria gráfico de curva de equity."""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            y=equity_curve,
            mode="lines",
            name="Equity",
            line=dict(color="rgb(75, 192, 192)", width=2),
        ))
        
        fig.update_layout(
            title="Curva de Equity",
            xaxis_title="Trades",
            yaxis_title="Saldo ($)",
            height=400,
            template="plotly_white",
        )
        
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
    
    def _create_drawdown_chart(self, equity_curve: list[float]) -> str:
        """Cria gráfico de drawdown."""
        import numpy as np
        
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            y=drawdown * 100,
            mode="lines",
            name="Drawdown",
            fill="tozeroy",
            line=dict(color="rgb(255, 99, 132)", width=2),
        ))
        
        fig.update_layout(
            title="Drawdown",
            xaxis_title="Trades",
            yaxis_title="Drawdown (%)",
            height=400,
            template="plotly_white",
        )
        
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
