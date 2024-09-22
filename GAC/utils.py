import os
import json


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
