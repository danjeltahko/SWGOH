"""
Main program for GAC CLI data management.
"""

import typer

from get_data import run as scrape_data
from create_data import run as create_data

app = typer.Typer(help="GAC CLI data management")


@app.command()
def scrape():
    """
    Scrape the data from the web.
    """
    scrape_data()


@app.command()
def create():
    """
    Create full data for the GAC project.
    """
    create_data()


if __name__ == "__main__":
    app()
