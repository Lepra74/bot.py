import discord
import json
import requests
import asyncio

# Cargar configuración
with open("config.json") as f:
    config = json.load(f)

TOKEN = config["discord_token"]
CHANNEL_ID = int(config["channel_id"])
INTERVAL = config["interval"]

# Cargar productos
with open("products.json") as f:
    products = json.load(f)

client = discord.Client(intents=discord.Intents.default())
last_prices = {}

async def check_prices():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        for product in products:
            try:
                url = f"https://www.simcompanies.com/api/v3/market/1/{product['id']}/"
                response = requests.get(url).json()
                market_data = response[0]["price"] if response else None

                if market_data is None:
                    continue

                last_prices[product["id"]] = market_data

                if market_data <= product["min_price"]:
                    await channel.send(f"💰 Alerta: {product['name']} bajo el umbral: {market_data}")
                elif market_data >= product["max_price"]:
                    await channel.send(f"📈 Alerta: {product['name']} sobre el umbral: {market_data}")

            except Exception as e:
                print(f"Error al obtener datos: {e}")

        await asyncio.sleep(INTERVAL)

@client.event
async def on_ready():
    print(f"Bot listo! Conectado como {client.user}")
    client.loop.create_task(check_prices())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!help"):
        await message.channel.send(
            "Comandos disponibles:\n"
            "!help - Mostrar ayuda\n"
            "!list - Listar productos y umbrales"
        )
    elif message.content.startswith("!list"):
        msg = "Productos monitoreados:\n"
        for p in products:
            msg += f"{p['name']}: min {p['min_price']} - max {p['max_price']}\n"
        await message.channel.send(msg)

client.run(TOKEN)
