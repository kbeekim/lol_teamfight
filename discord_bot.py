import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import bot

game = discord.Game("안녕!")
bot = commands.Bot(command_prefix='!', status=discord.Status.online, activity=game)
client = discord.Client()


def test():
    for i in range(1000 * 1000):
        print("second_task :", i)

    @staticmethod
    async def discord_start(str):
        @bot.event
        async def on_ready():
            print(bot.user.name)
            print(bot.user.id)
            print("준비되었니!")

            # print(bot.get_channel(797080733478027266))
            channel = bot.get_channel(330322582366715904)

        # await channel.send("준비되었습니다")
        # snd_msg = await channel.send(str)
        # await asyncio.sleep(60)
        #
        # await snd_msg.delete()
        # await bot.close()

        # @bot.command(aliases=['hi', '안녕'])
        # async def hello(ctx):
        #     await ctx.send("안녕하세요")

        # @client.event
        # async def on_message(message):
        #     if message.author == bot.user:
        #         return
        #     await bot.send_message(client.channel, client.content)

        bot.run('OTY5NDIxNDQ2OTIzMjg4NTg2.YmtKEw.0zEOljmFW5kwmY7Vp093QxcD5bw')

# def discord_end():
