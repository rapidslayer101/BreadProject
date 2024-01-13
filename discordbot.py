import discord
import os

subscribed_users = []  # List of user IDs that are subscribed to the bot


def subscribe_user(user_id):
    subscribed_users.append(user_id)
    with open("BotData/subscribed_users.txt", "a") as f:
        f.write(f"{user_id}\n")


# Get token
with open("BotData/token.txt", "r") as f:
    token = f.read()

# Get subscribed users
with open("BotData/subscribed_users.txt", "a+") as f:
    content = f.readlines()
    for i in range(len(content)):
        subscribed_users.append(int(content[i].replace("\n", "")))


class BreadBot(discord.Client):

    async def on_ready(self):
        print(f"Logged on as {self.user}")

    async def on_message(self, message: discord.Message):
        if type(message.channel) is discord.DMChannel:

            if message.content.startswith("!subscribe"):
                if message.author.id not in subscribed_users:
                    subscribe_user(message.author.id)
                    await message.channel.send("You have subscribed to the BreadBot, W rizz my friend! :bread:")
                else:
                    await message.channel.send("You have already subscribed! :bread:")

            if message.content.startswith("!push") and message.author.id == 209612336275652608:  # Only Lewis' ID can push for now
                push_content = message.content.split("!push ")[1]
                for user_id in subscribed_users:
                    user = await self.fetch_user(user_id)
                    await user.send(push_content)


# Create client
intents = discord.Intents.default()
intents.message_content = True

client = BreadBot(intents=intents)
client.run(token)
