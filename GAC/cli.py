from endpoints import get_all_characters, get_player_data
from printinglog import Logger
from copy import deepcopy
import json

logger = Logger(format="simple")


NOT_FOUND = []  # Global variable to store all not found characters


def read_data(filename: str) -> dict:
    """
    Read the data from a JSON file

    :param filename: The name of the file to read
    :return: The data from the file
    """
    with open(f"data/{filename}.json", "r") as f:
        data = json.load(f)
    return data


def get_all_player_units(ally_code: str, max_gear_level=12) -> list:
    """
    Get all player characters with greater or equal to max_gear_level

    :param ally_code: The ally code of the player
    :param max_gear_level: The minimum gear level of the characters
    :return: List with all player characters with greater or equal to max_gear_level

    Each character in the list contains:

        {
            "name": str,
            "base_id": str,
        }
    """
    # Get all player characters
    player_data = get_player_data(ally_code=ally_code)

    units_with_base_id = []
    # Iterate through each character in the player data
    for unit in player_data["units"]:
        unit_data = unit["data"]
        if unit_data["gear_level"] >= max_gear_level:
            units_with_base_id.append(
                {
                    "name": unit_data["name"],
                    "base_id": unit_data["base_id"],
                }
            )

    return units_with_base_id


def transform_team(team: list, all_existing_characters: list) -> tuple[list, bool]:
    """
    Transform a list with character names to a list with character IDs

    :param team: List with character names
    :param all_existing_characters: List with all existing characters
    :return: List with character IDs, and a boolean value if the team has a Galactic Legend
    """
    transformed_team = []
    has_gl = False
    # Iterate through each member in the team
    for member in team:
        character_id = None
        # Iterate through all existing characters to find the character ID
        for character in all_existing_characters:
            if member == character["name"]:
                character_id = character["base_id"]
                # Check if the character is a Galactic Legend
                if "Galactic Legend" in character["categories"]:
                    has_gl = True

        # If the character ID is not found
        # print the character ID
        if not character_id:
            NOT_FOUND.append(member)
            continue
        # Otherwise append the character ID to the transformed team
        else:
            transformed_team.append(character_id)

    return transformed_team, has_gl


def counters_available(
    counter: dict, player_units: list, dest_list: list, has_gl: bool = False
) -> list[dict]:
    """
    Check if the counter is available for the player.

    :param counter: Dictionary with the counter data
    :param player_units: List with all available player units
    :param dest_list: List to append the counter to, if available
    :return: List with the appended counters
    """

    # Don't add the counter if player doesn't have the required units
    available = True
    for counter_unit in counter["attack"]:
        if counter_unit not in player_units:
            available = False
            break

    # If the counter is available, then add it to the list
    if available:
        dest_list.append(
            {
                "attack": counter["attack"],
                "win_rate": counter["win_rate"],
                "has_gl": has_gl,
            }
        )

    return dest_list


def transform_data(
    data: dict,
    counters_data: dict,
    player_characters: list,
    focus: list[str],
    match_threshold: int = 5,
) -> list:
    """
        Transform the data to use character IDs and add all the available counters for each opponent team.

        :param data: Dictionary with the GAC round data
        :param counters_data: Dictionary with the counters for each leader
        :param player_units: List with all available player units
        :param focus: List with the zones to focus on
        :param match_threshold: The threshold for how similar the defense team should be to the counter team
        :return: List with the transformed data


    data = [
        {
            "ZONE": zone,
            "TEAMS": [
                {
                    "defense": [
                        {
                            "name": name,
                            "base_id": base_id,
                            "categories": categories
                            "image": image
                        }
                    ],
                    "counters": [
                        {
                            "attack": [
                                {
                                    "name": name,
                                    "base_id": base_id,
                                    "categories": categories
                                    "image": image
                                }
                            ],
                            "win_rate": 100
                        }
                    ],
                    "best_team": {
                        "attack": [
                            {
                                "name": name,
                                "base_id": base_id,
                                "categories": categories
                                "image": image
                            }
                        ],
                        "win_rate": 100
                    }
                }

            ]
        }
    ]

    """

    transformed_data = []
    # Get all existing characters in the game
    all_existing_characters = get_all_characters()
    # Divide the data into opponent and player data
    oppone_data = data["opponent"]
    player_data = data["player"]

    # Transform player defense to list of character IDs
    players_defense_units = [
        units
        for zone in player_data
        for team in zone["TEAMS"]
        for units in transform_team(team["defense"], all_existing_characters)[0]
    ]
    # Remove those units from player_units
    player_units = [
        unit for unit in player_characters if unit not in players_defense_units
    ]

    """
    data = [
        {
            "ZONE": ZONE(1-3),
            "TEAMS": [
                {
                    "defense":  [CHARACTER_ID...],
                    "counters": [
                        {
                            "attack": [CHARACTER_ID...],
                            "win_rate": 100,
                        }
                    ]
                }
            ]
        },
    ]

    """

    # Iterate through each opponents zone in data (T1, B1, B2*)
    for zone in oppone_data:
        if zone["ZONE"] not in focus:
            continue
        # Create a new zone dictionary
        transformed_zone = {"ZONE": zone["ZONE"], "TEAMS": []}
        # Iterate through each team in the zone
        for team in zone["TEAMS"]:

            # Creates a new transformed team list, where we transform
            # each charachters name to their character ID.
            transformed_team, has_gl = transform_team(
                team=team["defense"], all_existing_characters=all_existing_characters
            )

            # Leader is always the first character in the team
            leader_character = transformed_team[0]

            # Key for counters_data(dict) is the leader, which holds a list
            # as value with all counters for that team with that leader
            counters_for_leader = counters_data[leader_character]

            # List to store all counters available for the player
            counters = []

            # FIND: All counters for the exact same defense team
            for counter in counters_for_leader:
                # Check if the team in def is exact same as counter-def for the team
                if sorted(transformed_team) == sorted(counter["defense"]):
                    # Add only the counters that are available for the player
                    counters = counters_available(
                        counter=counter,
                        player_units=player_units,
                        dest_list=counters,
                        has_gl=has_gl,
                    )

            # TODO: Maybe add, that if a GL exists in the TEAM, but not as leader.
            # Then add the exact same counter, and maybe even for that leaders team.

            # If length of counters is too small, then add all available counters
            # for the leader, even if the defense team is not the exact same
            if len(counters) <= match_threshold:
                # Reinitiallize counters, and add them again with no need of exact match.
                counters = []
                # Iterate through each counter for the leader
                for counter in counters_for_leader:
                    # Add only the counters that are available for the player
                    counters = counters_available(
                        counter=counter,
                        player_units=player_units,
                        dest_list=counters,
                        has_gl=has_gl,
                    )

            # If counters is empty, then add a default counter
            # it's either because of couldn't find data on that
            # exact def setup or player doesn't have the required units

            # Append the transformed team to the ZONE
            transformed_zone["TEAMS"].append(
                {"defense": transformed_team, "counters": counters}
            )

        transformed_data.append(transformed_zone)

    return transformed_data


def transform_solution(data: list, solution: dict) -> list:
    """
    resutl = [
        {
            "ZONE": 1,
            "TEAM": [
                {
                    "defense": [CHARACTER_ID...],
                    "counter": [CHARACTER_ID...],
                    "win_rate": 100,
                }
            ]
    ]
    """

    result = []
    for value in data:

        zone = {
            "ZONE": value["ZONE"],
            "TEAM": [],
        }

        for team in value["TEAMS"]:

            for _, sol in solution:

                all_characters = get_all_characters()

                # DEFENSE
                # Revert the character IDs to character names
                defense_with_names = []
                if sol["defense"] == team["defense"]:

                    for character_id in team["defense"]:
                        for character in all_characters:
                            if character_id == character["base_id"]:
                                defense_with_names.append(character["name"])

                    # COUNTER
                    # Revert the character IDs to character names
                    counters_with_names = []
                    for character_id in sol["best_team"]["attack"]:
                        for character in all_characters:
                            if character_id == character["base_id"]:
                                counters_with_names.append(character["name"])
                    t = {
                        "defense": defense_with_names,
                        "counter": counters_with_names,
                        "win_rate": sol["best_team"]["win_rate"],
                    }
                    zone["TEAM"].append(t)

        result.append(zone)

    return result


def main(
    ally_code: str,
    gac_season: str,
    gac_round_input: str,
    max_gear_level: int,
    focus_zone: list[str],
):

    # Get all all_code players characters that
    # have geaaar level greater than max_gear_level
    player_characters = get_all_player_units(
        ally_code=ally_code, max_gear_level=max_gear_level
    )

    # 1. Read the seasons counter data from file
    counters = read_data(gac_season)

    # 2. Read the GAC round data from file
    gac_round = read_data(gac_round_input)

    # 3. Transform the GAC round data to use character ID
    # and add all the available counters for each opponent team
    data = transform_data(
        data=gac_round,
        counters_data=counters,
        player_characters=player_characters,
        match_threshold=1,
        focus=focus_zone,
    )
    """
    TODO:

    Old ben lean with starkiller, showed Wampa as counter
    but only because there wasn't many counters available.
    , when reduced to 1, then correct counter with jedi revan showed.

    Maybe add somewhere that if the win rate is low, then raise thershold
    """

    if NOT_FOUND:
        for member in NOT_FOUND:
            logger.error(f"Character {member} not found")
        return

    for zone in data:
        print(f"======= ZONE : {zone['ZONE']} =======\n")
        for team in zone["TEAMS"]:
            print(f"Defense: {team['defense']}")
            print(f"Counters: {team['counters']}\n")

    # 4. Calcualate which team to attack with which team
    # calculate_best_attack(data=data)
    from csp import calculate

    # solution = calculate(data=data)
    #
    # result = transform_solution(data=data, solution=solution)
    #
    # for zone in result:
    #     print(f"======= ZONE : {zone["ZONE"]} =======\n")
    #     for team in zone["TEAM"]:
    #         print(f"Defense: {team["defense"]}")
    #         print(f"Counter: {team["counter"]}")
    #         print(f"Win Rate: {team["win_rate"]}\n")


if __name__ == "__main__":
    main(
        ally_code="454-998-525",
        gac_season="Season_55",
        gac_round_input="test",
        max_gear_level=12,
        focus_zone=["B1", "B2"],
    )

"""

https://swgoh.gg/gac/counters/GLREY/?season_id=CHAMPIONSHIPS_GRAND_ARENA_GA2_EVENT_SEASON_55&page=1&d_member=EPIXFINN%2CEPIXPOE
"""


"""
This would be better!!
-----------------------
data = [
    {
        "ZONE": zone,
        "TEAMS": [
            {
                "defense": [
                    {
                        "name": name,
                        "base_id": base_id,
                        "categories": categories
                        "image": image
                    }
                ],
                "counters": [
                    {
                        "attack": [
                            {
                                "name": name,
                                "base_id": base_id,
                                "categories": categories
                                "image": image
                            }
                        ],
                        "win_rate": 100
                    }
                ],
                "best_team": {
                    "attack": [
                        {
                            "name": name,
                            "base_id": base_id,
                            "categories": categories
                            "image": image
                        }
                    ],
                    "win_rate": 100
                }
            }

        ]
    }
]

"""
