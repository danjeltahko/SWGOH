import os
import json
import re


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
