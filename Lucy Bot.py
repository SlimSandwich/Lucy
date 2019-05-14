import discord
import json
import asyncio
from secrets import randbelow
from discord.ext import commands
# opens the json file to grab standard information, along with the quote pool
jsonPath = 'data.json'
with open(jsonPath) as fopen:
	data = json.load(fopen)
# setting default prefix for the bot, change to whatever you want within reason	
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

# ---------------------------------------------------------------------------------------------------	
# Allows the server owner to change the welcome message (whenever a user joins) to whatever they want
# Also has the ability to add an image to the message, for extra flair
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
	
# Displays an message whenever someone leaves the server. No image capability
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def goodbyemessage(context, *, message):
	message = message.replace('%u', '{0}')
	data['goodbyeMessage'] = message
	await context.send('I will now say that when someone leaves!')
	saveInfo()

# Gives the server owner the ability to set where Lucy will greet, send off, post quotes.
# Also has the added function of setting specific channels where Lucy will listen for commands
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
	
# Allows the server owner to add a rank	
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
	
# Allows the server owner to remove a rank	
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

# Allows the server owner to edit the message given when joining or leaving a rank	
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def editrank(context, *args):
	if len(args) != 3:
		await context.send('That\'s the wrong number of arguments!')
		return
		
	roleName = args[0]
	if roleName not in data['Roles']: # Looks for the role given. If the role doesn't exist, it gives an error message
		await context.send('I could not find a rank with that name. Are you sure it exists?')
		return
		
	messageType = args[1]
	if messageType not in ['join', 'leave']: # Looks for the command "join" or "leave". If neither are given, it gives an error message
		await context.send('Your second argument was invalid. Please use either **join** or **leave**')
		return
		
	editType = args[2]
	if editType not in ['message', 'image']: # Looks for the command "message" or "image". If neither are given, it gives an error message
		await context.send('Your third argument was invalid. Please use either **message** or **image**')
		return
	
	if editType == 'image': # Asks the owner for an image to send when someone joins/leaves a rank
		await context.send('Type an image link for me to send when someone {0}s a rank, or type remove to set it to nothing.'.format(messageType))
		imgLink = await bot.wait_for('message', check=TestOwner)
		imgLink = imgLink.content
		
		while 'http' not in imgLink:
			if imgLink == 'remove': # Removes the image from the join/leaveing message
				img = ''
				await context.send('I will not send an image when someone {0}s **{1}** anymore!'.format(messageType, roleName))
				break
			# Error message
			await context.send('That was not a valid link. Please try again.')
			imgLink = await client.wait_for('message', check=TestOwner)
			imgLink = imgLink.content
		# Saves the image to the join/leave array	
		if messageType == 'join':
			data['Roles'][roleName][2] = imgLink
		else:
			data['Roles'][roleName][4] = imgLink

		saveInfo()

		if imgLink == '':
			return
	
		await context.send('I will now send that image whenever someone {0}s **{1}**!'.format(messageType, roleName))
	
	else: # The server owner can set a custom message for Lucy to send when someone joins a rank, or can be left blank
		await context.send('Type a custom message for me to send when someone {0}s a rank, or type remove to set it to nothing.'.format(messageType))
		customMessage = await bot.wait_for('message', check=TestOwner)
		customMessage = customMessage.content
		customMessage = customMessage.replace('%u', '{0}')
		customMessage = customMessage.replace('%r', '{1}')
		# Removes the custom message
		if customMessage == 'remove':
			customeMessage = ''
			await context.send('I will now use the default message for when someone {0}s **{1}**!'.format(messageType, roleName))
		# Saves the message to the join/leave array
		if messageType == 'join':
			data['Roles'][roleName][1] = customMessage
		else:
			data['Roles'][roleName][3] = customMessage
		
		saveInfo()
		
		if customMessage == '':
			return
			
		await context.send('I will now send that message when someone {0}s **{1}**!'.format(messageType, roleName))
		
# Adds a quote to the quotepool
@bot.command()
@commands.check(TestOwner)
@commands.check(TestChannel)
async def addquote(context, *, quote):
	data['quotePool'].append(quote)
	await context.send('Quote added!')
	
	saveInfo()
# Displays the quotepool
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
	
# Deletes a quote from the quotepool	
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
	
# Allows a user to join/leave the specified rank	
@bot.command()
@commands.check(TestChannel)
async def rank(context, rankName):
	if rankName not in data['Roles']:
		await context.send('I could not find a rank with that name.') # Displays if the role was not found in the array
		return
	
	role = context.guild.get_role(data['Roles'][rankName][0])
	
	if role not in context.author.roles:
		await context.author.add_roles(role)
		# Grabs user and adds them to the role specified
		if data['Roles'][rankName][1] == '':
			await context.send('{0}, you have joined **{1}**'.format(context.author.mention, role.name))
			
		else: # Gives the custom message instead of the default
			await context.send(data['Roles'][rankName][1].format(context.author.mention, role.name))
		#If there is an image to display upon joining a role, this allows it to display	
		if data['Roles'][rankName][2] != '':
			embed = discord.Embed(title='', description = '')
			embed = embed.set_image(url=data['Roles'][rankName][2])
			await context.send(content=None, embed=embed)
			
	else:
		await context.author.remove_roles(role)
		# Grabs user and removes them from the role specified
		if data['Roles'][rankName][3] == '':
			await context.send('{0}, you have left **{1}**'.format(context.author.mention, role.name))
			
		else: # Gives the custom message instead of the default
			await context.send(data['Roles'][rankName][3].format(context.author.mention, role.name))
		# If there is an image to display upon leaving a role, this allows it to display	
		if data['Roles'][rankName][4] != '':
			embed = discord.Embed(title='', description = '')
			embed = embed.set_image(url=data['Roles'][rankName][4])
			await context.send(content=None, embed=embed)

# Outputs the created roles			
@bot.command()
@commands.check(TestChannel)
async def ranks(context):
	msg = 'List of self-assignable roles for this server:\n'
	
	for i in data['Roles']:
		msg = msg + '**' + i + '**\n'

	await context.send(msg)
	
	
# Displays the welcome message to a new user	
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
	
# Displays the goodbye message when a user leaves the server
@bot.event
async def on_member_remove(member):
	if data['goodbyeMessage'] == '' or data['goodbyeChannelID'] == '':
		return
	
	goodbyeChannel = bot.get_channel(data['goodbyeChannelID'])
	await goodbyeChannel.send(data['goodbyeMessage'].format('**' + member.name + '**'))
	
# Grabs and re-add users to a renamed/edited rank	
@bot.event
async def on_guild_role_update(before, after):
	if before.name in data['Roles']:
		data['Roles'][after.name] = data['Roles'][before.name]
		data['Roles'].pop(before.name)
		
		saveInfo()

# Displays in terminal when the bot has connected to the Discord API, and displays quotes to users at random	
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
