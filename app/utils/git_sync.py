"""Utilities for keeping the local repository synchronized with GitHub."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Iterable


def _default_runner(*args, **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(*args, **kwargs)


def ensure_repo_is_up_to_date(
    branch: str = "main",
    repo_dir: Path | None = None,
    echo: Callable[[str], None] | None = None,
    run_cmd: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> None:
    """Fetch and fast-forward the local git repository when possible.

    The update is skipped when git is unavailable, the repository has local
    modifications, or the project is not a git checkout.
    """

    project_root = repo_dir or Path(__file__).resolve().parents[2]
    git_dir = Path(project_root) / ".git"
    messenger = echo or (lambda message: None)
    runner = run_cmd or _default_runner

    if not git_dir.exists():
        return

    def call_git(args: Iterable[str], capture_output: bool = True):
        kwargs = {
            "cwd": project_root,
            "check": True,
        }
        if capture_output:
            kwargs.update({"capture_output": True, "text": True})
        return runner(list(args), **kwargs)

    try:
        status = call_git(["git", "status", "--porcelain"])
    except (FileNotFoundError, subprocess.CalledProcessError):
        messenger("⚠️  Não foi possível verificar atualizações automáticas do Git.")
        return

    if status.stdout.strip():
        messenger(
            "⚠️  Atualização automática ignorada: há modificações locais pendentes."
        )
        return

    try:
        call_git(["git", "fetch", "origin", branch], capture_output=False)
        ahead_behind = call_git(
            ["git", "rev-list", "--left-right", "--count", f"HEAD...origin/{branch}"]
        )
    except subprocess.CalledProcessError:
        messenger("⚠️  Não foi possível sincronizar com o repositório remoto.")
        return

    parts = ahead_behind.stdout.strip().split()
    if len(parts) != 2:
        messenger("⚠️  Erro ao interpretar o estado do repositório remoto.")
        return

    ahead, behind = (int(part) for part in parts)
    if behind == 0:
        messenger("✅ Repositório já está atualizado com a versão do GitHub.")
        return

    try:
        call_git(["git", "pull", "--ff-only", "origin", branch], capture_output=False)
    except subprocess.CalledProcessError:
        messenger("⚠️  Não foi possível aplicar atualização automática (git pull falhou).")
        return

    messenger("✅ Repositório atualizado automaticamente com a versão do GitHub.")

