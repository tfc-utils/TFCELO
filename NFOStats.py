import socket
import discord
from discord.ext import commands
import json
import logging
import asyncio
import select

intents = discord.Intents.all()
client = commands.Bot(
    command_prefix=["!", "+", "-"], case_insensitive=True, intents=intents
)

UDP_IP_ADDRESS = "0.0.0.0"
UDP_PORT_NO = 6789
DM_CHANNEL_ID = 1230852204567597186

# Create UDP socket
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
serverSock.setblocking(False)  # Make socket non-blocking

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

with open("login.json") as f:
    logins = json.load(f)
with open("variables.json") as f:
    v = json.load(f)

async def process_match_data(data):
    if "[MATCH RESULT]" in str(data):
        with open("activePickups.json") as f:
            activePickups = json.load(f)
        string = str(data)
        begin = string.find("<") + 1
        end = string.find(">")
        winningScore = string[begin:end]
        begin = string.find("(") + 1
        end = string.find(")")
        losingScore = string[begin:end]
        final_part = string[string.find(")") + 2:].split(" ")
        region = final_part[0]
        map = final_part[1][:-7]

        if losingScore == "0":
            print("Ignoring match result due to 0")
        else:
            if len(activePickups) > 0:
                logging.info(str(activePickups))
                reported_match = None
                for game in activePickups:
                    if map == activePickups[game][7]:
                        logging.info(f"Found match {game} for map {map}")
                        reported_match = game
                        break
                if reported_match is None:
                    logging.info("No match found for map, using most recent match")
                    reported_match = list(activePickups)[-1]
                
                pChannel = await client.fetch_channel(v["pID"])
                if "Team 1 Wins" in (str(data)):
                    await pChannel.send(f"!win 1 {reported_match}")
                    await asyncio.sleep(0.5)  # Add delay between messages
                    await pChannel.send(
                        f"**AUTO-REPORTING** Team 1 wins {winningScore} to {losingScore} for game {reported_match}"
                    )
                    await asyncio.sleep(0.5)  # Add delay between messages
                    await pChannel.send(
                        f"!stats {region.lower()} {reported_match} {winningScore} {losingScore}"
                    )
                elif "Team 2 Wins" in (str(data)):
                    await pChannel.send(f"!win 2 {reported_match}")
                    await asyncio.sleep(0.5)  # Add delay between messages
                    await pChannel.send(
                        f"**AUTO-REPORTING** Team 2 wins {winningScore} to {losingScore} for game {reported_match}"
                    )
                    await asyncio.sleep(0.5)  # Add delay between messages
                    await pChannel.send(
                        f"!stats {region.lower()} {reported_match} {winningScore} {losingScore}"
                    )
                elif "DRAW" in (str(data)):
                    await pChannel.send(f"!draw {reported_match}")
                    await asyncio.sleep(0.5)  # Add delay between messages
                    await pChannel.send(f"**AUTO-REPORTING** DRAW at {losingScore} for game {reported_match}")
                    await asyncio.sleep(0.5)  # Add delay between messages
                    await pChannel.send(
                        f"!stats {region.lower()} {reported_match} {losingScore}"
                    )
            else:
                print("!! NO ACTIVE PICKUPS!")

    if "[1v1 MATCH RESULT]" in str(data):
        with open("active_1v1_matches.json", "r") as f:
            active_1v1_matches = json.load(f)
        if len(active_1v1_matches) > 0:
            reported_1v1_match = list(active_1v1_matches)[-1]
            dm_channel = await client.fetch_channel(DM_CHANNEL_ID)
            if "Team 1 Wins" in (str(data)):
                await dm_channel.send("!win1v1 1")
                await asyncio.sleep(0.5)  # Add delay between messages
                await dm_channel.send(
                    f"**AUTO-REPORTING** Team 1 wins {reported_1v1_match}"
                )
            elif "Team 2 Wins" in (str(data)):
                await dm_channel.send("!win1v1 2")
                await asyncio.sleep(0.5)  # Add delay between messages
                await dm_channel.send(
                    f"**AUTO-REPORTING** Team 2 wins {reported_1v1_match}"
                )
            await asyncio.sleep(0.5)  # Add delay before final message
            await dm_channel.send("!stats1v1")

async def socket_listener():
    while True:
        try:
            readable, _, _ = select.select([serverSock], [], [], 0.1)
            if serverSock in readable:
                data, addr = serverSock.recvfrom(1024)
                logging.info(str(data))
                await process_match_data(data)
            await asyncio.sleep(0.1)
        except Exception as e:
            logging.error(f"Error in socket listener: {e}")
            await asyncio.sleep(1)

@client.event
async def on_ready():
    logging.info("Auto Report Starting!")
    client.loop.create_task(socket_listener())

client.run(v["TOKEN"])
