"""
Created by Epic at 9/18/20
"""
from speedcord.http import Route


def send_message(channel_id):
    return Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id)
