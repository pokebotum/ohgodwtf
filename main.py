"""
Created by Epic at 9/17/20
"""
from speedcord import Client
from speedutils import typing
from os import environ as env

bot = Client(512, token=env["TOKEN"])

banned_users = []


@bot.listen("MESSAGE_CREATE")
async def on_message(data, shard):
    args = data["content"].lower().split(" ")
    if args[0] == "wtf!status":
        route = typing.send_message(data["channel_id"])
        await bot.http.request(route, json={"content": f"Total banned users: {len(banned_users)}"})
    elif args[0] == "wtf!ban":
        if env["MOD_ROLE_ID"] not in data["member"]["roles"]:
            route = typing.send_message(data["channel_id"])
            await bot.http.request(route, json={"content": "No access"})
            return


bot.run()
