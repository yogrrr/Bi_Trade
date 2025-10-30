from __future__ import annotations

from types import SimpleNamespace

from app.utils.git_sync import ensure_repo_is_up_to_date


def test_ensure_repo_skips_when_not_a_git_repo(tmp_path):
    calls = []

    def fake_run(*args, **kwargs):  # pragma: no cover - should not be called
        calls.append((args, kwargs))
        return SimpleNamespace(stdout="", returncode=0)

    ensure_repo_is_up_to_date(repo_dir=tmp_path, run_cmd=fake_run)

    assert calls == []


def test_ensure_repo_skips_when_dirty(tmp_path):
    (tmp_path / ".git").mkdir()
    calls = []

    responses = [SimpleNamespace(stdout=" M app/main.py", returncode=0)]

    def fake_run(args, **kwargs):
        calls.append(args)
        return responses[len(calls) - 1]

    ensure_repo_is_up_to_date(repo_dir=tmp_path, run_cmd=fake_run)

    assert calls == [["git", "status", "--porcelain"]]


def test_ensure_repo_fetches_and_reports_up_to_date(tmp_path):
    (tmp_path / ".git").mkdir()
    calls = []
    responses = [
        SimpleNamespace(stdout="", returncode=0),
        SimpleNamespace(stdout="", returncode=0),
        SimpleNamespace(stdout="0\t0", returncode=0),
    ]

    def fake_run(args, **kwargs):
        calls.append(args)
        return responses[len(calls) - 1]

    messages = []
    ensure_repo_is_up_to_date(
        repo_dir=tmp_path,
        run_cmd=fake_run,
        echo=messages.append,
    )

    assert calls == [
        ["git", "status", "--porcelain"],
        ["git", "fetch", "origin", "main"],
        ["git", "rev-list", "--left-right", "--count", "HEAD...origin/main"],
    ]
    assert messages[-1] == "✅ Repositório já está atualizado com a versão do GitHub."


def test_ensure_repo_pulls_when_behind(tmp_path):
    (tmp_path / ".git").mkdir()
    calls = []
    responses = [
        SimpleNamespace(stdout="", returncode=0),
        SimpleNamespace(stdout="", returncode=0),
        SimpleNamespace(stdout="0\t3", returncode=0),
        SimpleNamespace(stdout="", returncode=0),
    ]

    def fake_run(args, **kwargs):
        calls.append(args)
        return responses[len(calls) - 1]

    messages = []
    ensure_repo_is_up_to_date(
        repo_dir=tmp_path,
        run_cmd=fake_run,
        echo=messages.append,
    )

    assert calls == [
        ["git", "status", "--porcelain"],
        ["git", "fetch", "origin", "main"],
        ["git", "rev-list", "--left-right", "--count", "HEAD...origin/main"],
        ["git", "pull", "--ff-only", "origin", "main"],
    ]
    assert messages[-1] == "✅ Repositório atualizado automaticamente com a versão do GitHub."

