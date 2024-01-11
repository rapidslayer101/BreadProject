import discord
import os

subscribed_users = []  # List of user IDs that are subscribed to the bot


class BreadBot(discord.Client):

    async def on_ready(self):
        print(f"Logged on as {self.user}")

    async def on_message(self, message: discord.Message):
        if type(message.channel) is discord.DMChannel:

            if message.content.startswith("!subscribe"):
                if not message.author.id in subscribed_users:
                    subscribe_user(message.author.id)
                    await message.channel.send("You have subscribed to the BreadBot, W rizz my friend! :bread:")
                else:
                    await message.channel.send("You have already subscribed! :bread:")

            if message.content.startswith("!push") and message.author.id == 209612336275652608:  # Only Lewis' ID can push for now
                push_content = message.content.split("!push ")[1]
                for user_id in subscribed_users:
                    user = await self.fetch_user(user_id)
                    await user.send(push_content)


def subscribe_user(user_id):
    subscribed_users.append(user_id)
    with open("BotData/subscribed_users.txt", "a") as file:
        file.write(str(user_id) + "\n")


# Get token
with open("BotData/token.txt", "r") as file:
    token = file.read()

# Get subscribed users
with open("BotData/subscribed_users.txt", "a+") as file:
    content = file.readlines()
    for i in range(len(content)):
        subscribed_users.append(int(content[i].replace("\n", "")))

# Create client
intents = discord.Intents.default()
intents.message_content = True

client = BreadBot(intents=intents)
client.run(token)
