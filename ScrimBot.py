#scrim - bot.py

#id of scrim-announcments = 726194169537757184
#id of scrim-setups = 726529754785775626

import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
import time
import datetime
import json
import sys
from dotenv import load_dotenv

load_dotenv("/home/pi/bots/.env")
TOKEN = os.getenv('SCRIM_BOT')
print (TOKEN)

ANNOUNCMENT_ID = 726194169537757184
SETUP_ID = 726529754785775626
SCRIM_INFO = 728610912675692585
TRIAL_ID = 730760392007221299
infoFile = os.getenv('ROSTER_STATS_PATH')
trialFile = os.getenv('TRIAL_STATS_PATH')
commandsFile = os.getenv('COMMANDS_PATH')

PREFIX = 's!'
bot = commands.Bot(command_prefix=PREFIX)
client = discord.Client()


scrimTime = 0
doneOneHr = False
doneHalfHr = False
doneTenMin = False
pingCoach = False
currentTime = 0
mostRecentInfo = 0
maps = ['Not', 'Set']

with open(commandsFile,'r') as f:
	commandList = f.read()
print (commandList)

def toTime (hours, minutes, seconds):
	return datetime.timedelta(0,seconds,0,0,minutes,hours)
	
async def sendScrimInfo():
	global maps
	global scrimTime
	global pingCoach
	channel = bot.get_channel(SETUP_ID)
	await channel.purge()
	if scrimTime != 0:
		await channel.send(f"> __**Commands**__\n{commandList}\n\n> __**Current**__\n**Scrim Time**: {scrimTime.time()} on {scrimTime.day}-{scrimTime.month}-{scrimTime.year}\n\n**Maps**: {', '.join(maps)}\n\n**Ping Coach**: {pingCoach}")
	else:
		await channel.send(f"> __**Commands**__\n{commandList}\n\n> __**Current**__\n**Scrim Time**: Not Set\n\n**Maps**: {','.join(maps)}\n\n**Ping Coach**: {pingCoach}")
@bot.event
async def on_ready():
	global maps
	maps = ['Not', 'Set']
	print ("Logged on as:")
	print (bot.user.name)
	print (bot.user.id)
	print ("----------")
	await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"ELTDA | {PREFIX}helpme"))
	checktime.start()
	checkForScrim.start()
	await sendScrimInfo()
	
@tasks.loop(seconds=20)
async def checktime():
	global currentTime
	currentTime = datetime.datetime.now()

@tasks.loop(seconds=20)
async def checkForScrim():
	global currentTime
	global doneOneHr
	global doneHalfHr
	global maps
	global scrimTime
	global pingCoach
	print (f"Checking For Scrim at {currentTime}")
	if scrimTime != 0:
		beforeScrim = scrimTime - currentTime
		if beforeScrim < toTime(1,5,0) and beforeScrim > toTime(0,55,0) and doneOneHr == False:
			print ("1 Hour")
			channel = bot.get_channel(ANNOUNCMENT_ID)
			await channel.send(f"<@&726192849191829686> Scrim in ~1Hr! | Maps are {', '.join(str(x) for x in maps)}")
			doneOneHr = True
			if pingCoach:
				await channel.send(f"<@&726193012371357698>! The roster is requesting your presence for the scrim in {beforeScrim}")
		if beforeScrim < toTime(0,35,0) and beforeScrim > toTime(0,25,0) and doneHalfHr == False:
			print ("30 Min")
			channel = bot.get_channel(ANNOUNCMENT_ID)
			await channel.send(f"<@&726192849191829686> Scrim in ~30 Min! | Maps are {', '.join(str(x) for x in maps)}")
			doneHalfHr = True
			if pingCoach:
				await channel.send(f"<@&726193012371357698>! The roster is requesting your presence for the scrim in {beforeScrim}")
		if beforeScrim < toTime(0,5,0) and beforeScrim > toTime(0,0,0):
			print ("Scrim Time")
			channel = bot.get_channel(ANNOUNCMENT_ID)
			await channel.send(f"<@&726192849191829686> Scrim Time BOOYYYSS | Maps are {', '.join(str(x) for x in maps)}")
			if pingCoach:
				await channel.send(f"<@&726193012371357698>! The roster is requesting your presence for the scrim in {beforeScrim}")
			doneHalfHr = False
			doneOneHour = False
			maps = ['Not','Set']
			pingCoach = False
			msgs = []
			if scrimTime < currentTime + toTime(0,5,0):
				scrimTime = 0
				await bot.get_channel(ANNOUNCMENT_ID).purge()
			print ("RESET")
				
	
@bot.command()
async def helpme(ctx):
	print (f"{ctx.author.name} called helpme()")
	channel = bot.get_channel(SETUP_ID)
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		await ctx.message.delete()
		await channel.send(commandList)
		print (commandList)
		print (f"This server is: {ctx.message.guild.name}")

@bot.command()
async def time(ctx, message):
	global scrimTime
	print (f"{ctx.author.name} called settime()")
	channel = bot.get_channel(SETUP_ID)
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		messageArray = message.split(":")
		print (messageArray)
		hours = int(messageArray[0])
		minutes = int(messageArray[1])
		try:
			day = int(messageArray[2])
		except:
			now = datetime.datetime.now()
			day = now.day
		try:
			month = int(messageArray[3])
		except:
			now = datetime.datetime.now()
			month = now.month
		try:
			year = int(messageArray[4])
		except:
			now = datetime.datetime.now()
			year = now.year
		if len(str(year)) == 2:
			year = 2000 + year
		scrimTime = datetime.time(hours,minutes)
		scrimTime = datetime.datetime.combine(datetime.date(year,month,day), scrimTime)
		await ctx.message.delete()
		await sendScrimInfo()
		
@bot.command()
async def pingcoach(ctx):
	global pingCoach
	print (f"{ctx.author.name} called pingcoach()")
	channel = bot.get_channel(SETUP_ID)
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		pingCoach = not pingCoach
		await sendScrimInfo()
		print (pingCoach)
		
@bot.command()
async def maps(ctx, *message):
	print (f"{ctx.author.name} called setmaps()")
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	global maps
	maps = message
	channel = bot.get_channel(SETUP_ID)
	await ctx.message.delete()
	await sendScrimInfo()
	print (maps)
	
	
@bot.command()
async def ping(ctx):
	print (f"{ctx.author.name} called ping()")
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	global maps
	try:
		beforeScrim = (scrimTime - currentTime)
	except:
		beforeScrim = "No time Set"
	await ctx.message.delete()
	channel = bot.get_channel(ANNOUNCMENT_ID)
	mentions = []
	for mention in ctx.message.mentions:
		mentions.append(mention.mention)
	if len(mentions) == 0:
		mentions.append(ctx.author.mention)
	try:
		await channel.send(f"{' '.join(mentions)} Scrim Time in **{beforeScrim.days}**days **{beforeScrim.seconds//3600}**hrs **{(beforeScrim.seconds%3600)//60}**min **{((beforeScrim.seconds%3600)%60)}**seconds | Maps are **{', '.join(str(x) for x in maps)}**")
	except:
		await channel.send(f"{' '.join(mentions)} **No Time set** | Maps are **{', '.join(str(x) for x in maps)}**")

	
@bot.command()
async def scrimresult(ctx, roundsWon, roundsLost):
	print (f"{ctx.author.name} called scrimresult()")
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	roundsWon = int(roundsWon)
	roundsLost = int(roundsLost)
	try:
		if roundsWon>roundsLost:
			won = True
		elif roundsWon<roundsLost:
			won = False
		else:
			won = None
	except:
		won = None
	with open(infoFile,"r") as read_file:
		data = json.load(read_file)
		for p in data['info']:
			if won == None:
				print("DREW")
			elif won:
				p['wins'] = p['wins']+1
			elif not won:
				p['losses'] = p['losses']+1
			p['rwins'] = p['rwins'] + roundsWon
			p['rlosses'] = p['rlosses'] + roundsLost
	with open(infoFile,"w") as write_file:
		json.dump(data, write_file)
	await info(ctx)
	
				
@bot.command()
async def exit(ctx):
	print (f"{ctx.author.name} called exit()")
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	await ctx.message.delete()
	await bot.change_presence(status=discord.Status.idle, activity=discord.Game(f"Exited"))
	sys.exit()
	
@bot.command()
async def info(ctx):
	global currentTime
	global trialOneName
	global trialTwoName
	global trialThreeName
	print (f"{ctx.author.name} called info()")
	await ctx.message.delete()
	channel = bot.get_channel(SCRIM_INFO)
	await channel.purge()
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	with open(infoFile,"r") as read_file:
		data = json.load(read_file)
		await channel.send(f"> Last Updated at {currentTime.strftime('**%H:%M:%S** on **%d-%m-%Y**')}")
		for p in data['info']:
			try:
				await channel.send(f"> __**Stats**__\n**Wins**: {p['wins']}\n**Losses**: {p['losses']}\n**Round Wins**: {p['rwins']}\n**Round Losses**: {p['rlosses']}\n**Win/Loss**: {round(p['wins']/p['losses'],3)}\n**Round Win/Loss**: {round(p['rwins']/p['rlosses'],3)}")
			except:
				await channel.send(f"> __**Stats**__\n**Wins**: {p['wins']}\n**Losses**: {p['losses']}\n**Round Wins**: {p['rwins']}\n**Round Losses**: {p['rlosses']}\n**Win/Loss**: 0.000\n**Round Win/Loss**: 0.000")
		for p in data['miitto']:
			try:
				await channel.send(f"> __**Miitto**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: {round(p['kills']/p['deaths'],3)}")
			except:
				await channel.send(f"> __**Miitto**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: 0.000")
		for p in data['nathan']:
			try:
				await channel.send(f"> __**Nathan**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: {round(p['kills']/p['deaths'],3)}")
			except:
				await channel.send(f"> __**Nathan**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: 0.000")
		for p in data['marcus']:
			try:
				await channel.send(f"> __**Marcus**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: {round(p['kills']/p['deaths'],3)}")
			except:
				await channel.send(f"> __**Marcus**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: 0.000")
		for p in data['jack']:
			try:
				await channel.send(f"> __**Jack**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: {round(p['kills']/p['deaths'],3)}")
			except:
				await channel.send(f"> __**Jack**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: 0.000")
		for p in data['viddy']:
			try:
				await channel.send(f"> __**Viddy**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: {round(p['kills']/p['deaths'],3)}")
			except:
				await channel.send(f"> __**Viddy**__\n**Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: 0.000")
	with open(trialFile,"r") as trial_file:
		data = json.load(trial_file)
		channel = bot.get_channel(TRIAL_ID)
		await channel.purge()
		await channel.send(f"> **Trial Stats**  Last Updated at {currentTime.strftime('**%H:%M:%S** on **%d-%m-%Y**')}")
		try:
			for p in data['trialone']:
				try:
					await channel.send(f"> __**Trial 1 | {p['name']}**__\n**Games Played**: {p['games']}  **Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: {round(p['kills']/p['deaths'],3)}")
				except:
					await channel.send(f"> __**Trial 1 | {p['name']}**__\n**Games Played**: {p['games']}  **Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: 0.000")
		except:
			print ("No Trial One")
		try:
			for p in data['trialtwo']:
				try:
					await channel.send(f"> __**Trial 2 | {p['name']}**__\n**Games Played**: {p['games']}  **Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: {round(p['kills']/p['deaths'],3)}")
				except:
					await channel.send(f"> __**Trial 2 | {p['name']}**__\n**Games Played**: {p['games']}  **Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: 0.000")
		except:
			print ("No Trial Two")
		try:
			for p in data['trialthree']:
				try:
					await channel.send(f"> __**Trial 3 | {p['name']}**__\n**Games Played**: {p['games']}  **Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: {round(p['kills']/p['deaths'],3)}")
				except:
					await channel.send(f"> __**Trial 3 | {p['name']}**__\n**Games Played**: {p['games']}  **Kills**: {p['kills']}  **Deaths**: {p['deaths']}  **Assists**: {p['assists']}\n**K/D**: 0.000")
		except:
			print ("No Trial Three")




		
@bot.command()
async def prefix(ctx, message):
	print (f"{ctx.author.name} called setprefix()")
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		PREFIX = message
		bot = commands.Bot(command_prefix=PREFIX)
		await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"ELTDA | {PREFIX}helpme"))
	
@bot.command()
async def clear(ctx, message):
	print (f"{ctx.author.name} called clear()")
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		message = int(message)
		await ctx.channel.purge(limit = message+1)

@bot.command()
async def pingall(ctx):
	print (f"{ctx.author.name} called ping()")
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	global maps
	try:
		beforeScrim = (scrimTime - currentTime)
	except:
		beforeScrim = "No time Set"
	await ctx.message.delete()
	channel = bot.get_channel(ANNOUNCMENT_ID)
	try:
		await channel.send(f"<@&726192849191829686> Scrim Time in **{beforeScrim.days}**days **{beforeScrim.hour}**hrs **{beforeScrim.minutes}**min **{beforeScrim.seconds}**seconds | Maps are **{', '.join(str(x) for x in maps)}**")
	except:
		await channel.send(f"<@&726192849191829686> **No Time set** | Maps are **{', '.join(str(x) for x in maps)}**")

@bot.command()
async def miitto(ctx, kills, deaths, assists):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		kills = int(kills)
		deaths = int(deaths)
		assists = int(assists)
		with open(infoFile, "r") as read_file:
			data = json.load(read_file)
			for p in data['miitto']:
				p['kills'] = p['kills'] + kills
				p['deaths'] = p['deaths'] + deaths
				p['assists'] = p['assists'] + assists
		with open(infoFile, "w") as write_file:
			json.dump(data, write_file)
		await info(ctx)

@bot.command()
async def marcus(ctx, kills, deaths, assists):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		kills = int(kills)
		deaths = int(deaths)
		assists = int(assists)
		with open(infoFile, "r") as read_file:
			data = json.load(read_file)
			for p in data['marcus']:
				p['kills'] = p['kills'] + kills
				p['deaths'] = p['deaths'] + deaths
				p['assists'] = p['assists'] + assists
		with open(infoFile, "w") as write_file:
			json.dump(data, write_file)
		await info(ctx)

@bot.command()
async def nathan(ctx, kills, deaths, assists):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		kills = int(kills)
		deaths = int(deaths)
		assists = int(assists)
		with open(infoFile, "r") as read_file:
			data = json.load(read_file)
			for p in data['nathan']:
				p['kills'] = p['kills'] + kills
				p['deaths'] = p['deaths'] + deaths
				p['assists'] = p['assists'] + assists
		with open(infoFile, "w") as write_file:
			json.dump(data, write_file)
		await info(ctx)
		
@bot.command()
async def lokii(ctx, kills, deaths, assists):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		kills = int(kills)
		deaths = int(deaths)
		assists = int(assists)
		with open(infoFile, "r") as read_file:
			data = json.load(read_file)
			for p in data['lokii']:
				p['kills'] = p['kills'] + kills
				p['deaths'] = p['deaths'] + deaths
				p['assists'] = p['assists'] + assists
		with open(infoFile, "w") as write_file:
			json.dump(data, write_file)
		await info(ctx)
@bot.command()
async def jack(ctx, kills, deaths, assists):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		kills = int(kills)
		deaths = int(deaths)
		assists = int(assists)
		with open(infoFile, "r") as read_file:
			data = json.load(read_file)
			for p in data['jack']:
				p['kills'] = p['kills'] + kills
				p['deaths'] = p['deaths'] + deaths
				p['assists'] = p['assists'] + assists
		with open(infoFile, "w") as write_file:
			json.dump(data, write_file)
		await info(ctx)

@bot.command()
async def viddy(ctx, kills, deaths, assists):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		kills = int(kills)
		deaths = int(deaths)
		assists = int(assists)
		with open(infoFile, "r") as read_file:
			data = json.load(read_file)
			for p in data['viddy']:
				p['kills'] = p['kills'] + kills
				p['deaths'] = p['deaths'] + deaths
				p['assists'] = p['assists'] + assists
		with open(infoFile, "w") as write_file:
			json.dump(data, write_file)
		await info(ctx)
		
@bot.command()
async def trialone(ctx, kills, deaths, assists):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		kills = int(kills)
		deaths = int(deaths)
		assists = int(assists)
		with open(trialFile, "r") as read_file:
			data = json.load(read_file)
			for p in data['trialone']:
				p['games'] = p['games'] + 1
				p['kills'] = p['kills'] + kills
				p['deaths'] = p['deaths'] + deaths
				p['assists'] = p['assists'] + assists
		with open(trialFile, "w") as write_file:
			json.dump(data, write_file)
		await info(ctx)

@bot.command()
async def trialtwo(ctx, kills, deaths, assists):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		kills = int(kills)
		deaths = int(deaths)
		assists = int(assists)
		with open(trialFile, "r") as read_file:
			data = json.load(read_file)
			for p in data['trialtwo']:
				p['games'] = p['games'] + 1
				p['kills'] = p['kills'] + kills
				p['deaths'] = p['deaths'] + deaths
				p['assists'] = p['assists'] + assists
		with open(trialFile, "w") as write_file:
			json.dump(data, write_file)
		await info(ctx)

@bot.command()
async def trialthree(ctx, kills, deaths, assists):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		kills = int(kills)
		deaths = int(deaths)
		assists = int(assists)
		with open(trialFile, "r") as read_file:
			data = json.load(read_file)
			for p in data['trialthree']:
				p['games'] = p['games'] + 1
				p['kills'] = p['kills'] + kills
				p['deaths'] = p['deaths'] + deaths
				p['assists'] = p['assists'] + assists
		with open(trialFile, "w") as write_file:
			json.dump(data, write_file)
		await info(ctx)

@bot.command()
async def settrialone (ctx, *name):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		with open(trialFile,"r") as read_file:
			data = json.load(read_file)
			for p in data['trialone']:
				p['name'] = name[0]
				try:
					if name[1].upper() == "Y":
						p['games'] = 0
						p['kills'] = 0
						p['deaths'] = 0
						p['assists'] = 0
				except:
					print ("Updating Name Only")
		with open(trialFile,"w") as write_file:
			json.dump(data, write_file)
		await info(ctx)

@bot.command()
async def settrialtwo (ctx, *name):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		with open(trialFile,"r") as read_file:
			data = json.load(read_file)
			for p in data['trialtwo']:
				p['name'] = name[0]
				try:
					if name[1].upper() == "Y":
						p['games'] = 0
						p['kills'] = 0
						p['deaths'] = 0
						p['assists'] = 0
				except:
					print ("Updating Name Only")
		with open(trialFile,"w") as write_file:
			json.dump(data, write_file)
		await info(ctx)
		
@bot.command()
async def settrialthree (ctx, *name):
	if ctx.author.bot:
		print ("BOT AUTHOR")
		return
	else:
		with open(trialFile,"r") as read_file:
			data = json.load(read_file)
			for p in data['trialthree']:
				p['name'] = name[0]
				try:
					if name[1].upper() == "Y":
						p['games'] = 0
						p['kills'] = 0
						p['deaths'] = 0
						p['assists'] = 0
				except:
					print ("Updating Name Only")
		with open(trialFile,"w") as write_file:
			json.dump(data, write_file)
		await info(ctx)

while True:
	try:
		bot.run(TOKEN)
	except:
		print ("Failed bot run")
		time.sleep(5)
