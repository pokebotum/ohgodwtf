"""
Created by Epic at 9/17/20
"""
from speedcord import Client
from speedutils import typing
from os import environ as env
from pymongo import MongoClient
from checks.user import duplicated_pokemon_id_one_user
from asyncio import sleep

bot = Client(512, token=env["TOKEN"])
db_client = MongoClient(env["MONGO_URI"])
db = db_client.pokebot
users_table = db.users
pokemon_table = db.users_pokemoms

banned_users = []
user_checks = [duplicated_pokemon_id_one_user]


@bot.listen("MESSAGE_CREATE")
async def on_message(data, shard):
    args = data["content"].lower().split(" ")
    if args[0] == "wtf!status":
        route = typing.send_message(data["channel_id"])
        await bot.http.request(route, json={"content": f"Total banned users: {len(banned_users)}"})
    elif args[0] == "wtf!ban":
        # TODO: Implement this
        if env["MOD_ROLE_ID"] not in data["member"]["roles"]:
            route = typing.send_message(data["channel_id"])
            await bot.http.request(route, json={"content": "No access"})
            return


async def ban(user_id, reason, *, check_violated=None):
    # TODO: Implement this
    print(f"Banned {user_id} for {reason}. Check violated: {check_violated}")


async def do_check(check, check_name, data, *, check_type):
    user_id = data["owner"] if check_type == "pokemon" else data["_id"]
    if user_id in banned_users:
        return True
    try:
        is_okay = await check.execute(data)
    except Exception as e:
        print(f"Check {check_name} failed!")
        raise e
    if not is_okay:
        banned_users.append(user_id)
        await ban(user_id, "Automatic exploit detection", check_violated=check_name.upper())
    return is_okay


async def do_scan():
    this_wave = 0
    # User scans
    users = users_table.find({})

    for db_user in users:
        for check in user_checks:
            check_result = await do_check(check, check.check_id, db_user, check_type="user")
            if not check_result:
                # Check failed, user was banned
                this_wave += 1

bot.run()
