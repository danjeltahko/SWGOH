from .endpoints import get_all_characters, get_player_data
from .csp import calculate
from .utils import read_data
from printinglog import Logger

logger = Logger(format="simple")


def get_all_player_units(ally_code: str, min_gear_level=12) -> list:
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
        if unit_data["gear_level"] >= min_gear_level:
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

    # Divide the data into opponent and player data
    oppone_data = data["opponent"]
    player_data = data["player"]
    used_attack = data["used_attack"]
    """

    'used_attack': [
        [
            
            {
                "name": name,
                "base_id": base_id,
                "categories": categories
                "image": image
            }
        ]
    ]

    """

    # Transform player defense to list of character IDs
    player_defense_characters_with_id = [
        character["base_id"]
        for zone in player_data
        for team in player_data[zone]
        for character in team["defense"]
    ]

    # Add the used attack to the player defense characters
    if used_attack != []:
        for team_list in used_attack:
            for character in team_list:
                player_defense_characters_with_id.append(character["base_id"])

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
    mode: str,
    gac_round: dict,
    min_gear_level: int,
    focus_zone: list[str],
    debug: bool = False,
):

    # Get the opponent data
    data: dict = gac_round["opponent"]

    # Print the data for validation
    if debug:
        print("\n")
        logger.debug("VALIDATION OF OPPONENTS DEFENSE:")
        data = gac_round["opponent"]
        for zone in data:
            print(f"======= ZONE : {zone} =======")
            for team in data[zone]:
                defense = [character["base_id"] for character in team["defense"]]
                print(f"Defense: {defense}")

    # Get all ally_code players characters that
    # have gear level greater than min_gear_level
    player_characters = get_all_player_units(
        ally_code=ally_code, min_gear_level=min_gear_level
    )

    # Read the counter data from file | 3v3.json or 5v5.json
    counters = read_data(mode)

    # Transform the GAC round data to use character ID
    # and add all the available counters for each opponent team
    data_to_calculate = transform_data(
        data=gac_round,
        counters_data=counters,
        player_characters=player_characters,
        match_threshold=1,
        focus=focus_zone,
    )

    # Print the transformed data for validation
    if debug:
        logger.debug("VALIDATION OF TRANSFORMED DATA:")
        for zone in data_to_calculate:
            print(f"======= ZONE : {zone} =======")
            for team in data_to_calculate[zone]:
                defense = [character["base_id"] for character in team["defense"]]
                print(f"Defense: {defense}")
                counters = [counter for counter in team["counters"]]
                for counter in counters:
                    counter_list = [
                        character["base_id"] for character in counter["attack"]
                    ]
                    print(f"({counter['win_rate']}) Counter: {counter_list}")

    # Calculate the best teams to use against the opponent teams
    solution = calculate(data=data_to_calculate)

    # Transform the solution to be added to the original opponent data
    transformed_solution = transform_solution(data=data, solution=solution)

    # Print the transformed solution for validation
    if debug:
        logger.debug("VALIDATION OF SOLUTION DATA:")
        for zone in transformed_solution:
            print(f"======= ZONE : {zone} =======")
            for team in transformed_solution[zone]:
                defense = [character["base_id"] for character in team["defense"]]
                print(f"Defense: {defense}")
                if defense and not team["eliminated"]:
                    best_counter = [
                        character["base_id"]
                        for character in team["best_team"]["attack"]
                    ]
                    print(f"Counter: {best_counter}")

    return transformed_solution


if __name__ == "__main__":
    main(
        ally_code="454-998-525",
        mode="3v3",
        gac_round={},
        min_gear_level=12,
        focus_zone=["B1", "B2"],
    )
