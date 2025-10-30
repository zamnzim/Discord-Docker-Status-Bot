# DiscordBot-Docker-Status
A lightweight Python based Discord bot that that runs in a docker container, monitors Docker containers, and posts their status to a pinned message in a specified Discord channel.

Every 10 seconds, the bot checks the status of all containers. If any changes are detected, it updates the pinned message with the current status.

This bot is designed for multi-server deployments. Each instance identifies its own pinned message using a unique server name (```DOCKER_SERVER_NAME```) and updates only the message associated with the server it’s running on. This allows multiple servers to report to the same Discord channel without interference.

![Example Running](https://github.com/user-attachments/assets/048d22fd-ecf6-4afa-b088-2dfbded9d404)

# Environment Variables

| Variable | Dscription |
| -------- | ---------- |
| DISCORD_TOKEN | Your Discord bot token. |
| DISCORD_CHANNEL_ID | The ID of the Discord channel where the bot will post status updates in. |
| DOCKER_SERVER_NAME | A unique name for the server. Used to distinguish pinned messages per host. Defaults to ```"Docker"```. |

# Docker Run
```
docker run -d \
  --name discordbot-docker-status \
  --restart unless-stopped \
  -e DISCORD_TOKEN=your_discord_bot_token_here \
  -e DISCORD_CHANNEL_ID=your_channel_id_here \
  -e DOCKER_SERVER_NAME=your_server_name_here \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  ghcr.io/zamnzim/discordbot-docker-status:latest
```
# Docker Compose
```yaml
services:
  discordbot-docker-status:
    image: ghcr.io/zamnzim/discord-docker-status-bot:latest
    container_name: discordbot-docker-status
    restart: unless-stopped
    environment:
      - DISCORD_TOKEN=your_discord_bot_token_here
      - DISCORD_CHANNEL_ID=your_channel_id_here
      - DOCKER_SERVER_NAME=your_server_name_here
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```
