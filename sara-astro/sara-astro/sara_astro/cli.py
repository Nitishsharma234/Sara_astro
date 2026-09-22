"""Command-line interface: ``sara-astro <object name>``."""

from __future__ import annotations

import sys

import click

from sara_astro import AstroObject
from sara_astro.exceptions import SaraAstroError


@click.command()
@click.argument("identifier")
@click.option("--cache/--no-cache", default=False, help="Cache catalog responses on disk.")
def main(identifier: str, cache: bool) -> None:
    """Look up ASTRONOMICAL-OBJECT and print a summary.

    Example: sara-astro Sirius
    """
    click.echo("SARA Astro")
    click.echo("-----------")
    click.echo("")
    try:
        obj = AstroObject(identifier, cache=cache)
    except SaraAstroError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(obj.info())


if __name__ == "__main__":
    main()
