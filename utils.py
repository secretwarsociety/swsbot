# import os
import yaml
import sys
# import json
# import hashlib
# import hmac

# this is a pointer to the module object instance itself.
this = sys.modules[__name__]

# This way the config is always accessible at utils.config.
this.config = None

def load_config():
    with open("config.yaml", "r") as stream:
        try:
            this.config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Unable to load config.yaml")
            print(exc)
            exit(1)

    if not this.config:
        print("Unable to load config.yaml")
        exit(1)

    if not this.config.get('discord'):
        print("Missing discord section.")
        exit(1)

    discord = this.config['discord']
    for key in ['token']:
        if not discord.get(key):
            print("Discord section missing", key)
            exit(1)

    if not discord.get('guild'):
        this.config['discord']['guild'] = None

    if not this.config.get('search_url'):
        this.config['search_url'] = 'https://secretwarsociety.com/card_search.json/';

    return this.config
