import discord

from discord.ext import commands
from discord import Color

from dotenv import dotenv_values

import argparse
import requests
import urllib.parse
import json
import time

import jumpstartdata as jsd

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

botCache = {}

#bot = discord.bot(intents=intents)
bot = commands.Bot(command_prefix=['!'], intents=intents) #command_prefix can be one item - i.e. '!' or a list - i.e. ['!','#','$']

listParser = argparse.ArgumentParser(prog='!list', description='Simple JumpStart List Query Command', epilog='Example(s):\n!list --set JMP TEFERI\n!list TEFERI', add_help=False, formatter_class=argparse.RawTextHelpFormatter)
listParser.add_argument('list', action='store')
listParser.add_argument('-s', '--set', choices=['ALL', 'JMP', 'J22', 'DMU', 'BRO', 'ONE', 'MOM', 'LTR'], default='ALL', action='store')
listParser.add_argument('-n', '--number', choices=['1', '2', '3', '4'], default=1, action='store') #might not want to default to 1 here, but think of a better way to handle this

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
                    
                #Get the list from GitHub or the cache
                cacheKey = f"{dataList['Set']}{dataList['Theme']}{dataList['Rarity']}{dataList['PrimaryColor']}{uniqueList}"
                if(cacheKey not in botCache):
                    url = f'https://raw.githubusercontent.com/tyraziel/MTG-JumpStart/main/etc/{urllib.parse.quote(dataList["Set"])}/{urllib.parse.quote(uniqueList)}.txt'
                    #await ctx.send(f"GITHUB PULL: {url}")
                    req = requests.get(url)
                    if(req.status_code == requests.codes.ok):
                        theListText = f'{req.text}'
                        #await ctx.send(f"CACHE CREATE: {cacheKey}")
                        botCache[cacheKey] = theListText
                    # else: #this would carry on and report not found if the list isn't found on the github
                    #     continue
                else:
                    #await ctx.send(f"CACHE HIT: {cacheKey}")
                    theListText = botCache[cacheKey]
                
                #Get the card image url from scryFall or the cache
                cacheKey = f"{dataList['Set']}{dataList['Theme']}"
                if(cacheKey not in botCache):
                    url = f"https://api.scryfall.com/cards/named?exact={urllib.parse.quote(dataList['Theme'])}&pretty=true&set={urllib.parse.quote(jsd.sets[dataList['Set']]['ScryfallFrontSetCode'])}"
                    req = requests.get(url)
                    if(req.status_code == requests.codes.ok):
                        scryFallResults = json.loads(req.text)
                        theListThemeCardImageUrl = scryFallResults["image_uris"]["small"]
                        botCache[cacheKey] = theListThemeCardImageUrl
                    else:
                        continue
                else:
                    theListThemeCardImageUrl = botCache[cacheKey]

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
        embed.set_footer(text=f'!list Query took {endTime - startTime}s')
        await ctx.send(embed=embed)
    else:
        await ctx.send(f'Unable to find a JumpStart list for {queryList} ({queryNumber}) in {querySet}')



@bot.command(aliases=['information', 'fancontent', 'fancontentpolicy'])
async def info(ctx):
    await ctx.send(content="This JumpStart Discord Bot is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.  https://company.wizards.com/en/legal/fancontentpolicy\n\nRandomization and distribution of packs/themes via this bot are based on observation, and guesswork, followed by iterations of testing, validation, refinement, observation and more guesswork.\n\nOther data and images furnished by https://api.scryfall.com/ (https://cards.scryfall.io) and https://static.wikia.nocookie.net/mtgsalvation_gamepedia/ (https://mtg.fandom.com/wiki/)", suppress_embeds=True)

bot.run(dev_env['BOT_TOKEN'])