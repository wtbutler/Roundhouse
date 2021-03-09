#!/usr/bin/python
import roll_utils
import macro_utils

import os, re

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_SERVER')

bot = commands.Bot(command_prefix='/')





@bot.command(name='add', help='add a regex macro that expands into a proper roll')
async def add_macro(ctx):
    message_in = f"{ctx.message.content[len(ctx.prefix+ctx.command.name+' '):]}"
    mention = ctx.author.mention
    if message_in == 'help':
        await ctx.send(rf'''
Syntax to add a macro:
```/add <pattern> => <target> | <test>```
This adds the rule that <pattern> is replaced with <target>, substituting groups, and runs it once on <test>
for example:
```/add F(-?[0-9]+) => 4dF+\1 | F3```
might return:
> `4dF+3` = (+--+)+3 = 3
and would have the rule 
```/add F(-?[0-9]+) => 4dF+\1 | F3```
saved until deleted

See https://docs.python.org/3/library/re.html and github.readme for more info
        ''')
        return
    macro = re.compile(r"^(?P<pattern>.+) => (?P<target>.+) \| (?P<test>.+)$")
    match = macro.match(message_in)
    if not match:
        await ctx.send(f"{mention}\nIncorrect syntax for macro")
        return
    components = match.groups()
    retval = await macro_utils.add_macro(ctx, components[0], components[1], components[2])
    await handle_message(ctx, retval)

@bot.command(name='list', help='list existing macro commands')
async def list_macro(ctx):
    await ctx.send(await macro_utils.list_macros(ctx))

@bot.command(name='delete', help='delete specified macro commands')
async def delete_macro(ctx, macro: int):
    await ctx.send(await macro_utils.remove_macro(ctx, macro))





@bot.command(name='roll', help='rolls dice')
async def roll(ctx):
    message_in = f"{ctx.message.content[len(ctx.prefix+ctx.command.name+' '):]}"
    await handle_message(ctx, message_in)

@bot.command(name='r', help='rolls dice')
async def r(ctx):
    message_in = f"{ctx.message.content[len(ctx.prefix+ctx.command.name+' '):]}"
    await handle_message(ctx, message_in)

async def handle_message(ctx, message_in):
    result = await roll_utils.handle_dice(ctx, message_in)
    print(f"{ctx.author} asked for {message_in}")
    mention = ctx.author.mention
    message = f"{mention}\n{result}"
    if len(message) >= 2000:
        print(f"\terror: message too long")
        message = f"{mention}\n{await util.error_message('Message too long')}"
    print(f"\treturning:\n{result}\n")
    await ctx.send(message)

bot.run(TOKEN)
