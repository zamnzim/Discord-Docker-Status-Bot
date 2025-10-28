# Discord-Docker-Status-Bot
Simple discord bot written in python.

The bot will pull the status of containers and pin the status to a chosen chat. Every 10s the docker containers are checked for changes. If any changes occur to the containers, the pinned message is edited and replaced with the current status.

![Example Running](https://github.com/user-attachments/assets/74962c43-742a-4fbb-a9d1-6804a5420c42)

# Docker Run
```
docker run -d \
  --name discord-docker-status-bot \
  --restart unless-stopped \
  -e DISCORD_TOKEN=your_discord_bot_token_here \
  -e DISCORD_CHANNEL_ID=your_channel_id_here \
  -e DOCKER_SERVER_NAME=your_server_name_here \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  ghcr.io/zamnzim/discord-docker-status-bot:latest
```
# Docker Compose
```yaml
services:
  discord-docker-status-bot:
    image: ghcr.io/zamnzim/discord-docker-status-bot:latest
    container_name: discord-docker-status-bot
    restart: unless-stopped
    environment:
      - DISCORD_TOKEN=your_discord_bot_token_here
      - DISCORD_CHANNEL_ID=your_channel_id_here
      - DOCKER_SERVER_NAME=your_server_name_her
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```