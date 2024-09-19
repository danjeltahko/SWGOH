from bs4 import BeautifulSoup
from endpoints import get_all_characters
from tqdm import tqdm
import json
import requests
import re
import os


# Get the page HTML as soup
def get_page(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


# Write the data to a file
def write_to_file(data: dict, filename: str):
    # Get the path to the data folder
    path = os.path.join(os.getcwd(), "data")
    # Write the data to a file
    with open(f"{path}/{filename}", "w") as f:
        json_data = json.dumps(data, indent=2)
        # Write the data to the file
        f.write(json_data)


# TODO: Add all the pages available, now we only scrape the first page
def get_all_counters_for_team(leader: str, url: str) -> list[dict[str, list[str]]]:
    """
    Get all the counters from the given URL

    :param url: URL to the page with the counters
    :return: List of dictionaries with the counters
    """

    # Get the page HTML as soup
    soup = get_page(url)
    counters: list = []

    # Iterate through all the counter cards
    # Each counter card has a list of characters
    # It starts with the counter and ends with the defense
    for counter in soup.find_all("div", {"class": "paper paper--size-sm"}):

        # Variables for each counter card
        a_team: list[str] = []  # Attack team
        b_team: list[str] = [leader]  # Defense team
        win_rate = 0

        # Gets all the characters in the counter card
        # Each a tag has a url with the character name
        characters = counter.find_all("a")
        # Iterate through all the urls with the character names
        for character_ref in characters:
            character = character_ref.get("href")
            # URL could look like this:
            # ..CHAMPIONSHIPS_GRAND_ARENA_GA2_EVENT_SEASON_55&d_member=SEVENTHSISTER
            # Hence we split the url by "&" and then by "=" to get the character name
            member, name = character.split("&")[1].split("=")

            # Position is either a (attack) or d (defense)
            # and either lead or member.
            if member[0] == "a":
                a_team.append(name)
            elif member[0] == "d":
                b_team.append(name)

        # Get the win rate and win history data of the counter
        data = counter.find_all("div", {"class": "flex-1"})
        # Iterate through each div in the data
        for d in data:
            # Strip the line of all whitespace
            line = d.get_text(strip=True)
            # If the line starts with "Win" it is the win rate
            if line.startswith("Win"):
                # Remove all non-digits from the line, eg. %99% -> 99
                win_rate = int(re.sub(r"\D", "", line))

        # Append the counter to the list of counters
        counters.append(
            {
                "attack": a_team,
                "defense": b_team,
                "win_rate": win_rate,
            }
        )

    return counters


def run():

    # Dictionary to store all counters
    gac_counters = {}

    # Base URL for the counter pages
    base_url = "https://swgoh.gg/gac/counters/"

    # 1. Get latest GAC SEASON url.
    # TODO: Get the latest GAC season ID
    season_id = "CHAMPIONSHIPS_GRAND_ARENA_GA2_EVENT_SEASON_55"

    # 2. Get all available characters from the API
    all_characters = get_all_characters()

    # 3. Get all counters for each team(leader).
    for character_data in tqdm(all_characters, desc="Scraping GAC.. ", colour="green"):
        # Get the base ID of the character
        character = character_data["base_id"]
        # Create the URL for the counter
        counter_link = f"{base_url}{character}/?season_id={season_id}"
        # Get all counters for the team(leader)
        gac_counters[character] = get_all_counters_for_team(
            leader=character, url=counter_link
        )

    season_name = "Season_55"
    # Write the data to a file
    write_to_file(gac_counters, f"{season_name}.json")


if __name__ == "__main__":
    run()
