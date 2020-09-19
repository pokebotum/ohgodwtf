"""
Created by Epic at 9/19/20
"""
check_id = "DUPLICATED_POKEMON_ID_ONE_USER"


async def execute(user):
    return not len(set(user["pokemons"])) != len(user["pokemons"])
