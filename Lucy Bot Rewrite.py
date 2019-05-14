import discord
import json
import asyncio
from secrets import randbelow
from discord.ext import commands

jsonPath = 'data.json'
with open(jsonPath) as fopen:
	data = json.load(fopen)
	
bot = commands.Bot(command_prefix = '?')

	
def findRoleID(roleName, guild):
	roles = guild.roles
	for i in roles:
		if i.name == roleName:
			return i.id
	return None
	
	
def TestOwner(ctx):
	return ctx.author.id in data['ownerIDs']

	
def TestChannel(ctx):
	return ctx.channel.id in data['botChannels']

	
def saveInfo():
	with open(jsonPath, 'w') as outFile:
		json.dump(data, outFile, indent=4)
	
	
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def welcomemessage(context, *, message):
	message = message.replace('%u', '{0}')
	data['welcomeMessage'][0] = message
	
	await context.send('Do you want to include an image? Send the link if yes, type n to skip.')
	imageLink = await bot.wait_for('message', check=TestOwner)
	imageLink = imageLink.content
	while 'http' not in imageLink:
		if imageLink == 'n':
			imageLink = ''
			break
		await context.send('That was not a valid link. Please try again.')
		imageLink = await bot.wait_for('message', check=TestOwner)
		imageLink = imageLink.content
		
	data['welcomeMessage'][1] = imageLink
	saveInfo()
	await context.send('I will now welcome new people with that message!')
	
	
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def goodbyemessage(context, *, message):
	message = message.replace('%u', '{0}')
	data['goodbyeMessage'] = message
	await context.send('I will now say that when someone leaves!')
	saveInfo()

	
@bot.command()
@commands.check(TestOwner)
async def setchannel(context, type):
	if type == 'join':
		data['welcomeChannelID'] = context.channel.id
		await context.send('This is now the channel where I welcome people!')
	
	elif type == 'leave':
		data['goodbyeChannelID'] = context.channel.id
		await context.send('This is now the channel where I monitor people who leave!')
	
	elif type == 'quote':
		data['quoteChannelID'] = context.channel.id
		await context.send('This is now the channel where I send quotes!')
		
	elif type == 'commands':
		if context.channel.id in data['botChannels']:
			data['botChannels'].remove(context.channel.id)
			await context.send('I will not listen to commands in this channel anymore!')
		
		else:
			data['botChannels'].append(context.channel.id)
			await context.send('I will now listen to commands in this channel!')
			
		
	saveInfo()
	
	
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def addrank(context, roleName):
	if roleName in data['Roles']:
		await context.send('This rank already exists!')
		return
		
	roleID = findRoleID(roleName, context.guild)
	if roleID == None:
		await context.send('I could not find a role with the name **{0}**. Are you sure it exists?'.format(roleName))
		continue
	data['Roles'][roleName] = [roleID, '', '', '', '']
	await context.send('Rank **{0}** has been added!'.format(roleName))
		
	saveInfo()
	
	
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def delrank(context, *roleNames):
	if not roleNames:
		await context.send('You need to type at least one role name!')
		return
		
	for i in roleNames:
		if i not in data['Roles']:
			await context.send('I could not find a rank with the name **{0}**. Are you sure it exists?'.format(i))
			continue
			
		data['Roles'].pop(i)
		await context.send('The rank **{0}** has been removed!'.format(i))
	
	saveInfo()

	
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def editrank(context, *args):
	if len(args) != 3:
		await context.send('That\'s the wrong number of arguments!')
		return
		
	roleName = args[0]
	if roleName not in data['Roles']:
		await context.send('I could not find a rank with that name. Are you sure it exists?')
		return
		
	messageType = args[1]
	if messageType not in ['join', 'leave']:
		await context.send('Your second argument was invalid. Please use either **join** or **leave**')
		return
		
	editType = args[2]
	if editType not in ['message', 'image']:
		await context.send('Your third argument was invalid. Please use either **message** or **image**')
		return
	
	if editType == 'image':
		await context.send('Type an image link for me to send when someone {0}s a rank, or type remove to set it to nothing.'.format(messageType))
		imgLink = await bot.wait_for('message', check=TestOwner)
		imgLink = imgLink.content
		
		while 'http' not in imgLink:
			if imgLink == 'remove':
				img = ''
				await context.send('I will not send an image when someone {0}s **{1}** anymore!'.format(messageType, roleName))
				break
			
			await context.send('That was not a valid link. Please try again.')
			imgLink = await client.wait_for('message', check=TestOwner)
			imgLink = imgLink.content
			
		if messageType == 'join':
			data['Roles'][roleName][2] = imgLink
		else:
			data['Roles'][roleName][4] = imgLink

		saveInfo()

		if imgLink == '':
			return
	
		await context.send('I will now send that image whenever someone {0}s **{1}**!'.format(messageType, roleName))
	
	else:
		await context.send('Type a custom message for me to send when someone {0}s a rank, or type remove to set it to nothing.'.format(messageType))
		customMessage = await bot.wait_for('message', check=TestOwner)
		customMessage = customMessage.content
		customMessage = customMessage.replace('%u', '{0}')
		customMessage = customMessage.replace('%r', '{1}')
		
		if customMessage == 'remove':
			customeMessage = ''
			await context.send('I will now use the default message for when someone {0}s **{1}**!'.format(messageType, roleName))
		
		if messageType == 'join':
			data['Roles'][roleName][1] = customMessage
		else:
			data['Roles'][roleName][3] = customMessage
		
		saveInfo()
		
		if customMessage == '':
			return
			
		await context.send('I will now send that message when someone {0}s **{1}**!'.format(messageType, roleName))
		

@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def addquote(context, *, quote):
	data['quotePool'].append(quote)
	await context.send('Quote added!')
	
	saveInfo()
	
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def quotes(context):
	msg = 'List of quotes for this server:\n'
	j = 1
	
	for i in data['quotePool']:
		if len(msg + str(j) + ' - ' + i + '\n') > 2000:
			await context.send(msg)
			msg = ''
		msg = msg + str(j) + ' - ' + i + '\n'
		j += 1
		
	await context.send(msg)
	
	
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def delquote(context, position):
	try:
		position = int(position)
	except ValueError:
		await context.send('That was not a valid number!')
		return
		
	if position > len(data['quotePool']) or position < 1:
		await context.send('Sorry, I couldn\'t find a quote in that position.')
	
	data['quotePool'].pop(quoteNumber - 1)
	await context.send('Quote removed.')
	
	saveInfo()
	
	
@bot.command()
@commands.check(TestChannel)
async def rank(context, rankName):
	if rankName not in data['Roles']:
		await context.send('I could not find a rank with that name.')
		return
	
	role = context.guild.get_role(data['Roles'][rankName][0])
	
	if role not in context.author.roles:
		await context.author.add_roles(role)
		
		if data['Roles'][rankName][1] == '':
			await context.send('{0}, you have joined **{1}**'.format(context.author.mention, role.name))
			
		else:
			await context.send(data['Roles'][rankName][1].format(context.author.mention, role.name))
			
		if data['Roles'][rankName][2] != '':
			embed = discord.Embed(title='', description = '')
			embed = embed.set_image(url=data['Roles'][rankName][2])
			await context.send(content=None, embed=embed)
			
	else:
		await context.author.remove_roles(role)
		
		if data['Roles'][rankName][3] == '':
			await context.send('{0}, you have left **{1}**'.format(context.author.mention, role.name))
			
		else:
			await context.send(data['Roles'][rankName][3].format(context.author.mention, role.name))
			
		if data['Roles'][rankName][4] != '':
			embed = discord.Embed(title='', description = '')
			embed = embed.set_image(url=data['Roles'][rankName][4])
			await context.send(content=None, embed=embed)

			
@bot.command()
@commands.check(TestChannel)
async def ranks(context):
	msg = 'List of self-assignable roles for this server:\n'
	
	for i in data['Roles']:
		msg = msg + '**' + i + '**\n'

	await context.send(msg)
	
	
	
@bot.event
async def on_member_join(member):
	if data['welcomeMessage'][0] == '' or data['welcomeChannelID'] == '':
		return
	
	welcomeChannel = bot.get_channel(data['welcomeChannelID'])
	await welcomeChannel.send(data['welcomeMessage'][0].format(member.mention))
	
	if data['welcomeMessage'][1] != '':
		embed = discord.Embed(title='', description='')
		embed = embed.set_image(url=data['welcomeMessage'][1].format(member.mention))
		await welcomeChannel.send(content=None, embed=embed)
	

@bot.event
async def on_member_remove(member):
	if data['goodbyeMessage'] == '' or data['goodbyeChannelID'] == '':
		return
	
	goodbyeChannel = bot.get_channel(data['goodbyeChannelID'])
	await goodbyeChannel.send(data['goodbyeMessage'].format('**' + member.name + '**'))
	
	
@bot.event
async def on_guild_role_update(before, after):
	if before.name in data['Roles']:
		data['Roles'][after.name] = data['Roles'][before.name]
		data['Roles'].pop(before.name)
		
		saveInfo()

	
@bot.event
async def on_ready():
	print('------')
	print('Logged in as {0}'.format(bot.user.name))
	
	quoteChannel = bot.get_channel(data['quoteChannelID'])
	while quoteChannel == None:
		quoteChannel = bot.get_channel(data['quoteChannelID'])
	
	while 1:
		randomNumber = randbelow(100)
		if randomNumber == 69:
			messageNumber = randbelow(len(data['quotePool']))
			await quoteChannel.send(data['quotePool'][messageNumber])
			await asyncio.sleep(3600)
		else:
			await asyncio.sleep(120)



bot.run(data['TOKEN'])

while True:
	bot.connect(reconnect = True)
	time.sleep(1)