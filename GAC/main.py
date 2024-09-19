from .endpoints import get_all_characters, get_player_data
from .csp import calculate
from printinglog import Logger
import json

logger = Logger(format="simple")


NOT_FOUND = []  # Global variable to store all not found characters


def read_data(filename: str) -> dict:
    """
    Read the data from a JSON file

    :param filename: The name of the file to read
    :return: The data from the file
    """
    with open(f"GAC/data/{filename}.json", "r") as f:
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
            "name": character["name"],
            "base_id": character["base_id"],
            "categories": character["categories"],
            "image": character["image"],
        }
    """
    # Get all player characters
    player_data = get_player_data(ally_code=ally_code)

    # Get all existing characters in the game
    all_characters = {
        character["base_id"]: {
            "name": character["name"],
            "base_id": character["base_id"],
            "categories": character["categories"],
            "image": character["image"],
        }
        for character in get_all_characters()
    }

    player_characters: list[dict] = []
    # Iterate through each character in the player data
    for unit in player_data["units"]:
        unit_data = unit["data"]
        # Only add the characters with higher gear level than max_gear_level
        if unit_data["gear_level"] >= max_gear_level:
            # Add the dictionary with the character data to the list
            player_characters.append(all_characters[unit_data["base_id"]])

    return player_characters


def gl_in_team(team: list) -> bool:
    """
    Check if the team has a Galactic Legend

    :param team: List with character objects
    :return: Boolean value if the team has a Galactic Legend
    """
    for character in team:
        if "Galactic Legend" in character["categories"]:
            return True
    return False


def counters_available(
    counter: dict, player_characters: list, dest_list: list, has_gl: bool = False
) -> list[dict]:
    """
    Check if the counter is available for the player.

    :param counter: Dictionary with the counter data
    :param player_units: List with all available player units
    :param dest_list: List to append the counter to, if available
    :return: List with the appended counters
    """

    # Don't add the counter if player doesn't have the required units
    attack: list[dict] = []
    # Iterate through each character id in the counter
    for counter_unit_base_id in counter["attack"]:
        # Check if the player has the required unit
        for character in player_characters:
            if counter_unit_base_id == character["base_id"]:
                attack.append(character)

    # If the counter is available, then add it to the list
    if len(attack) == len(counter["attack"]):
        dest_list.append(
            {
                "attack": attack,
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
) -> dict:
    """
        Transform the data to use character IDs and add all the available counters for each opponent team.

        :param data: Dictionary with the GAC round data
        :param counters_data: Dictionary with the counters for each leader
        :param player_characters: List with all available player characters
        :param focus: List with the zones to focus on
        :param match_threshold: The threshold for how similar the defense team should be to the counter team
        :return: List with the transformed data

    data = {
        "T1": [
            {
                "defense": [
                    {
                        "name": name,
                        "base_id": base_id,
                        "categories": categories
                        "image": image
                    }
                ],
                "eliminated": False,
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
                        "win_rate": 100,
                        "has_gl": True
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


    """

    # Get all existing characters in the game
    all_existing_characters = get_all_characters()
    # Divide the data into opponent and player data
    oppone_data = data["opponent"]
    player_data = data["player"]

    # print(player_data)
    # print("")
    # print(oppone_data)
    # print("")

    # Transform player defense to list of character IDs
    player_defense_characters_with_id = [
        character["base_id"]
        for zone in player_data
        for team in player_data[zone]
        for character in team["defense"]
    ]
    logger.info("Successfully transformed player defense to character IDs")

    # Remove the defense characters from players available characters
    # Each character in the list contains:
    #
    #     {
    #         "name": character["name"],
    #         "base_id": character["base_id"],
    #         "categories": character["categories"],
    #         "image": character["image"],
    #     }
    #
    available_player_characters = [
        character
        for character in player_characters
        if character["base_id"] not in player_defense_characters_with_id
    ]
    logger.info("Successfully removed player defense characters from player units")

    transformed_data = {}
    for zone in oppone_data:

        transformed_zone: list[dict] = []

        if zone not in focus:
            continue

        for team in oppone_data[zone]:

            if team["defense"] == [] or team["eliminated"]:
                continue
            # Find if team contains Galactic Legend
            has_gl = gl_in_team(team["defense"])
            # Leader is always the first character in the team
            leader_character = team["defense"][0]["base_id"]
            # Key for counters_data(dict) is the leader, which holds a list
            # as value with all counters for that team with that leader
            counters_for_leader = counters_data[leader_character]
            # List to store all counters available for the player
            counters: list = []
            # FIND: All counters for the exact same defense team
            base_id_characters = [character["base_id"] for character in team["defense"]]
            for counter in counters_for_leader:
                # Check if the team in def is exact same as counter-def for the team
                if sorted(base_id_characters) == sorted(counter["defense"]):
                    # Add only the counters that are available for the player
                    counters = counters_available(
                        counter=counter,
                        player_characters=available_player_characters,
                        dest_list=counters,
                        has_gl=has_gl,
                    )

                    # Each character in counters will look like this:
                    # {
                    #     "attack": [
                    #         {
                    #             "name": name,
                    #             "base_id": base_id,
                    #             "categories": categories
                    #             "image": image
                    #         }
                    #     ],
                    #     "win_rate": 100,
                    #     "has_gl": True
                    # }

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
                        player_characters=available_player_characters,
                        dest_list=counters,
                        has_gl=has_gl,
                    )

            # If counters is empty, then add a default counter
            # it's either because of couldn't find data on that
            # exact def setup or player doesn't have the required units
            transformed_zone.append({"defense": team["defense"], "counters": counters})

        transformed_data[zone] = transformed_zone

    return transformed_data


def transform_solution(data: dict, solution: list) -> dict:
    """
    Transform the solution to use character IDs

    :param data: Dictionary with the transformed data
    :param solution: List with the solution
    :return: List with the transformed solution

    data: {
        "T1": [
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
                        "win_rate": 100,
                        "has_gl": True
                    }
                ]
            }
        ]
    }

    solution:
    [(index, dict={
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
                "win_rate": 100,
                "has_gl": True
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
    })]
    """
    for _, solution_team in solution:
        defense_team = [character["base_id"] for character in solution_team["defense"]]
        for zone in data:
            for team in data[zone]:
                if defense_team == [
                    character["base_id"] for character in team["defense"]
                ]:
                    team["best_team"] = solution_team["best_team"]

    return data


def main(
    ally_code: str,
    gac_season: str,
    gac_round: dict,
    min_gear_level: int,
    focus_zone: list[str],
):

    print("\n")
    logger.debug("VALIDATION OF DATA:")
    data = gac_round["opponent"]
    for zone in data:
        print(f"======= ZONE : {zone} =======")
        for team in data[zone]:
            defense = [character["base_id"] for character in team["defense"]]
            print(f"Defense: {defense}")

    # Get all ally_code players characters that
    # have gear level greater than min_gear_level
    player_characters = get_all_player_units(
        ally_code=ally_code, max_gear_level=min_gear_level
    )
    print("\n")
    logger.info("Player characters has been fetched")

    # 1. Read the seasons counter data from file
    counters = read_data(gac_season)
    logger.info(f"Counter data for {gac_season} has been read")

    # 2. Read the GAC round data from file
    # gac_round = read_data(gac_round_input)

    # 3. Transform the GAC round data to use character ID
    # and add all the available counters for each opponent team
    data = transform_data(
        data=gac_round,
        counters_data=counters,
        player_characters=player_characters,
        match_threshold=1,
        focus=focus_zone,
    )

    logger.info("GAC round data has been transformed\n")

    logger.debug("VALIDATION OF TRANSFORMED DATA:")
    for zone in data:
        print(f"======= ZONE : {zone} =======")
        for team in data[zone]:
            defense = [character["base_id"] for character in team["defense"]]
            print(f"Defense: {defense}")
            counters = [counter for counter in team["counters"]]
            for counter in counters:
                counter_list = [character["base_id"] for character in counter["attack"]]
                print(f"({counter['win_rate']}) Counter: {counter_list}")
                break

    solution = calculate(data=data)
    transformed_solution = transform_solution(data=data, solution=solution)

    print("\n")
    logger.debug("VALIDATION OF SOLUTION DATA:")
    for zone in transformed_solution:
        print(f"======= ZONE : {zone} =======")
        for team in transformed_solution[zone]:
            defense = [character["base_id"] for character in team["defense"]]
            best_counter = [
                character["base_id"] for character in team["counters"][0]["attack"]
            ]
            counter_team = [
                character["base_id"] for character in team["best_team"]["attack"]
            ]

            print(f"Defense: {defense}")
            print(f"({team['counters'][0]['win_rate']}) Best counter: {best_counter}")
            print(f"({team['best_team']['win_rate']}) Calc counter: {counter_team}")
            print("\n")

    """
    Returns:

    {
        "T1": [
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
                        "win_rate": 100,
                        "has_gl": True
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
    """

    """
    TODO:

    Old ben lean with starkiller, showed Wampa as counter
    but only because there wasn't many counters available.
    , when reduced to 1, then correct counter with jedi revan showed.

    Maybe add somewhere that if the win rate is low, then raise thershold
    """

    return transformed_solution


if __name__ == "__main__":
    main(
        ally_code="454-998-525",
        gac_season="Season_55",
        gac_round={},
        min_gear_level=12,
        focus_zone=["B1", "B2"],
    )
