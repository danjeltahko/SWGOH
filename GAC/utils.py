import os
import json
import re
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def write_to_file(data: dict, filename: str) -> None:
    """
    Writes the data to a file

    Parameters:
    ----------
    data: dict
        Data to write to the file

    filename: str
        Name of the file to write the data to

    """
    # Get the path to the data folder
    path = os.path.join(os.getcwd(), "GAC/data")
    # Write the data to a file
    with open(f"{path}/{filename}", "w") as f:
        json_data = json.dumps(data, indent=2)
        # Write the data to the file
        f.write(json_data)


def read_data(filename: str) -> dict:
    """
    Read the data from a JSON file

    Parameters:
    ----------
    filename: str
        The name of the file to read

    Returns:
    -------
    data: dict
        The data from the file
    """
    # Get the path to the data folder
    path = os.path.join(os.getcwd(), "GAC/data")
    with open(f"{path}/{filename}.json", "r") as f:
        data = json.load(f)
    return data


def get_3v3_seasons() -> list:
    """
    Get all the scraped seasons from 3v3

    Returns:
    -------
    seasons: list
        List of scraped seasons
    """
    # Get the path to the data folder
    path = os.path.join(os.getcwd(), "GAC/data/3v3")
    # Get all the scraped seasons
    seasons = [
        int(re.search(r"\d+", f).group())
        for f in os.listdir(path)
        if f.endswith(".json")
    ]
    return seasons


def get_5v5_seasons() -> list:
    """
    Get all the scraped seasons from 5v5

    Returns:
    -------
    seasons: list
        List of scraped seasons
    """
    # Get the path to the data folder
    path = os.path.join(os.getcwd(), "GAC/data/5v5")
    # Get all the scraped seasons
    seasons = [
        int(re.search(r"\d+", f).group())
        for f in os.listdir(path)
        if f.endswith(".json")
    ]
    return seasons


def get_all_scraped_seasons() -> list:
    """
    Get all the scraped seasons

    Returns:
    -------
    seasons: list
        List of scraped seasons
    """
    # Get all the scraped seasons
    seasons = get_3v3_seasons() + get_5v5_seasons()
    return seasons


def get_season_date(season: int) -> tuple[date, date]:
    """
    Get the date of the season

    Parameters:
    ----------
    season: int
        The season number

    Returns:
    -------
    new_date: tuple[date, date]
        The start and end date of the season
    """
    # Each GAC season is every 28 days
    # The first one scraped was season 41 on June 20, 2023
    base_date = (41, date(2023, 6, 20))
    start_date = base_date[1] + relativedelta(days=28 * (season - base_date[0]))
    end_date = start_date + relativedelta(days=21)
    return start_date, end_date
