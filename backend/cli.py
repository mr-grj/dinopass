import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, NoReturn

import httpx
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="dinopass",
    help="Manage your self-hosted dinopass vault from the terminal.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
pw_app = typer.Typer(
    help="Manage passwords.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
app.add_typer(pw_app, name="password")

_out = Console()
_err = Console(stderr=True)


def _api_url() -> str:
    return os.environ.get("DINOPASS_API_URL", "http://localhost:8000/api").rstrip("/")


def _die(msg: str) -> NoReturn:
    _err.print(f"[red]✗[/red]  {msg}")
    raise typer.Exit(1)


def _ok(msg: str) -> None:
    _out.print(f"[green]✓[/green]  {msg}")


def _check(resp: httpx.Response) -> None:
    if not resp.is_success:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        _die(str(detail))


def _unlock(client: httpx.Client) -> tuple[str, str]:
    master = typer.prompt("Master password", hide_input=True)
    try:
        resp = client.post("/master_password/check", json={"master_password": master})
    except httpx.ConnectError:
        _die(f"Cannot reach the API at {_api_url()!r}. Is the service running?")

    _check(resp)
    data = resp.json()
    if not data.get("valid"):
        _die("Invalid master password.")

    key: str = data["key_derivation"]
    return master, key


def _hdr(key: str) -> dict[str, str]:
    return {"x-dino-key-derivation": key}


@pw_app.command("list")
def pw_list() -> None:
    with httpx.Client(base_url=_api_url(), timeout=30) as client:
        _, key = _unlock(client)
        resp = client.get("/passwords", headers=_hdr(key))

    _check(resp)

    items: list[dict] = resp.json()
    if not items:
        _out.print("[dim]The vault is empty.[/dim]")
        return

    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2, 0, 0))
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="dim")
    table.add_column("Backed up", justify="center")

    for item in items:
        table.add_row(
            item["password_name"],
            item.get("description") or "-",
            "[green]✓[/green]" if item["backed_up"] else "[dim]–[/dim]",
        )

    _out.print(table)


@pw_app.command("get")
def pw_get(name: Annotated[str, typer.Argument(help="Password name.")]) -> None:
    with httpx.Client(base_url=_api_url(), timeout=30) as client:
        _, key = _unlock(client)
        resp = client.get(f"/passwords/{name}", headers=_hdr(key))

    _check(resp)

    item = resp.json()

    _out.print(f"\n  [bold cyan]{item['password_name']}[/bold cyan]")
    _out.print(f"  [dim]Value[/dim]        {item['password_value']}")

    if item.get("description"):
        _out.print(f"  [dim]Description[/dim]  {item['description']}")

    _out.print()


@pw_app.command("create")
def pw_create(name: Annotated[str, typer.Argument(help="Password name.")]) -> None:
    with httpx.Client(base_url=_api_url(), timeout=30) as client:
        _, key = _unlock(client)
        headers = _hdr(key)

        if client.get(f"/passwords/{name}", headers=headers).is_success:
            _die(f"A password named '{name}' already exists.")

        value = typer.prompt(
            "Password value", hide_input=True, confirmation_prompt=True
        )
        description = (
            typer.prompt("Description", default="", show_default=False) or None
        )
        resp = client.post(
            "/passwords/create",
            json={
                "password_name": name,
                "password_value": value,
                "description": description,
            },
            headers=headers,
        )

    _check(resp)

    _ok(f"Created [cyan]{name}[/cyan]")


@pw_app.command("update")
def pw_update(name: Annotated[str, typer.Argument(help="Password name.")]) -> None:
    with httpx.Client(base_url=_api_url(), timeout=30) as client:
        _, key = _unlock(client)
        headers = _hdr(key)

        current_resp = client.get(f"/passwords/{name}", headers=headers)

        _check(current_resp)

        current = current_resp.json()
        if current.get("description"):
            _out.print(f"  [dim]Current description:[/dim] {current['description']}")

        new_value = typer.prompt(
            "New password value", hide_input=True, confirmation_prompt=True
        )
        new_description = (
            typer.prompt(
                "New description",
                default=current.get("description") or "",
                show_default=bool(current.get("description")),
            )
            or None
        )

        resp = client.patch(
            "/passwords/update",
            json={
                "password": {
                    "password_name": name,
                    "password_value": current["password_value"],
                    "description": current.get("description"),
                },
                "new_password": {
                    "password_name": name,
                    "password_value": new_value,
                    "description": new_description,
                },
            },
            headers=headers,
        )

    _check(resp)

    _ok(f"Updated [cyan]{name}[/cyan]")


@pw_app.command("delete")
def pw_delete(
    name: Annotated[str, typer.Argument(help="Password name.")],
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip confirmation.")
    ] = False,
) -> None:
    with httpx.Client(base_url=_api_url(), timeout=30) as client:
        _, key = _unlock(client)
        headers = _hdr(key)

        exists = client.get(f"/passwords/{name}", headers=headers)
        if not exists.is_success:
            _check(exists)

        if not yes:
            typer.confirm(f"Delete '{name}'?", abort=True)

        resp = client.delete(f"/passwords/{name}", headers=headers)

    _check(resp)

    _ok(f"Deleted [cyan]{name}[/cyan]")


@app.command("backup")
def cmd_backup(
    out_dir: Annotated[
        Path, typer.Option("--out", "-o", help="Directory to save the backup file.")
    ] = Path("."),
) -> None:
    with httpx.Client(base_url=_api_url(), timeout=60) as client:
        master, key = _unlock(client)
        resp = client.post(
            "/passwords/backup",
            json={"master_password": master},
            headers=_hdr(key),
        )

    _check(resp)

    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"dinopass_backup_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.zip"
    dest = out_dir / filename
    dest.write_bytes(resp.content)

    _ok(f"Backup saved to [cyan]{dest}[/cyan]")


@app.command("import")
def cmd_import(
    file: Annotated[Path, typer.Argument(help="Path to the dinopass backup ZIP.")],
    on_conflict: Annotated[
        str,
        typer.Option(
            help="How to handle existing entries: skip or overwrite.",
        ),
    ] = "skip",
) -> None:
    if not file.exists():
        _die(f"File not found: {file}")

    if on_conflict not in ("skip", "overwrite"):
        _die("--on-conflict must be 'skip' or 'overwrite'.")

    file_bytes = file.read_bytes()

    with httpx.Client(base_url=_api_url(), timeout=60) as client:
        master, key = _unlock(client)
        resp = client.post(
            "/passwords/import",
            data={"master_password": master, "on_conflict": on_conflict},
            files={"file": (file.name, file_bytes, "application/zip")},
            headers=_hdr(key),
        )

    _check(resp)

    r = resp.json()

    _ok(
        f"Import complete - "
        f"[cyan]{r['imported']}[/cyan] added, "
        f"[cyan]{r['overwritten']}[/cyan] overwritten, "
        f"[cyan]{r['skipped']}[/cyan] skipped"
    )


if __name__ == "__main__":
    app()
