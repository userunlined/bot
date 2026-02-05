import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # necessário pros tickets/verificação
bot = commands.Bot(command_prefix='!', intents=intents)

# IDs de cargos e categoria
VERIF_ROLE = 1469007626938355805       # Cargo verificado
ADMIN_ROLE = 1469006955992453151      # Admin (usa !verifica)
TICKET_ADMIN_ROLE = 1469006955992453151  # Mesmo admin (usa !ticket)
TICKET_CATEGORY_ID = 1469073649654042655  # <<< TROCAR pelo ID da categoria

# ---------------- ON_READY ----------------
channel = bot.get_channel(PANEL_CHANNEL)
await channel.purge(limit=50)  # limpa 50 msgs antigas
embed = discord.Embed(title="🎫 Tickets", description="Clique para abrir ticket!", color=0x3498db)
view = TicketView()
await channel.send(embed=embed, view=view)

# --------------- VERIFICAÇÃO ----------------
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
    if str(payload.emoji) != '🏴‍☠️' or payload.user_id == bot.user.id:
        return
    try:
        guild = bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        if msg.author.id != bot.user.id:
            return

        member = await guild.fetch_member(payload.user_id)
        role = guild.get_role(VERIF_ROLE)
        if not role:
            print("❌ Role not found")
            return
        if role in member.roles:
            print("✅ Already verified")
            return

        print(f"✅ Adding {role.name} to {member}")
        await member.add_roles(role, reason="Verificação")
        await member.send("✅ Verificado no servidor!")
    except Exception as e:
        print(f"❌ Erro completo: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ Você não tem permissão para usar esse comando.")

# --------------- TICKET SYSTEM ----------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Escolha o tipo de ticket...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Dúvidas", value="duvidas", emoji="❓"),
            discord.SelectOption(label="Denúncias", value="denuncias", emoji="🚨"),
        ],
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        tipo = select.values[0]
        user = interaction.user
        guild = interaction.guild

        # Limpa chat do ticket
        await interaction.channel.purge(limit=None)

        # Contador
        count = 1
        for channel in guild.text_channels:
            if channel.name.startswith(f"{tipo}-"):
                count = max(count, int(channel.name.split('-')[1]) + 1)

        nome_canal = f"{tipo}-{count:02d}"

        # Permissões: só user + @everyone deny
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
        }

        # Cria canal
        category = guild.get_channel(TICKET_CATEGORY_ID) or None
        canal = await guild.create_text_channel(
            name=nome_canal,
            overwrites=overwrites,
            category=category,
            topic=f"Ticket de {user} | {tipo}",
            reason=f"Ticket {tipo} criado"
        )

        embed = discord.Embed(title=f"🎫 {tipo.title()}", description=f"{user.mention}, seu ticket foi criado!", color=0x00ff00)
        view_close = TicketCloseView()
        await canal.send(embed=embed, view=view_close)

        embed_res = discord.Embed(description=f"✅ **Ticket criado**: {canal.mention}", color=0x00ff00)
        await interaction.response.send_message(embed=embed_res, ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="🔒 Ticket Fechado", description="Este ticket será deletado em 5s.", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        await interaction.channel.delete(delay=5)

# Comando REMOVIDO - painel auto no on_ready

# --------------- COMANDO DE TESTE ----------------
@bot.command()
async def ping(ctx):
    await ctx.send('Pong! Funcionando 24/7.')

# --------------- RUN ----------------
bot.run(os.getenv('DISCORD_TOKEN'))
