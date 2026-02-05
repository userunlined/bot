import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

VERIF_ROLE = 1469007626938355805  # Cargo verificado
ADMIN_ROLE = 1469006955992453151  # Cargo admin (só eles usam !verifica)

@bot.event
async def on_ready():
    print(f'{bot.user} está online no Railway!')

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def verifica(ctx):
    embed = discord.Embed(
        title="🏴‍☠️ Verificação",
        description="**Clique no emoji 🏴‍☠️ para ganhar acesso ao servidor!**",
        color=0x00ff00
    )
    embed.set_footer(text="Seja Bem-Vindo!")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🏴‍☠️")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name != '🏴‍☠️' or payload.user_id == bot.user.id:
        return
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    if msg.author.id != bot.user.id:
        return
    try:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(VERIF_ROLE)
        if role in member.roles:
            return
        await member.add_roles(role)
        print(f"✅ Role dado a {member}")
        await member.send("✅ Verificado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

# Adicione no final antes bot.run:
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ Só admins podem usar !verifica!")

@bot.command()
async def ping(ctx):
    await ctx.send('Pong! Funcionando 24/7.')

bot.run(os.getenv('DISCORD_TOKEN'))
