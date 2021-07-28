import discord

# Command Channel embed
def command_channel_embed():
    embed = discord.Embed(
        title='Support Ticket Machine',
        description=
        f'Welcome Alchemists to the support text channels. This is a channel where all commands can be typed to create tickets. A ticket is way to get a support staff member to help you.',
        colour=discord.Colour.blue()
    )
    embed.set_thumbnail( url= 'https://icohigh.net/uploads/posts/2021-04/thumbs/1618468617_covalent_logo.png')
    embed.add_field(name='Creating tickets',
        value='To create a ticket type /ticket. This will add you to the queue.',
        inline=True)
    embed.add_field(
        name='Closing tickets',
        value='When you don\'t need help anymore you can type /close to close an open ticket.',
        inline=False
    )
    embed.add_field(
        name='History tickets',
        value='To get a list of your previous tickets, type /history.',
        inline=False
    )
    embed.add_field(
        name='Information ticket',
        value='To get information about one of your previous tickets type /information ticketnumber.',
        inline=False
    )
    return embed

def ticket_embed(ctx, tn: int, queue: int):
    # Ticket created embed
    embed = discord.Embed(
        title='Your ticket has been received',
        description=
        f'Hi {ctx.author.name}, you are in queue with ticketnumber {tn}. Please wait for the support staff to help.',
        colour=discord.Colour.blue()
    )
    embed.set_thumbnail(url= 'https://icohigh.net/uploads/posts/2021-04/thumbs/1618468617_covalent_logo.png')
    embed.add_field(name='Position in queue',
        value=f'Your current position is: {queue}.',
        inline=True)
    embed.add_field(
        name='Close ticket',
        value='To close your ticket type "/close" in the guild chat.',
        inline=False
    )
    return embed

# Create embed
def claimed_embed(ctx, user: discord.Member):
    embed = discord.Embed(
        title='Support Text Channel',
        description=
        f'Welcome {user.mention}! Feel free to ask any questions to our staff member {ctx.author.mention}. You can ask your questions in this text channel.',
        colour=discord.Colour.blue())
    embed.set_image(url= 'https://www.koncert.com/hubfs/Images/Blog%20Images/ask-blackboard-chalk-board-356079.jpg')
    embed.set_thumbnail(url= 'https://icohigh.net/uploads/posts/2021-04/thumbs/1618468617_covalent_logo.png')
    embed.add_field(
        name='End conversition',
        value= 'Type "/end" to close the conversation. The conversation will be saved afterwards',
        inline=False)
    return embed

def information_embed(ctx, ticketnumber: int, information: dict):
    # Send message with the information of the ticketnumber
    embed = discord.Embed(
        title=f'Information ticket {ticketnumber}',
        description= 'Here is an overview of the ticket.',
        colour=discord.Colour.blue())
    embed.set_thumbnail(url= 'https://icohigh.net/uploads/posts/2021-04/thumbs/1618468617_covalent_logo.png')
    # Make strings for the embed
    general_information = 'Userid: {}'.format(information['user'].mention)
    if information['staff'] != None:
        general_information += '\nStaffid: {}'.format(information['staff'].mention)
    general_information += '\nStatus: {}\nCreated: {}'.format(information['status'], information['date'].strftime("%d %B %Y at %H:%M"))
    if information['duration'] != None: 
        general_information += f'\nDuration: '
        seconds = int(information['duration'].total_seconds())
        minutes = seconds // 60 % 60
        hours = seconds // 3600 % 24
        days = seconds // 86400 
        if days > 0: 
            general_information += f'{days} days, {hours} hours and {minutes} minutes'
        elif hours > 0:
            general_information += f'{hours} hours and {minutes} minutes'
        else: general_information += f'{minutes} minutes and {seconds%60} seconds'

    embed.add_field(
        name='General information',
        value= general_information,
        inline=False)
    if information['status'] == 'Closed': 
        str_question = ''
        for message in information['questions']:
            str_question = str_question + message.author.name + ": " + message.content + '\n'
        embed.add_field(
            name='Conversation',
            value= str_question,
            inline=False)
    return embed

def history_embed(ctx, hist: list):    
    # Send message with the information of the ticketnumber
    embed = discord.Embed(
        title=f'History f your tickets',
        description= 'Here is an overview of your ticket history.',
        colour=discord.Colour.blue())
    embed.set_thumbnail(url= 'https://icohigh.net/uploads/posts/2021-04/thumbs/1618468617_covalent_logo.png')
    embed.add_field(
        name='Ticket list',
            value= hist,
            inline=False)
    return embed
