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
PANEL_CHANNEL = 1469006850681995455  # Canal do painel

# ---------------- ON_READY ----------------
@bot.event
async def on_ready():
    print(f'{bot.user} está online no Railway!')
    
    # Painel ticket AUTO
    channel = bot.get_channel(PANEL_CHANNEL)
    if channel:
        await channel.purge(limit=50)  # limpa chat
        embed = discord.Embed(
            title="🎫 Sistema de Tickets", 
            description="**Selecione abaixo o tipo de ticket que deseja abrir:**", 
            color=0x3498db
        )
        view = TicketView()
        await channel.send(embed=embed, view=view)
        print("✅ Painel de tickets enviado!")
    else:
        print("❌ Canal do painel não encontrado!")
    
    bot.add_view(TicketView())  # mantém views após restart
    
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
    options=[
        discord.SelectOption(label="Dúvidas", value="duvidas", emoji="❓"),
        discord.SelectOption(label="Denúncias", value="denuncias", emoji="🚨"),
    ]
)
async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
    tipo = select.values[0]
    user = interaction.user
    guild = interaction.guild

    # Contador
    count = 1
    for ch in guild.channels:
        if isinstance(ch, discord.TextChannel) and ch.name.startswith(f"{tipo}-"):
            try:
                num = int(ch.name.split('-')[1])
                count = max(count, num + 1)
            except:
                pass
    nome_canal = f"{tipo}-{count:02d}"

    # Perms
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }

    # Cria canal
    category = guild.get_channel(TICKET_CATEGORY_ID)
    canal = await guild.create_text_channel(
        name=nome_canal,
        overwrites=overwrites,
        category=category
    )

    # Mensagem no novo ticket
    embed = discord.Embed(title=f"🎫 {tipo.title()}", description=f"{user.mention}, seu ticket foi criado!", color=0x00ff00)
    close_view = TicketCloseView()
    await canal.send(embed=embed, view=close_view)

    # Resposta + RESET select (volta placeholder)
    embed_res = discord.Embed(description=f"✅ **{tipo.title()}** criado: {canal.mention}", color=0x00ff00)
    await interaction.response.send_message(embed=embed_res, ephemeral=True)


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fechar", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket fechando em 5s...")
        await interaction.channel.delete(delay=5)

# --------------- COMANDO DE TESTE ----------------
@bot.command()
async def ping(ctx):
    await ctx.send('Pong! Funcionando 24/7.')

# --------------- RUN ----------------
bot.run(os.getenv('DISCORD_TOKEN'))
