"""API FastAPI para interface web do Binary Trading Bot."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.backtest.engine import BacktestEngine
from app.backtest.report import ReportGenerator
from app.config import Config, synchronize_risk_aliases
from app.data.loaders import SyntheticDataLoader
from app.features.ta_features import TechnicalFeatures
from app.live.runner import create_live_runner

# Criar aplicação FastAPI
app = FastAPI(
    title="Binary Trading Bot API",
    description="API para controle do robô de trading de opções binárias",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global
live_runner = None
live_task = None


class BacktestRequest(BaseModel):
    """Requisição de backtest."""
    symbol: str = "EURUSD"
    timeframe: str = "1m"
    expiry: int = 120
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"


class LiveRequest(BaseModel):
    """Requisição de execução live."""
    symbol: str = "EURUSD"
    timeframe: str = "1m"
    expiry: int = 120
    demo: bool = True


class ConfigUpdate(BaseModel):
    """Atualização de configuração."""
    config: dict[str, Any]


@app.get("/")
async def root() -> dict[str, str]:
    """Endpoint raiz."""
    return {"message": "Binary Trading Bot API", "version": "1.0.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check."""
    return {"status": "ok"}


@app.get("/config")
async def get_config() -> dict[str, Any]:
    """Obtém a configuração atual."""
    try:
        config = Config()
        return config._config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/config")
async def update_config(update: ConfigUpdate) -> dict[str, str]:
    """Atualiza a configuração."""
    try:
        import yaml

        config_path = Path("config.yaml")
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
                current_config: dict[str, Any] = yaml.safe_load(f) or {}
        else:
            current_config = {}

        def deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
            for key, value in overrides.items():
                if isinstance(value, dict) and isinstance(base.get(key), dict):
                    base[key] = deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        merged_config = deep_merge(dict(current_config), update.config)

        # Manter aliases stake_percent/risk_per_trade sincronizados
        risk_override = update.config.get("risk") if isinstance(update.config, dict) else None
        prefer: str | None = None
        if isinstance(risk_override, dict):
            if "stake_percent" in risk_override:
                prefer = "stake_percent"
            elif "risk_per_trade" in risk_override:
                prefer = "risk_per_trade"

        synchronize_risk_aliases(merged_config, prefer=prefer)

        with config_path.open("w", encoding="utf-8") as f:
            yaml.dump(merged_config, f, default_flow_style=False, allow_unicode=True)

        return {"message": "Configuração atualizada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/backtest")
async def run_backtest(request: BacktestRequest) -> dict[str, Any]:
    """Executa um backtest."""
    try:
        # Carregar configuração
        config = Config()
        
        # Sobrescrever com parâmetros da requisição
        config._config["symbol"] = request.symbol
        config._config["timeframe"] = request.timeframe
        config._config["expiry"] = request.expiry
        config._config["backtest"]["start_date"] = request.start_date
        config._config["backtest"]["end_date"] = request.end_date
        
        # Carregar dados
        loader = SyntheticDataLoader()
        df = loader.load(
            request.symbol,
            request.timeframe,
            request.start_date,
            request.end_date,
        )
        
        # Adicionar features
        df = TechnicalFeatures.add_all_features(df, config._config)
        
        # Executar backtest
        engine = BacktestEngine(config._config)
        results = engine.run(df)
        
        # Gerar relatório
        report_path = f"out/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_gen = ReportGenerator()
        report_gen.generate(results, report_path)
        
        # Retornar resultados
        return {
            "status": "success",
            "metrics": results["metrics"],
            "report_path": report_path,
            "total_trades": len(results["trades"]),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/live/start")
async def start_live(request: LiveRequest) -> dict[str, str]:
    """Inicia execução live/demo."""
    global live_runner, live_task
    
    try:
        if live_runner is not None:
            return {"message": "Bot já está em execução"}
        
        # Carregar configuração
        config = Config()
        
        # Sobrescrever com parâmetros da requisição
        config._config["symbol"] = request.symbol
        config._config["timeframe"] = request.timeframe
        config._config["expiry"] = request.expiry
        
        # Criar runner
        live_runner = create_live_runner(config._config, demo=request.demo)
        
        # Iniciar em background
        live_task = asyncio.create_task(asyncio.to_thread(live_runner.start))
        
        mode = "demo" if request.demo else "live"
        return {"message": f"Bot iniciado em modo {mode}"}
    
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERRO /live/start: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@app.post("/live/stop")
async def stop_live() -> dict[str, str]:
    """Para execução live/demo."""
    global live_runner, live_task
    
    try:
        if live_runner is None:
            return {"message": "Bot não está em execução"}
        
        # Parar runner
        live_runner.stop()
        
        # Aguardar task finalizar
        if live_task:
            await live_task
        
        live_runner = None
        live_task = None
        
        return {"message": "Bot parado com sucesso"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/live/status")
async def live_status() -> dict[str, Any]:
    """Obtém status da execução live."""
    global live_runner
    
    if live_runner is None:
        return {
            "running": False,
            "balance": 0.0,
            "active_trades": 0,
            "daily_pnl": 0.0,
            "daily_trades": 0,
        }
    
    try:
        balance = live_runner.broker.get_balance()
        stats = live_runner.risk_manager.get_daily_stats()
        
        return {
            "running": live_runner.is_running,
            "balance": balance,
            "active_trades": len(live_runner.active_trades),
            "daily_pnl": stats["daily_pnl"],
            "daily_trades": stats["daily_trades"],
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports")
async def list_reports() -> dict[str, list[str]]:
    """Lista relatórios disponíveis."""
    try:
        out_dir = Path("out")
        if not out_dir.exists():
            return {"reports": []}
        
        reports = [f.name for f in out_dir.glob("*.html")]
        reports.sort(reverse=True)
        
        return {"reports": reports}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/{filename}")
async def get_report(filename: str) -> FileResponse:
    """Obtém um relatório específico."""
    try:
        report_path = Path("out") / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Relatório não encontrado")
        
        return FileResponse(report_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket) -> None:
    """WebSocket para atualizações em tempo real."""
    await websocket.accept()
    
    try:
        while True:
            # Enviar status a cada 2 segundos
            if live_runner is not None:
                balance = live_runner.broker.get_balance()
                stats = live_runner.risk_manager.get_daily_stats()
                
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "running": live_runner.is_running,
                    "balance": balance,
                    "active_trades": len(live_runner.active_trades),
                    "daily_pnl": stats["daily_pnl"],
                    "daily_trades": stats["daily_trades"],
                }
                
                await websocket.send_json(data)
            
            await asyncio.sleep(2)
    
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
