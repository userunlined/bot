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
    if str(payload.emoji) == '🏴‍☠️' and payload.user_id != bot.user.id:
        try:
            guild = bot.get_guild(payload.guild_id)
            if not guild:
                print("Guild not found")
                return
            member = guild.get_member(payload.user_id)
            role = guild.get_role(VERIF_ROLE)
            if not role:
                print("Role not found")
                return
            if role in member.roles:
                print("Already verified")
                return
            print(f"Adding role to {member.name}")
            await member.add_roles(role, reason="Verificação")
            await member.send("✅ Verificado!")
        except Exception as e:
            print(f"Error: {e}")

# Adicione no final antes bot.run:
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ Só admins podem usar !verifica!")

@bot.command()
async def ping(ctx):
    await ctx.send('Pong! Funcionando 24/7.')

bot.run(os.getenv('DISCORD_TOKEN'))
