"""
Create complete data for the GAC project
"""

from endpoints import (
    get_all_characters,
    get_datacron_sets,
    get_datacron_templates,
    get_datacron_affix_template_sets,
)
from utils import (
    read_data,
    write_to_file,
    get_3v3_seasons,
    get_5v5_seasons,
    get_season_date,
)
from rich import print
from datetime import datetime
from dateutil.relativedelta import relativedelta


def find_duplicates(data: list[dict]) -> dict:
    """
    Find all the duplicate fights from all seasons
    where attack vs defense is exactly the same

    Parameters:
    ----------
    data: list[dict]
        List of dictionaries where each dictionary is a season
        and the data is the fights in the season with leader
        as the key and the value is a list of dictionaries
        with the attack vs defense and the win_rate, avg_banners, seen

    Returns:
    --------
    dict
        Dictionary where the key is the character base_id
        and the value is a list of dictionaries where each
        dictionary is a fight with the attack vs defense
        and the win_rate, avg_banners, seen for each season
    """
    all_characters = get_all_characters()

    merged_data: dict = {}

    # Iterate over all the characters in the game
    for character in all_characters:
        character_base_id = character["base_id"]
        # Iterate over all the seasons
        counter_data: list = []
        found_fights: list = []
        # Iterate over all the seasons
        for season, season_data in data:
            """
            season = 47
            season_data = {
                BASE_ID: [
                    {
                        "attack": [BASE_ID, ...],
                        "defense": [BASE_ID, ...],
                        "win_rate": 0.5,
                        "avg_banners": 50,
                        "seen": 100,
                    },
                ]
            }
            """
            # Check if the character is in the season
            if character_base_id not in season_data.keys():
                print(f"{character_base_id} not found in season")
                continue

            # Add all the attack vs defense to a list if they don't exist
            # If the key already exists, add the values to of the list
            for counter in season_data[character_base_id]:
                """
                counter = {
                    "attack": [BASE_ID, ...],
                    "defense": [BASE_ID, ...],
                    "win_rate": 0.5,
                    "avg_banners": 50,
                    "seen": 100,
                }
                """
                # Set the exact fight, with attack vs defense
                fight = (counter["attack"], counter["defense"])
                # If the exact fight is found, append the data about the fight
                if fight in found_fights:
                    # Iterate over the counter_data to find the fight
                    for added_counter in counter_data:
                        # Add the season & its win_rate, avg_banners, seen to the fight
                        if (
                            added_counter["attack"] == counter["attack"]
                            and added_counter["defense"] == counter["defense"]
                        ):
                            added_counter["win_rate"].append(
                                (season, counter["win_rate"])
                            )
                            added_counter["avg_banners"].append(
                                (season, counter["avg_banners"])
                            )
                            added_counter["seen"].append((season, counter["seen"]))
                # If the exact fight is not found, add the fight to the list
                else:
                    counter_data.append(
                        {
                            "attack": counter["attack"],
                            "defense": counter["defense"],
                            "win_rate": [(season, counter["win_rate"])],
                            "avg_banners": [(season, counter["avg_banners"])],
                            "seen": [(season, counter["seen"])],
                        }
                    )
                    # Add the fight to the found fights
                    found_fights.append(fight)

        merged_data[character_base_id] = counter_data

    return merged_data


def transform_data(data: dict) -> dict:
    """
    Transform the data so the win_rate, avg_banners, seen
    are averaged for each fight

    Parameters:
    ----------
    data: dict
        Dictionary where the key is the character base_id
        and the value is a list of dictionaries where each
        dictionary is a fight with the attack vs defense
        and the win_rate, avg_banners, seen for each season

    Returns:
    --------
    dict
        Dictionary where the key is the character base_id
        and the value is a list of dictionaries where each
        dictionary is a fight with the attack vs defense
        and the average win_rate, avg_banners, seen for each fight
    """
    datacrons = get_datacrons()
    transformed_data: dict = {}
    for leader_character in data:
        average_fight_data: list = []
        for fight in data[leader_character]:
            """
            fight = {
                "attack": [BASE_ID, ...],
                "defense": [BASE_ID, ...],
                "win_rate": [(41, 0.5), ...],
                "avg_banners": [(41, 50), ...],
                "seen": [(41, 100), ...],
            }
            """
            # Remove attack teams that only worked with datacrons
            # This only removes the attack teams that was solo (len == 1)
            # but if the "solo" team was used outside of that period
            # then it will still be included
            has_datacron_character = True
            if len(fight["attack"]) == 1 and fight["attack"][0] in datacrons.keys():
                character = fight["attack"][0]
                # If the character is found in the datacron list
                # check if the counter was done during the datacrons
                # active period
                seasons = [season for season, _ in fight["seen"]]
                for season in seasons:
                    # Season this attack was used
                    season_start, season_end = get_season_date(season)
                    datacron_start = datacrons[character]["start"]
                    datacron_expire = datacrons[character]["expire"]
                    if datacron_start < season_end and season_start < datacron_expire:
                        continue
                    else:
                        has_datacron_character = False
            else:
                has_datacron_character = False

            # Skip adding the counter if it was only used with datacron
            if has_datacron_character:
                continue

            wins: list = []
            banners: list = []
            for index, seen_data in enumerate(fight["seen"]):
                _, seen = seen_data
                # Add every win_rate & banners per seen to the wins list
                for _ in range(seen):
                    wins.append(fight["win_rate"][index][1])
                    banners.append(fight["avg_banners"][index][1])

            # Calculate the average win_rate & avg_banners
            average_wins = float(sum(wins) / len(wins)).__round__(2)
            average_banners = float(sum(banners) / len(banners)).__round__(2)

            # Append the average win_rate, avg_banners, seen to the fight
            average_fight_data.append(
                {
                    "attack": fight["attack"],
                    "defense": fight["defense"],
                    "win_rate": average_wins,
                    "avg_banners": average_banners,
                    "seen": sum([seen for _, seen in fight["seen"]]),
                }
            )

        transformed_data[leader_character] = average_fight_data

    return transformed_data


def sort_transformed_data(data: dict) -> dict:
    """
    Sort the data based on win_rate, and seen if same
    and avg_banners if same as seen.

    Parameters:
    ----------
    data: dict
        Dictionary where the key is the character base_id
        and the value is a list of dictionaries where each
        dictionary is a fight with the attack vs defense
        and the average win_rate, avg_banners, seen for each fight

    Returns:
    --------
    dict
        Dictionary where the key is the character base_id
        and the value is a list of dictionaries where each
        dictionary is a fight with the attack vs defense
        and the average win_rate, avg_banners, seen for each fight
        sorted based on win_rate, seen, avg_banners
    """

    for character_id in data:
        # Sort the fights based on win_rate
        data[character_id] = sorted(
            data[character_id],
            key=lambda x: (x["win_rate"], x["seen"], x["avg_banners"]),
            reverse=True,
        )

    return data


def get_datacrons() -> dict:
    """
    Get all the datacrons for each character in the game
    and the expiration date for the datacron

    Returns:
    {
        "CHARACTER_ID": {
            "datacron": "DATA_ID",
            "expire": "DATE",
            "start": "DATE",
        },
        ...
    }

    """

    datacrons_sets = get_datacron_sets()
    datacrons_templates = get_datacron_templates()
    datacrons_affix = get_datacron_affix_template_sets()
    all_characters = get_all_characters()

    crons = {}
    # Iterate through all the datacron templates
    for template in datacrons_templates:
        # In counters data, we only have from season 41 and onwards
        # Therefore no need for datacrons before that (2023-06-20)
        if template["set_id"] < 8:
            continue
        # Use only templates that ends with "base"
        # In other words, has all the possible datacrons
        # for specific characters in the game
        if template["base_id"][-4:] == "base":
            # ability_sets holds the id for characters
            # eg. [ability_set_thirdsister_001, ...]
            ability_sets = []
            # Iterate through the tiers to get the ability sets
            for tier in template["tiers"]:
                # Tier 9 holds character specific sets
                if tier["tier_id"] == 9:
                    ability_sets += tier["affix_template_set_ids"]

            # Iterate through all the ability sets
            for ability in ability_sets:
                # Iterate through all the affixes that holds
                # the data about each bonus ability
                # eg. scope_target_name = 'Critical Chance'
                for affix in datacrons_affix:
                    # But we only want to get the abilities that
                    # are character specific, not the general ones
                    if affix["base_id"] == ability:
                        # Get the expiration time for the datacron
                        # eg. 2022-12-28 08:00:00+00:00 -> 2022-12-28
                        expire = [
                            cron["expiration_time"]
                            for cron in datacrons_sets
                            if cron["id"] == template["set_id"]
                        ][0].split(" ")[0]
                        # Sets start date for datacron 3 months before expire
                        start_date = datetime.strptime(
                            expire, "%Y-%m-%d"
                        ).date() - relativedelta(months=3)
                        # Get the character id for the character
                        character_id = [
                            character["base_id"]
                            for character in all_characters
                            if character["name"]
                            == affix["affix_templates"][0]["scope_target_name"]
                        ][0]
                        # Add the character datacron
                        crons[character_id] = {
                            "datacron": template["set_id"],
                            "expire": datetime.strptime(expire, "%Y-%m-%d").date(),
                            "start": start_date,
                        }

    return crons


def run():

    for mode in ["3v3", "5v5"]:
        seasons_data = []
        # Get all the seasons for the mode
        if mode == "3v3":
            seasons = get_3v3_seasons()
        else:
            seasons = get_5v5_seasons()

        # 1. Read all the data for each season
        for season in sorted(seasons):
            # Append the season and the data to the list
            # eg. (47, {BASE_ID: [{attack: [BASE_ID, ...],}]}
            seasons_data.append((season, read_data(f"{mode}/Season_{season}")))

        # 2. Merge all seasons so no duplicates are included, they are merged
        merged_data = find_duplicates(seasons_data)

        # 3. Calculate the average win_rate, avg_banners, seen for each fight
        transformed_data = transform_data(merged_data)

        # 4. Sort the data based on win_rate, and seen if same.
        sorted_data = sort_transformed_data(transformed_data)

        # 5. Save the data to a file
        write_to_file(sorted_data, f"{mode}.json")
        print(f"Finished creating {mode} data")


if __name__ == "__main__":
    run()
