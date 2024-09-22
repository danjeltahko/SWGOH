from bs4 import BeautifulSoup
from endpoints import get_all_characters
from utils import (
    write_to_file,
    get_all_scraped_seasons,
    get_3v3_seasons,
    get_5v5_seasons,
)
from printinglog import Logger
from tqdm import tqdm
import requests
import re
from time import sleep

logger = Logger(format="simple")


def get_page(url):
    """
    Get the url response as a soup object

    Parameters:
    ----------
    url: str
        URL to the page

    Returns:
    -------
    soup: BeautifulSoup
        Soup object of the page
    """
    try:
        sleep(1)
        page = requests.get(url)
        page.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error: {e}")
        raise

    soup = BeautifulSoup(page.content, "html.parser")
    return soup


def get_all_counters_for_team(leader: str, url: str) -> list[dict[str, list[str]]]:
    """
    Get all the counters from the given URL for the team(leader)

    Parameters:
    ----------
    leader: str
        Leader of the team

    url: str
        URL to the page with the counters

    Returns:
    -------
    counters: list[dict[str, list[str]]]
        List of counters for the team(leader)

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
        d_team: list[str] = [leader]  # Defense team
        win_rate = 0
        avg_banners = 0.0
        seen = 0

        # Gets all the characters in the counter card
        # Each <a> tag has a url with the character name
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
                d_team.append(name)

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
            # If the line starts with "Avg" it is the average banners
            elif line.startswith("Avg"):
                # Remove the "Avg" from the line, eg. Avg 50 -> 50
                avg_banners = float(line.strip("Avg"))
            # If the line starts with "Seen" it is the value of times counter been seen
            elif line.startswith("Seen"):
                seen_raw = line.strip("Seen")
                # First line will be the complete string, add last time
                if not "Win" in seen_raw:
                    # eg. 1,327 -> 1327
                    seen_raw = seen_raw.replace(",", "")
                    # eg. 11.3K -> 11300
                    seen_raw = seen_raw.replace(".", "")
                    seen_raw = seen_raw.replace("K", "00")
                    # Save the value as an integer
                    seen = int(seen_raw)

        # Append the counter to the list of counters
        counters.append(
            {
                "attack": a_team,
                "defense": d_team,
                "win_rate": win_rate,
                "avg_banners": avg_banners,
                "seen": seen,
            }
        )

    # If there is a next page, get the counters from the next page
    pagination = soup.find_all("a", {"class": "pagination__link"})
    if pagination:
        next = pagination[-1].get_text(strip=True)
        if next == "Next":
            # Get the next page URL
            next_page = "https://swgoh.gg/" + pagination[-1].get("href")
            # Get all counters from the next page
            counters += get_all_counters_for_team(leader, next_page)

    return counters


def run():
    """
    Each counter in gac_counters contains the following data:

    {
        "CHARACTER_ID": [
            {
                "attack": [CHARACTER_ID, ...],
                "defense": [CHARACTER_ID, ...],
                "win_rate": int(win_rate),
                "avg_banners": float(avg_banners),
                "seen": int(seen),
            }
        ]
    }
    """

    # Base URL for the counter pages
    base_url = "https://swgoh.gg/gac/counters/"

    # Get the latest scraped season
    oldest_season = max(get_all_scraped_seasons())

    # Get the latest season
    soup = get_page(url="https://swgoh.gg/gac/counters/")
    latest_season = max(
        [
            int(
                season.find("div", {"class": "fw-bold text-muted mb-2 small"})
                .get_text(strip=True)
                .split(" ")[-1]
            )
            for season in soup.find_all("a", {"class": "paper d-block link-no-style"})
        ]
    )

    # Scrape all seasons from the oldest to the latest
    for season in range(oldest_season + 1, latest_season + 1):

        # Dictionary to store all counters
        gac_counters = {}

        # 1. Set the latest GAC SEASON url.
        season_id = f"CHAMPIONSHIPS_GRAND_ARENA_GA2_EVENT_SEASON_{season}"

        # 2. Get all available characters from the API
        all_characters = get_all_characters()

        # 3. Get all counters for each team(leader).
        for character_data in tqdm(
            all_characters, desc=f"Scraping GAC Season {season} >", colour="green"
        ):
            # Get the base ID of the character
            character = character_data["base_id"]
            # Create the URL for the counter
            counter_link = f"{base_url}{character}/?season_id={season_id}"
            # URL: https://swgoh.gg/gac/counters/DARTHTRAYA/?season_id=CHAMPIONSHIPS_GRAND_ARENA_GA2_EVENT_SEASON_
            # Get all counters for the team(leader)
            gac_counters[character] = get_all_counters_for_team(
                leader=character, url=counter_link
            )

        # 4. Save the data to the correct folder
        if (max(get_3v3_seasons()) + 1) == season:
            location = f"3v3/Season_{season}.json"
        elif (max(get_5v5_seasons()) + 1) == season:
            location = f"5v5/Season_{season}.json"
        else:
            raise ValueError("GAC season is not 3v3 or 5v5")

        # Write the data to a file
        write_to_file(gac_counters, location)


if __name__ == "__main__":
    run()
