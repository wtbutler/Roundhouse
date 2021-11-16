#!/usr/bin/python
import roll_utils
import macro_utils

import os, re

import discord
from discord.ext import commands
from dotenv import Dotenv

temp = Dotenv(".env")
TOKEN = temp["DISCORD_TOKEN"]
GUILD = temp["DISCORD_SERVER"]

bot = commands.Bot(command_prefix='/', help_command=None)





@bot.command(name='add')
async def add_macro(ctx):
    message_in = f"{ctx.message.content[len(ctx.prefix+ctx.command.name+' '):]}"
    mention = ctx.author.mention
    if message_in == 'help':
        await ctx.send(rf"https://github.com/wtbutler/Roundhouse#macros")
        return
    macro = re.compile(r"^(?P<pattern>.+) => (?P<target>.+) \| (?P<test>.+)$")
    match = macro.match(message_in)
    if not match:
        await ctx.send(f"{mention}\nIncorrect syntax for macro")
        return
    components = match.groups()
    added, retval = await macro_utils.add_macro(ctx, components[0], components[1], components[2])
    if not added:
        await ctx.send(f"{mention}\n{retval}")
        return
    await handle_message(ctx, retval)

@bot.command(name='list')
async def list_macro(ctx):
    await ctx.send(await macro_utils.list_macros(ctx))

@bot.command(name='delete', help='delete specified macro commands')
async def delete_macro(ctx, macro: int):
    await ctx.send(await macro_utils.remove_macro(ctx, macro))





@bot.command(name='roll')
async def roll(ctx):
    message_in = f"{ctx.message.content[len(ctx.prefix+ctx.command.name+' '):]}"
    if message_in == 'help':
        await ctx.send(rf"https://github.com/wtbutler/Roundhouse#usage")
        return
    await handle_message(ctx, message_in)

@bot.command(name='r')
async def r(ctx):
    message_in = f"{ctx.message.content[len(ctx.prefix+ctx.command.name+' '):]}"
    if message_in == 'help':
        await ctx.send(rf"https://github.com/wtbutler/Roundhouse/blob/main/README.md#usage")
        return
    await handle_message(ctx, message_in)

async def handle_message(ctx, message_in):
    comment = -1
    if '##' in message_in:
        m, comment = message_in[:message_in.find('##')].strip(), message_in[message_in.find('##')+2:].strip()
        message_in = m
    result = await roll_utils.handle_dice(ctx, message_in)
    print(f"{ctx.author} asked for {message_in}")
    mention = ctx.author.mention
    if comment == -1:
        message = f"{mention}\n{result}"
    else:
        message = f"{mention}\n{comment}\n{result}"
    if len(message) >= 2000:
        print(f"\terror: message too long")
        message = f"{mention}\n{await util.error_message('Message too long')}"
    print(f"\treturning:\n{result}\n")
    await ctx.send(message)

@bot.command(name='help')
async def help(ctx):
        await ctx.send(rf"https://github.com/wtbutler/Roundhouse")

bot.run(TOKEN)
