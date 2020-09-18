"""
Created by Epic at 9/17/20
"""
from os import environ as env
from time import sleep, perf_counter
from pymongo import MongoClient
from logging import DEBUG, WARNING
from discord import RequestsWebhookAdapter, Webhook, Embed

LOGGING_WEBHOOK_URL = env["WEBHOOK_URL"]
MONGO_URI = env["MONGO_URI"]
CHECK_INTERVAL = int(env["CHECK_INTERVAL"])

# Webhook stuff
webhook = Webhook.from_url(LOGGING_WEBHOOK_URL, adapter=RequestsWebhookAdapter())

# Logging
cache = []


def alert(level, message):
    if level == DEBUG:
        print(message)
    elif level == WARNING:
        # Send to discord thingy
        embed = Embed(title="(!) Alert", description=message, color=0xFFFF00)
        cache.append(embed)
    else:
        raise TypeError("Please only use debug and warning")


def fail_check(check_name, user_id):
    print(f"{user_id} failed {check_name}")
    IGNORE_LIST.append(user_id)
    alert(WARNING, f"<@{user_id}> failed check `{check_name}`")


def block_user(user_id: int):
    # TODO: Implement this
    pass


# Database stuff
mongo = MongoClient(MONGO_URI)
db = mongo.pokebot
user_table = db.users
pokemons_table = db.users_pokemons

# Data lookups
IGNORE_LIST = []  # TODO: Make this automatically save and read from a table


def do_user_check():
    user_id = user["_id"]
    print(IGNORE_LIST)
    print(user_id)
    if user_id in IGNORE_LIST:
        return
    pokemon_ids = user["pokemons"]
    if len(set(pokemon_ids)) != len(pokemon_ids):
        fail_check("SAME_POKEMON_ID_USER", user_id)


def clear_webhook_cache():
    new = cache.copy()
    while True:
        if len(new) >= 10:
            to_send = [new.pop(0) for i in range(10)]
            webhook.send(embeds=to_send)
            continue
        elif len(new) != 0:
            to_send = []
            for embed in new:
                to_send.append(embed)
            webhook.send(embeds=to_send)
            return
        return


while True:
    start_time = perf_counter()
    users = list(user_table.find())
    for user in users:
        do_user_check()
    end_time = perf_counter()
    print(f"Scan took {end_time - start_time}s")

    # Clear out webhook cache
    clear_webhook_cache()

    sleep(CHECK_INTERVAL)
