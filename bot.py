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
TICKET_CATEGORY_ID = SEU_ID_DA_CATEGORIA  # <<< TROCAR pelo ID da categoria

# ---------------- ON_READY ----------------
@bot.event
async def on_ready():
    bot.add_view(TicketView())  # mantém o painel de ticket após restart
    print(f'{bot.user} está online no Railway!')

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
        tipo = select.values[0]  # "duvidas" ou "denuncias"
        user = interaction.user
        guild = interaction.guild
        categoria = guild.get_channel(TICKET_CATEGORY_ID)

        if categoria is None:
            await interaction.response.send_message(
                "❌ Categoria de tickets não encontrada. Avise o administrador.",
                ephemeral=True
            )
            return

        # contador simples
        count = sum(1 for c in categoria.text_channels if c.name.startswith(tipo))
        nome_canal = f"{tipo}-{count+1:02d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        canal = await guild.create_text_channel(
            name=nome_canal,
            category=categoria,
            overwrites=overwrites,
            reason=f"Ticket {tipo} de {user}",
        )

        await canal.send(f"{user.mention}, seu ticket de **{tipo}** foi criado aqui.")
        await interaction.response.send_message(
            f"✅ Ticket **{tipo}** criado em {canal.mention}.", ephemeral=True
        )

@bot.command()
@commands.has_role(TICKET_ADMIN_ROLE)
async def ticket(ctx):
    embed = discord.Embed(
        title="🎫 Sistema de Tickets",
        description="Escolha abaixo o tipo de ticket que você deseja abrir.",
        color=0x3498db,
    )
    view = TicketView()
    await ctx.send(embed=embed, view=view)

# --------------- COMANDO DE TESTE ----------------
@bot.command()
async def ping(ctx):
    await ctx.send('Pong! Funcionando 24/7.')

# --------------- RUN ----------------
bot.run(os.getenv('DISCORD_TOKEN'))
