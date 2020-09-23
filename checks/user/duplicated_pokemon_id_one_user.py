"""
Created by Epic at 9/19/20
"""
check_id = "DUPLICATED_POKEMON_ID_ONE_USER"


async def execute(user):
    checked = []
    for pokemon_id in user["pokemons"]:
        if pokemon_id in checked:
            return False, pokemon_id
        checked.append(pokemon_id)
    return True, None
