import discord
import docker
import os
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Load environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
server_name = os.getenv("DOCKER_SERVER_NAME", "Docker")

# Initialize Discord and Docker clients
intents = discord.Intents.default()
client = discord.Client(intents=intents)
docker_client = docker.from_env()

# Generate a Discord embed with container status
def get_status_embed():
    embed = discord.Embed(
        title=f"{server_name} Docker Container Status"
    )

    name_width = 26
    status_width = 8
    details_pad = 10

    header = f"{'Name':<{name_width}} {'Status':>{status_width}} {' Details':<{details_pad}}"
    divider = "-" * len(header)

    lines = [header, divider]
    fields = []

    for container in docker_client.containers.list(all=True):
        name = container.name[:name_width - 2]
        status = "Running" if container.status == "running" else "Stopped"
        details = ""

        if container.status != "running":
            state = container.attrs.get("State", {})
            exit_code = state.get("ExitCode", "N/A")
            error = state.get("Error", "")
            oom = "OOMKilled" if state.get("OOMKilled") else ""

            details = f"Exit {exit_code}"
            if error:
                details += f" — {error}"
            if oom:
                details += f" — {oom}"

        emoji = "🟢" if container.status == "running" else "🔴"
        line = f"{emoji} {name:<{name_width - 2}} {status:>{status_width}} {details}"
        lines.append(line)

        # If the current chunk is getting too long, flush it
        if sum(len(l) + 1 for l in lines) > 900:
            fields.append("\n".join(lines))
            lines = [header, divider]

    # Add any remaining lines
    if len(lines) > 2:
        fields.append("\n".join(lines))

    # Add each chunk as a separate field
    for chunk in fields:
        embed.add_field(name="", value=f"```{chunk}```", inline=False)

    return embed

# Triggered when the bot successfully connects to Discord
@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)

    # Look for pinned messages that start with this server's name
    pinned = [
        msg async for msg in channel.pins()
        if msg.author == client.user and msg.embeds and msg.embeds[0].title.startswith(f"{server_name}")
    ]
    pinned_message = pinned[0] if pinned else None

    last_status = None  # Track last known container status

    # Main loop: check container status every 10 seconds
    while True:
        new_embed = get_status_embed()
        new_status_str = "\n".join(f"{f.name}: {f.value}" for f in new_embed.fields)

        if new_status_str != last_status:
            logging.info("Container status changed — updating message")
            if pinned_message:
                await pinned_message.edit(embed=new_embed)
            else:
                pinned_message = await channel.send(embed=new_embed)
                await pinned_message.pin()
                logging.info("Created and pinned new message")
            last_status = new_status_str
        else:
            logging.info("No change in container status — skipping update")

        await asyncio.sleep(10)

# Start the bot using the provided bot token
client.run(TOKEN)
