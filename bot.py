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

# Generate a formatted status message for all containers
def get_status_text():
    lines = [f"📦 **{server_name} Docker Container Status**\n"]
    for container in docker_client.containers.list(all=True):
        # Choose emoji based on container status
        emoji = "🟢" if container.status == "running" else "🔴"
        status = "**Running**" if container.status == "running" else "**Stopped**"

        # If container is stopped, append diagnostic info
        if container.status != "running":
            state = container.attrs.get("State", {})
            exit_code = state.get("ExitCode", "N/A")
            error = state.get("Error", "")
            oom = "OOMKilled" if state.get("OOMKilled") else ""

            # Build reason string with exit code, error, and OOM status
            reason = f"(Exit {exit_code})"
            if error:
                reason += f" — {error}"
            if oom:
                reason += f" — {oom}"
            status += f" {reason}"

        # Add container line to message
        lines.append(f"{emoji} `{container.name}` — {status}")
        
    # Return full message as a single string
    return "\n".join(lines)

# Triggered when the bot successfully connects to Discord
@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)

    # Look for pinned messages that start with this server's name
    pinned = [
        msg async for msg in channel.pins()
        if msg.author == client.user and msg.content.startswith(f"📦 **{server_name}")
    ]
    pinned_message = pinned[0] if pinned else None # Use first match or None

    last_status = None # Track last known container status

    # Main loop: check container status every 10 seconds
    while True:
        new_status = get_status_text()

        # If status has changed, update the pinned message
        if new_status != last_status:
            logging.info("Container status changed — updating message")
            if pinned_message:
                # Edit existing pinned message
                await pinned_message.edit(content=new_status)
            else:
                # Send and pin a new message
                pinned_message = await channel.send(new_status)
                await pinned_message.pin()
                logging.info("Created and pinned new message")
            last_status = new_status # Update last known status
        else:
            logging.info("No change in container status — skipping update")

        await asyncio.sleep(10)  # Check every 10 seconds

# Start the bot using the provided bot token
client.run(TOKEN)
