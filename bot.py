#!/usr/bin/python3.8 -u
# bot.py

import os
import sys
# Make sure the working dir is where the app lives.
abspath = os.path.abspath(sys.argv[0])
dname = os.path.dirname(abspath)
os.chdir(dname)

import utils
config = utils.load_config()

import client
client.client.run(config['discord']['token'], log_handler=None)
