FROM python:3.11-slim

WORKDIR /app

COPY bot.py .

RUN pip install discord.py docker

CMD ["python", "bot.py"]