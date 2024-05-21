import discord
import logging
import sys
import traceback
import asyncio

# Configure logging to redirect outputs to discord channel, hopefully it's better for tracing errors on live testing
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Log errors
def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

sys.excepthook = log_exception

async def setup_discord_logging(client, channel_id):
    try:
        await client.wait_until_ready()
        channel = client.get_channel(int(channel_id))
        if channel is None:
            print("Failed to find the specified Discord channel for logging.")
            return

        sys.stdout = DiscordStream(channel)
        sys.stderr = DiscordStream(channel)

    except Exception as e:
        print("An error occurred during setup_discord_logging:", e)

    return


class DiscordStream:
    def __init__(self, channel):
        self.channel = channel
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    async def send_message(self, message):
        # Check if the message is empty or whitespace
        if not message.strip():  
            return

        try:
            # limit main message length to be max 1980 chars for any character limit issue
            await self.channel.send("```\n" + message[:1980] + "\n```")
        except discord.HTTPException as e:
            logger.error(f"Failed to send message to Discord: {e}")

    def write(self, message):
        # Send message to Discord
        asyncio.ensure_future(self.send_message(message))

    def flush(self):
        pass

