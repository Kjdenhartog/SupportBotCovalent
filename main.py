import discord
import os
from discord.ext import commands
import asyncio
from keep_alive import keep_alive
from ticketmachine import Ticketmachine
from embeds import command_channel_embed, ticket_embed, claimed_embed, information_embed, history_embed

# Global
ROLENAME = 'Support Staff Member'
CATEGORY_NAME = 'SUPPORT'
COMMAND_CHANNEL_NAME = 'command-channel'

# Client
intents = discord.Intents.all()
client = commands.Bot(command_prefix='/', intents=intents)

# Ticketmachine
ticketmachines = dict()  # (server_object : ticketmachine_object)

@client.event
async def on_ready():
    print(f'Preparing {client.user}.')
    # Create staffmembers and support category
    for server in client.guilds:
        ticketmachine = Ticketmachine()
        await _update_staff_members(server, ticketmachine)
        # Create a ticketmachine
        ticketmachines[server] = ticketmachine 
    # Ready
    print(f'{client.user} is ready')

# Create a ticket
@client.command(pass_context=True)
async def ticket(ctx):
    await ctx.message.delete()
    # Check if a request is already made
    ticket_in_queue = ticketmachines[ctx.guild].already_in_queue(ctx.author)
    await ctx.author.create_dm()
    if ticket_in_queue == None:
        # Create the ticket
        tn, queue = ticketmachines[ctx.guild].create_ticket(ctx.author)
        embed = ticket_embed(ctx, tn, queue)
        await ctx.author.dm_channel.send(embed=embed)
        print(f'ticket created: {tn}')
    else:
        tn, queue = ticket_in_queue
        # Send a dm to the author
        await ctx.author.dm_channel.send(
            f'Hi {ctx.author.name}, you cannot make a new request since you are already in queue at position {queue} with ticketnumber {tn}. Please wait for the support staff to help.'
        )

# Close an open ticket
@client.command(pass_context=True)
async def close(ctx):
    await ctx.message.delete()
    ticket_in_queue = ticketmachines[ctx.guild].already_in_queue(ctx.author)
    if ticket_in_queue == None:
        msg = f'Hi {ctx.author.name}, you currently have no open tickets' 
    else:
        tn, queue = ticket_in_queue
        ticketmachines[ctx.guild].close_ticket(tn)
        msg = f'Hi {ctx.author.name}, your ticket request has been closed'
    await ctx.author.create_dm() 
    await ctx.author.dm_channel.send(msg) 
    print(f'ticket closed: {tn}')

# Let a staff member claim a ticket
@client.command(pass_context=True)
async def claim(ctx):
    await ctx.message.delete()
	# Check if staff member
    role = discord.utils.find(lambda r: r.name == ROLENAME, ctx.message.guild.roles)
    if role in ctx.author.roles:
        # Check if there are tickets in queue
        if ticketmachines[ctx.guild].isEmpty:
            await ctx.author.create_dm()
            await ctx.author.dm_channel.send('Currently no tickets available to claim')
            return
        await _update_staff_members(ctx.guild, ticketmachines[ctx.guild])
        # Assign a ticket to a staff member
        values = ticketmachines[ctx.guild].handle_ticket(ctx.author)
        if values == None:
            print('Whaaaatttt?')
            return
        ticketnumber, user = values
        # Create a text channel which is only visible to the user and staff member
        category = await _support_category(ctx.guild)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True)
            }
        channel = await ctx.guild.create_text_channel('ticket-' + str(ticketnumber), overwrites=overwrites, category=category)
        embed = claimed_embed(ctx, user)
        await channel.send(embed=embed)
        print(f'Ticket claimed: {ticketnumber}')

# End a ticket and save the information
@client.command(pass_context=True)
async def end(ctx):
    await ctx.message.delete()
    # Check if support channel
    if not 'ticket-' in ctx.channel.name : return
    ticketnumber = str(ctx.channel.name).replace('ticket-', '')
    if not ticketnumber.isnumeric(): return
    # Make a list of all the messages
    messages = []
    async for message in ctx.channel.history(limit=1000):
        if message.author.id == client.user.id: continue
        if '/end' in message.content: continue
        messages.insert(0, message)
    values = ticketmachines[ctx.guild].finish_ticket(int(ticketnumber), messages)
    if not values:
        await ctx.channel.send('This ticket does not exists or is not being handled. Cannot save the conversation.')
    else:
        user, staff = values
        await ctx.channel.send('Conversation is succesfully saved and the ticket has been closed. Any new messages will not be saved, for new questions type /ticket to get a new ticket. The channel will be deleted after an hour.')
        print(f'ticket ended: {ticketnumber}')
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            staff: discord.PermissionOverwrite(read_messages=True, send_messages=False)
            }
        await ctx.channel.edit(overwrites=overwrites)
        # Delete channel after an hour
        await asyncio.sleep(3600)
        await ctx.channel.delete()

# Get a list of the users tickets your tickets
@client.command(pass_context=True)
async def history(ctx):
    await ctx.message.delete()
    hist = ticketmachines[ctx.guild].history(ctx.author)
    await ctx.author.create_dm()
    embed = history_embed(ctx, hist)
    await ctx.author.dm_channel.send(embed=embed) 

# Get the full information of a ticket
@client.command(pass_context=True)
async def information(ctx, ticketnumber):
    # Check if it starts with a ticketnumber
    if not ticketnumber.isnumeric(): 
        await ctx.channel.send('Wrong input. Enter a numeric ticketnumber. Type /information ticketnumber')
        return
    # Check if it may acces this ticket
    information = ticketmachines[ctx.guild].information_ticket(int(ticketnumber))
    if information == None: 
        await ctx.channel.send('Wrong input. Enter a valid ticketnumber. Type /information ticketnumber')
        return
    # Check if has access
    role = discord.utils.find(lambda r: r.name == ROLENAME, ctx.message.guild.roles)
    if not role in ctx.author.roles and information['userid'] != ctx.author: 
        await ctx.channel.send('You don\'t have acces to this ticket.')
        return    
    # Send message with the information of the ticketnumber
    embed = information_embed(ctx, ticketnumber, information)
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send(embed=embed) 
    print(f'Information ticket: {ticketnumber}')

# Helper functions
async def _update_staff_members(server, ticketmachine: int):
	# Find the support staff role
	if ROLENAME in [role.name for role in server.roles]:
		role = [role for role in server.roles if role.name == ROLENAME][0]
	# Create new role if it does not exist
	else:
		role = await server.create_role(name=ROLENAME)
	for member in server.members:
		if role in member.roles:
			ticketmachine.add_staff(member)
		else:
			ticketmachine.delete_staff(member)

async def _support_category(server: discord.Guild):
    if CATEGORY_NAME in [cat.name for cat in server.categories]:
        # Get the category 
        for category in server.categories:
            if category.name == CATEGORY_NAME:
                return category
    else:
        # Create the category if it does not exist
        await _update_category(server)
        return _support_category(server)

async def _update_category(server: discord.Guild):
    if not CATEGORY_NAME in [cat.name for cat in server.categories]:
        # Create category with info channel and command channel
        category = await server.create_category(CATEGORY_NAME)
        info = await category.create_text_channel(COMMAND_CHANNEL_NAME)
        await info.send(embed=command_channel_embed())
    else:
        # Get the category 
        for category in server.categories:
            if category.name == CATEGORY_NAME:
                break
        info = None
        for channel in category.channels:
            if channel.name == COMMAND_CHANNEL_NAME:
                info = channel
        if info == None:
            info = await category.create_text_channel(COMMAND_CHANNEL_NAME)
            # Send an embed with all the information
            embed = command_channel_embed()
            await info.send(embed=embed)
        else:
            await info.purge(limit=100, check= lambda message: message.author != client.user)

# Function to run forever
async def background_tasks():
    await client.wait_until_ready()
    while not client.is_closed():
        for server in client.guilds:
            await _update_category(server) # Delete messages
        await asyncio.sleep(30) # task runs every 30 seconds

# Run the program
keep_alive()
client.loop.create_task(background_tasks())
client.run(os.environ['TOKEN'])

