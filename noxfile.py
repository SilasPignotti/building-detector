import nox

nox.options.sessions = ["lint", "typecheck"]


@nox.session(reuse_venv=True)
def lint(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", "format", "--check", ".")
    session.run("ruff", "check", ".")


@nox.session(reuse_venv=True)
def typecheck(session: nox.Session) -> None:
    session.install("pyright")
    session.run("pyright")
