"""Ponto de entrada principal com CLI."""

import click

from app.backtest.engine import BacktestEngine
from app.backtest.report import ReportGenerator
from app.config import Config
from app.data.loaders import SyntheticDataLoader
from app.features.ta_features import TechnicalFeatures
from app.live.runner import create_live_runner
from app.utils.logging import setup_logging


@click.group()
def cli() -> None:
    """Binary Trading Bot - Robô de trading de opções binárias com IA."""
    pass


@cli.command()
@click.option("--symbol", default=None, help="Símbolo do ativo (ex: EURUSD)")
@click.option("--timeframe", default=None, help="Timeframe (ex: 1m, 5m)")
@click.option("--expiry", default=None, type=int, help="Expiração em segundos")
@click.option("--report", default="out/report.html", help="Caminho para o relatório")
@click.option("--config", default="config.yaml", help="Caminho para config.yaml")
def backtest(
    symbol: str | None,
    timeframe: str | None,
    expiry: int | None,
    report: str,
    config: str,
) -> None:
    """Executa backtest das estratégias."""
    # Carregar configuração
    cfg = Config(config)
    setup_logging(cfg._config)
    
    # Sobrescrever com parâmetros CLI
    if symbol:
        cfg._config["symbol"] = symbol
    if timeframe:
        cfg._config["timeframe"] = timeframe
    if expiry:
        cfg._config["expiry"] = expiry
    
    click.echo("🚀 Iniciando backtest...")
    click.echo(f"   Símbolo: {cfg.symbol}")
    click.echo(f"   Timeframe: {cfg.timeframe}")
    click.echo(f"   Expiração: {cfg.expiry}s")
    
    # Carregar dados
    loader = SyntheticDataLoader()
    start_date = cfg.get("backtest.start_date", "2024-01-01")
    end_date = cfg.get("backtest.end_date", "2024-12-31")
    
    click.echo(f"\n📊 Carregando dados ({start_date} a {end_date})...")
    df = loader.load(cfg.symbol, cfg.timeframe, start_date, end_date)
    
    # Adicionar features
    click.echo("🔧 Calculando indicadores técnicos...")
    df = TechnicalFeatures.add_all_features(df, cfg._config)
    
    # Executar backtest
    click.echo(f"⚡ Executando backtest com {len(df)} barras...\n")
    engine = BacktestEngine(cfg._config)
    results = engine.run(df)
    
    # Exibir métricas
    metrics = results["metrics"]
    click.echo("\n📈 Resultados:")
    click.echo(f"   Total de trades: {metrics['total_trades']}")
    click.echo(f"   Win rate: {metrics['win_rate']:.2%}")
    click.echo(f"   Retorno total: {metrics['total_return']:.2%}")
    click.echo(f"   Expectância: {metrics['expectancy']:.4f}")
    click.echo(f"   Max drawdown: {metrics['max_drawdown']:.2%}")
    click.echo(f"   Brier score: {metrics['brier_score']:.4f}")
    click.echo(f"   Saldo final: ${metrics['final_balance']:.2f}")
    
    # Gerar relatório
    click.echo(f"\n📄 Gerando relatório em {report}...")
    report_gen = ReportGenerator()
    report_gen.generate(results, report)
    
    click.echo("\n✅ Backtest concluído com sucesso!")


@cli.command()
@click.option("--symbol", default=None, help="Símbolo do ativo (ex: EURUSD)")
@click.option("--timeframe", default=None, help="Timeframe (ex: 1m, 5m)")
@click.option("--expiry", default=None, type=int, help="Expiração em segundos")
@click.option("--demo", is_flag=True, help="Executar em modo demo (paper trading)")
@click.option("--broker", default=None, help="Nome do broker (para modo real)")
@click.option("--config", default="config.yaml", help="Caminho para config.yaml")
def live(
    symbol: str | None,
    timeframe: str | None,
    expiry: int | None,
    demo: bool,
    broker: str | None,
    config: str,
) -> None:
    """Executa trading em modo live/demo."""
    # Carregar configuração
    cfg = Config(config)
    setup_logging(cfg._config)
    
    # Sobrescrever com parâmetros CLI
    if symbol:
        cfg._config["symbol"] = symbol
    if timeframe:
        cfg._config["timeframe"] = timeframe
    if expiry:
        cfg._config["expiry"] = expiry
    
    mode = "DEMO" if demo else "LIVE"
    click.echo(f"🚀 Iniciando execução {mode}...")
    click.echo(f"   Símbolo: {cfg.symbol}")
    click.echo(f"   Timeframe: {cfg.timeframe}")
    click.echo(f"   Expiração: {cfg.expiry}s")
    
    if not demo and broker is None:
        click.echo("\n⚠️  AVISO: Modo LIVE requer --broker. Use --demo para paper trading.")
        return
    
    if not demo:
        click.echo("\n⚠️  ATENÇÃO: Você está prestes a operar com dinheiro real!")
        click.echo("   Certifique-se de ter testado em modo demo primeiro.")
        if not click.confirm("   Deseja continuar?"):
            click.echo("Operação cancelada.")
            return
    
    # Criar e iniciar runner
    click.echo(f"\n⚡ Iniciando runner {mode}...\n")
    runner = create_live_runner(cfg._config, demo=demo)
    
    try:
        runner.start()
    except KeyboardInterrupt:
        click.echo("\n\n⏸️  Execução interrompida pelo usuário")
    finally:
        click.echo("\n✅ Execução finalizada")


@cli.command()
def version() -> None:
    """Exibe a versão do bot."""
    from app import __version__
    click.echo(f"Binary Trading Bot v{__version__}")


if __name__ == "__main__":
    cli()
