from typing import Optional

import discord
import utils
import logging
import requests

from discord import app_commands
discord.utils.setup_logging(level=logging.INFO)

logger = logging.getLogger('myclient')

GUILD = None
if utils.config['discord']['guild']:
    GUILD = discord.Object(id=utils.config['discord']['guild'])  # replace with your guild id

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        if (GUILD):
            guild = await self.fetch_guild(GUILD.id)
            logger.info("Connecting only to Guild %s.", guild.name)
            # This copies the global commands over to your guild.
            self.tree.copy_global_to(guild=GUILD)
            await self.tree.sync(guild=GUILD)
        else:
            await self.tree.sync()


intents = discord.Intents.default()
client = MyClient(intents=intents)


class DefaultButton(discord.ui.Button):
    def __init__(self, custom_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_id = custom_id

    async def callback(self, interaction: discord.Interaction):
        embed = create_card_embed(0, self.view.cards[self.custom_id])
        await interaction.response.send_message('', embed=embed)
        return

class CardChoiceView(discord.ui.View):
    def __init__(self, cards):
        super().__init__(timeout=360)
        self.cards = cards
        number = 0
        for nid, card in cards.items():
            number += 1
            self.add_item(DefaultButton(label=f'Show #{number}', custom_id=nid))


def create_card_embed(number, card):
    if not number:
        title = f'{card["title"]} [{card["set"]}]'
    else:
        title = f'#{number}: {card["title"]} [{card["set"]}]'

    embed = discord.Embed(title=title, url=card['path'], description=card['subtitle'])
    if not number:
        embed.set_image(url=card['image'])
    else:
        embed.set_thumbnail(url=card['image'])

    fields = {
        'cost': 'Cost',
        'provides': 'Provides',
        'fighting': 'Fighting',
        'body': 'Body',
        'power': 'Power'
    }

    for key, label in fields.items():
        if card[key] != '' and card[key] is not None:
            embed.add_field(name=label, value = card[key])

    if card['text']:
        embed.add_field(name='Text', value=card['text'], inline=False)
    if card['flavor']:
        embed.add_field(name='Flavor', value=card['flavor'], inline=False)

    return embed

@client.tree.command()
@app_commands.describe(text='Text to search for')
async def search(interaction: discord.Interaction, text: str):
    """Searches for a card in the SWS database."""
    url = utils.config['search_url'] + text
    response = requests.get(url)
    cards = response.json()
    if not cards or len(cards) == 0:
        await interaction.response.send_message('No results found.')
        return

    embeds = []
    count = 0
    for nid, card in cards.items():
        count += 1
        embeds.append(create_card_embed(count, card))

    view = CardChoiceView(cards)
    await interaction.response.send_message('', embeds=embeds, view=view, ephemeral=True)



