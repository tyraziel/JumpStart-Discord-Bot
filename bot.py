import discord

from discord.ext import commands
from discord import Color

from dotenv import dotenv_values

from PIL import Image
import io

import argparse
import requests
import urllib.parse
import json
import time
import random

import jumpstartdata as jsd

from bot_cache import BotCache

cliParser = argparse.ArgumentParser(prog='compleat_bot', description='JumpStart Compleat Bot', epilog='', add_help=False)
cliParser.add_argument('-e', '--env', choices=['DEV', 'PROD'], default='DEV', action='store')
cliArgs = cliParser.parse_args()

dev_env = dotenv_values(".devenv")
prod_env = dotenv_values(".prodenv")

bot_env = dev_env
if('PROD' == cliArgs.env.upper()):
    bot_env = prod_env
    print(f'THIS IS RUNNING IN PRODUCTION MODE AND WILL CONNECT TO PRODUCTION BOT TO THE MAIN JUMPSTART DISCORD SERVER')
else:
    print(f'This is running DEVELOPMENT MODE and the DEVELOPMENT bot will connect to your test server')

intents = discord.Intents.default()
intents.message_content = True

botCache = BotCache()

#bot = discord.bot(intents=intents)
bot = commands.Bot(command_prefix=['!'], intents=intents) #command_prefix can be one item - i.e. '!' or a list - i.e. ['!','#','$']

listParser = argparse.ArgumentParser(prog='!list', description='Simple JumpStart List Query Command', epilog='Example(s):\n!list --set JMP TEFERI\n!list TEFERI', add_help=False, formatter_class=argparse.RawTextHelpFormatter)
listParser.add_argument('list', action='store') #look into nargs so we don't have to "" the lists?  This would introduct string concatination on the list that's the result.
listParser.add_argument('-s', '--set', choices=['ALL', 'JMP', 'J22', 'DMU', 'BRO', 'ONE', 'MOM', 'LTR'], default='ALL', action='store')
listParser.add_argument('-n', '--number', choices=['1', '2', '3', '4'], default=1, action='store') #might not want to default to 1 here, but think of a better way to handle this

pickParser = argparse.ArgumentParser(prog='!pick', description='Pick n Random JumpStart Packs Command', epilog='Example(s):\n!pick --set JMP \n!p3 --set J22\n!p3 --set J22 --type themes', add_help=False, formatter_class=argparse.RawTextHelpFormatter)
pickParser.add_argument('-n', '--number', choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], default=3, action='store')
pickParser.add_argument('-s', '--set', choices=['ALL', 'JMP', 'J22', 'DMU', 'BRO', 'ONE', 'MOM', 'LTR'], default='JMP', action='store')
pickParser.add_argument('-t', '--type', choices=['themes', 'THEMES', 'Themes', 't', 'T', 'lists', 'LISTS', 'l', 'L', "Lists"], default='themes', action='store')
pickParser.add_argument('--nodupes', action='store_true')
#MRCUS - rarity

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="JumpStart Lo-Fi"))
    print(f'We have logged in as {bot.user} with status {bot.status} and activity {bot.activity}')
    print(f'{jsd.jumpstart}')

#using @bot.listen() will listen for messages, but will continue processing commands, so having the await bot.process_commands(message) when this is set with @bot.listen() decorator it will fire the command twice.
@bot.event  
async def on_message(message):

    # print(f'{message.created_at}, Guild: {message.guild}, Channel: {message.channel}, Author: {message.author}, Message: {message.content}')

    if message.author == bot.user: #avoid infinite loops
        return
    if message.channel.name != 'bot-testing': #only allow processing of messages in the bot-testing channel
        return

    await bot.process_commands(message) #this will continue processing to allow commands to fire.

# @bot.command()
# async def ping(ctx, hidden=True):
#     await ctx.send("pong")
#     print(f'User Roles for ping: {ctx.author.roles}')

# @bot.command(name='test', hidden=True)
# async def test(ctx, arg):
#     await ctx.send(arg)

#This will bring args as a list of strings
# @bot.command(name='testmultiargs', hidden=True)
# async def test(ctx, *args):
#     await ctx.send(args)

@bot.command(name='pick', aliases=['mtga', 'pickem', 'pick3', 'p3'])
async def pick(ctx, *args):
    startTime = time.time()

    try:
        pickArgs = pickParser.parse_args(args)

        pickSet = pickArgs.set.upper()
        pickNumber = int(pickArgs.number)
        pickType = pickArgs.type.upper()[0]
        pickDupes = not pickArgs.nodupes

        imagesToConcatenate = []

        packPopulation = []

        for dataList in jsd.jumpstart:
            if(dataList['Set'] == pickSet or "ALL" == pickSet):
                if(pickType == 'T'):
                    packPopulation.append({'Theme': dataList['Theme'], 'List': dataList['Theme'], 'Set': dataList['Set']})
                else:
                    numberOfLists = 1

                    if(dataList['Rarity'] == 'R' or dataList['Rarity'] == 'S'):
                        numberOfLists = 2
                    elif(dataList['Rarity'] == 'C'):
                        numberOfLists = 4

                    if numberOfLists == 1:
                        packPopulation.append({'Theme': dataList['Theme'], 'List': f"{dataList['Theme']}", 'Set': dataList['Set']})
                    else:
                        for x in range(1,numberOfLists+1):
                            packPopulation.append({'Theme': dataList['Theme'], 'List': f"{dataList['Theme']} ({x})", 'Set': dataList['Set']})

        #random.choices(population, k=#) #pick with replacement (aka can have dupes)
        #random.sample(population, counts=[], k=#) #counts=[] could be interesting here, but we'll avoid it for now

        selectionThemes = ["ELVES", "GOBLINS", "TEFERI", "BASRI", "TREE-HUGGING", "SMASHING", "FEATHERED FRIENDS", "VAMPIRES", "DRAGONS", "ROGUES"]
        selections = []
        if(pickDupes):
            selections = random.choices(packPopulation, k=pickNumber)
        else:
            selections = random.sample(packPopulation, k=pickNumber)

        resultText = ""

        for x in range(0, pickNumber):
            imagesToConcatenate.append(botCache.fetchThemeImageWithCacheScryfallCardImage(selections[x]['Set'], selections[x]['Theme']))
            resultText = f"{resultText}{selections[x]['List']}\n"

        pickListImage = Image.new('RGBA', (imagesToConcatenate[0].width * pickNumber, imagesToConcatenate[0].height))

        for i in range(0, len(imagesToConcatenate)):
            pickListImage.paste(imagesToConcatenate[i], (imagesToConcatenate[0].width*i, 0))

        with io.BytesIO(pickListImage.tobytes()) as image_binary:
            pickListImage.save(image_binary, 'PNG')
            image_binary.seek(0)
            endTime = time.time()

            embed = discord.Embed(title=f'Pick {pickNumber} Results', color=Color.dark_purple()) #can also have url, description, color
            if(pickSet != 'ALL'):
                embed.set_author(name=jsd.sets[pickSet]['Name'], icon_url=jsd.sets[pickSet]['SetIconImageUrl'])
            
            embed.add_field(name="", value=resultText, inline=False)

            #Once the data is re-worked it would make more sense to categorize the cards as their main types
            #embed.add_field(name="Planeswalkers", value="1 PW1\n1 PW2", inline=True)
            #embed.add_field(name="Creatures", value="1 Creature1\n1 Creature2\n2 Creature3", inline=True)
            #embed.add_field(name="Sorceries", value="1 Sorcery1\n1 Sorcery2\n1 Sorcery3\n1 Sorcery4", inline=True)
            #embed.add_field(name="Instants", value="1 Instant1", inline=True)
            #embed.add_field(name="Artifacts", value="1 Artifact1\n1 Artifact2", inline=True)
            #embed.add_field(name="Enchantments", value="1 Enchantment1\n1 Enchantment2\n1 Enchantment3", inline=True)
            #embed.add_field(name="Lands", value="1 Land1\n6 Land2\n1 Land3", inline=True)
            embed.set_footer(text=f'!pick call took {endTime - startTime:.5f}s')

            await ctx.send(file=discord.File(fp=image_binary, filename='image.png'), embed=embed)
    except SystemExit as e: #SystemExit is the exception raised by parse_args when there's issues
        await ctx.send(f'Your command was invalid.\n\n{pickParser.format_help()}')

@bot.command(name='list', aliases=[])
async def list(ctx, *args):

    startTime = time.time()
    
    theListText = ""
    theListName = ""
    theListSet = ""
    theListFound = False
    theListColor = Color.magenta()
    theListThemeCardImageUrl = ""
    findCount = 0

    try:
        listArgs = listParser.parse_args(args)

        queryList = listArgs.list.upper()
        querySet = listArgs.set.upper()
        queryNumber = int(listArgs.number)
        
        for dataList in jsd.jumpstart:
            if((dataList['Set'] == querySet or "ALL" == querySet) and dataList['Theme'] == queryList):
                findCount =+ findCount
                #await ctx.send(f"FOUND VALID DATA: Set={dataList['Set']} Theme={dataList['Theme']} Rarity={dataList['Rarity']} PrimaryColor={dataList['PrimaryColor']}")
                
                uniqueList = queryList

                #if the rarity is R, C or S and the user didn't pass in a number, the number 1 is assumed
                if((dataList['Rarity'] == 'R' and queryNumber < 3) or (dataList['Rarity'] == 'C') or (dataList['Rarity'] == 'S' and queryNumber < 3)):
                    uniqueList = f"{uniqueList} ({queryNumber})"
                    
                theListText = botCache.fetchWithCacheGitHubList(dataList['Set'], uniqueList)

                theListThemeCardImageUrl = botCache.fetchThemeImageURLWithCacheScryfallCardJSONURL(dataList['Set'], dataList['Theme'])

                #Figure out color for the side of the embed
                if(dataList['PrimaryColor'] == "W"):
                    theListColor = Color.light_grey()
                elif(dataList['PrimaryColor'] == "U"):
                    theListColor = Color.blue()
                elif(dataList['PrimaryColor'] == "B"):
                    theListColor = Color.darker_grey()
                elif(dataList['PrimaryColor'] == "R"):
                    theListColor = Color.red()
                elif(dataList['PrimaryColor'] == "G"):
                    theListColor = Color.green()
                elif(dataList['PrimaryColor'] == "M"):
                    theListColor = Color.gold()
                elif(dataList['PrimaryColor'] == "N"):
                    theListColor = Color.dark_grey()

                theListFound = True
                theListName = uniqueList
                theListSet = dataList['Set']
                #break
            #else:
            #   await ctx.send(f"({dataList['Set']} == {querySet} or {'ALL'} == {querySet}) and {dataList['Theme']} == {queryList} -- FALSE")

    except SystemExit as e: #SystemExit is the exception raised by parse_args when there's issues
        await ctx.send(f'Your command was invalid.\n\n{listParser.format_help()}')

    endTime = time.time()
    if(theListFound):
        embed = discord.Embed(title=theListName, color=theListColor) #can also have url, description, color
        embed.set_author(name=jsd.sets[theListSet]['Name'], icon_url=jsd.sets[theListSet]['SetIconImageUrl'])
        embed.set_thumbnail(url=theListThemeCardImageUrl)
        embed.add_field(name="", value=theListText, inline=False)

        #Once the data is re-worked it would make more sense to categorize the cards as their main types
        #embed.add_field(name="Planeswalkers", value="1 PW1\n1 PW2", inline=True)
        #embed.add_field(name="Creatures", value="1 Creature1\n1 Creature2\n2 Creature3", inline=True)
        #embed.add_field(name="Sorceries", value="1 Sorcery1\n1 Sorcery2\n1 Sorcery3\n1 Sorcery4", inline=True)
        #embed.add_field(name="Instants", value="1 Instant1", inline=True)
        #embed.add_field(name="Artifacts", value="1 Artifact1\n1 Artifact2", inline=True)
        #embed.add_field(name="Enchantments", value="1 Enchantment1\n1 Enchantment2\n1 Enchantment3", inline=True)
        #embed.add_field(name="Lands", value="1 Land1\n6 Land2\n1 Land3", inline=True)
        embed.set_footer(text=f'!list Query took {endTime - startTime:.5f}s')
        await ctx.send(embed=embed)
    else:
        await ctx.send(f'Unable to find a JumpStart list for {queryList} ({queryNumber}) in {querySet}')

@bot.command(name='stats', aliases=[])
async def statistics(ctx, *args):
    await ctx.send(content=str(botCache), suppress_embeds=True)

@bot.command(aliases=['information', 'fancontent', 'fancontentpolicy', 'license'])
async def info(ctx):
    await ctx.send(content="Compleat JumpStart Bot v0.1.0-beta\n\nThis JumpStart Discord Bot is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.  https://company.wizards.com/en/legal/fancontentpolicy\n\nRandomization and distribution of packs/themes via this bot are based on observation, and guesswork, followed by iterations of testing, validation, refinement, observation and more guesswork.\n\nOther data and images furnished by https://api.scryfall.com/ (https://cards.scryfall.io) and https://static.wikia.nocookie.net/mtgsalvation_gamepedia/ (https://mtg.fandom.com/wiki/)\n\nSource Code is released under the MIT License https://github.com/tyraziel/JumpStart-Discord-Bot/ -- 2023", suppress_embeds=True)

bot.run(bot_env['BOT_TOKEN'])