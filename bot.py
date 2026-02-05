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
        title="🏴‍☠️ Painel de Verificação",
        description="**Clique no emoji 🏴‍☠️ para ganhar o cargo verificado!**",
        color=0x00ff00
    )
    embed.set_footer(text="Apenas uma reação por usuário!")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🏴‍☠️")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == '🏴‍☠️' and not payload.member.bot:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(VERIF_ROLE)
        if role and role not in member.roles:
            await member.add_roles(role)
            await member.send(f"✅ **Verificado!** Você ganhou o cargo `{role.name}`.")

@bot.command()
async def ping(ctx):
    await ctx.send('Pong! Funcionando 24/7.')

bot.run(os.getenv('DISCORD_TOKEN'))
