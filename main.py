"""
Created by Epic at 9/17/20
"""
from speedcord import Client, http
from speedutils import typing
from os import environ as env
from pymongo import MongoClient
from checks.user import duplicated_pokemon_id_one_user

bot = Client(512, token=env["TOKEN"])
db_client = MongoClient(env["MONGO_URI"])
db = db_client.pokebot
users_table = db.users
pokemon_table = db.users_pokemoms

banned_users = []
user_checks = [duplicated_pokemon_id_one_user]

api = http.HttpClient("", baseuri="http://pokebotapi/api")
api.default_headers["Authorization"] = env["API_AUTH"]  # TODO: Change format to "Admin <token>"


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
    elif args[0] == "wtf!scan":
        if env["MOD_ROLE_ID"] not in data["member"]["roles"]:
            route = typing.send_message(data["channel_id"])
            await bot.http.request(route, json={"content": "No access"})
            return
        bans_this_wave = await do_scan()
        route = typing.send_message(data["channel_id"])
        await bot.http.request(route, json={"content": f"Scan done! Blocked users: {bans_this_wave}"})


async def ban(user_id, reason, *, check_violated=None, check_data=None):
    route = http.Route("GET", f"/bans/{user_id}")
    r = await api.request(route)
    if (await r.json())["banned"]:
        return
    print(f"Banned {user_id} for {reason}. Check violated: {check_violated}. Check data: {check_data}")
    route = http.Route("POST", f"/bans/{user_id}")
    await api.request(route, json={
        "reason": reason,
        "check_name": check_violated,
        "check_data": check_data
    })


async def do_check(check, check_name, data, *, check_type):
    user_id = data["owner"] if check_type == "pokemon" else data["_id"]
    if user_id in banned_users:
        return True
    try:
        is_okay, check_data = await check.execute(data)
    except Exception as e:
        print(f"Check {check_name} failed!")
        raise e
    if not is_okay:
        banned_users.append(user_id)
        await ban(user_id, "Automatic exploit detection", check_violated=check_name.upper(), check_data=check_data)
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

    return this_wave


bot.run()
