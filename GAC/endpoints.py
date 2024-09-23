import requests

BASE_URL = "https://swgoh.gg/api/"

"""
/api/units/
/api/ships/
/api/gear/
/api/stat-definitions/
/api/datacron-affix-template-sets/
/api/datacron-sets/
/api/datacron-templates/
/api/guild-profile/<guild_id>/
/api/player/<ally_code>/
"""


def get_all_abilities() -> list[dict]:
    """
    Returns list with dictionraies of character abilities

    Dict:
        base_id(str): Base ID
        ability_id(str): Ability ID
        name(str): Name of the ability
        image(str): URL to ability image
        tier_max(int): Highest level of ability
        is_zeta(bool): Boolean value if ability has zeta
        is_omega(bool): Boolean value if ability has omega
        is_omicron(bool): Boolean value if ability has omicron
        is_ultimate(bool): Boolean value if ability has ULT(GL)
        description(str): Description of the ability
        combat_type(int): Combat type
        omicron_mode(int): Omicron mode
        type(int): Type
        character_base_id(str): Character base ID
        ship_base_id(str | None): Ship base ID
        omicron_batle_types(list): Omicron battle types
    """
    response = requests.get(url=BASE_URL + "abilities")
    data = response.json()
    return data


def get_all_characters() -> list[dict]:
    """
    Returns list with dictionraies of character abilities

    Dict:
        name(str): Character name
        base_id(str): Character ID
        url(str): URL
        image(str): IMG URL
        power(str): Highest total power
        description(str): Character description
        combat_type(int): Combat type
        gear_levels(list): Gear levels
        alignment(str): Alignment (Light, Dark, Neutral)
        categories(list): Character tags
        ability_classes(list): Ability classes
        role(str): Role
        ship(str): Ship name
        ship_slot(int): Ship slot
        activate_shard_count(int): Shard count
    """
    response = requests.get(url=BASE_URL + "characters")
    data = response.json()
    return data


def get_stat_definitions() -> list[dict]:
    """
    Returns list with dictionraies of character abilities

    Dict:
        base_id(str): Base ID
        ability_id(str): Ability ID
        name(str): Name of the ability
        image(str): URL to ability image
        tier_max(int): Highest level of ability
        is_zeta(bool): Boolean value if ability has zeta
        is_omega(bool): Boolean value if ability has omega
        is_omicron(bool): Boolean value if ability has omicron
        is_ultimate(bool): Boolean value if ability has ULT(GL)
        description(str): Description of the ability
        combat_type(int): Combat type
        omicron_mode(int): Omicron mode
        type(int): Type
        character_base_id(str): Character base ID
        ship_base_id(str | None): Ship base ID
        omicron_batle_types(list): Omicron battle types
    """
    response = requests.get(url=BASE_URL + "stat-definitions")
    data = response.json()
    return data


def get_player_data(ally_code: str) -> dict:
    """
    Returns list with dictionraies of character abilities

    Dict:
        data(dict): Player data
        units(list): Player units
        mods(list): Player mods
        datacron(list): Player datacron
    """
    # Remove any dashes from the ally code
    ally_code = ally_code.replace("-", "")
    response = requests.get(url=BASE_URL + f"player/{ally_code}")
    data = response.json()
    return data


def get_datacron_sets():
    response = requests.get(url=BASE_URL + "datacron-sets")
    data = response.json()
    return data


def get_datacron_templates():
    response = requests.get(url=BASE_URL + "datacron-templates")
    data = response.json()
    return data


def get_datacron_affix_template_sets():
    response = requests.get(url=BASE_URL + "datacron-affix-template-sets")
    data = response.json()
    return data


if __name__ == "__main__":
    datacrons = get_datacron_sets()
