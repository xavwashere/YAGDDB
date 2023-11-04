# YAGDDB
Yet Another Geometry Dash Discord Bot - Interact with the GD servers through Discord!

# Info
YAGDDB is a Discord bot used for interfacing with the Geometry Dash servers. YAGDDB is powered by [gd.py](https://github.com/nekitdev/gd.py).

YAGDDB has a couple of cool features:
- Searching for levels
- Searching for users
- Demon list
- Player demon list
- Daily and weekly commands
- ...and many others!

# Commands

- /daily - Shows the current daily level (uses `create_level_embed()`).
- /weekly - Shows the current daily level (uses `create_level_embed()`).
- /search level <name> - Searches for a level with the specified level name/ID.
- /search user <name> - Searches for a user with the specified username/ID.
- /demonlist - Shows the top 10 levels on the Demonlist (https://pointercrate.com).
- /leaderboard - Shows the top 10 players on the Demonlist leaderboard (https://pointercrate.com)
- /checkmod <name> - Checks the specified user's moderator status.
- /settings - Allows you to change the settings of the bot, as well as add a webhook that is triggered when a level is rated (currently broken)

# Running

Simply clone the repo, add an environment variable named YAGDDB and set the value to the bot token, then run `pip install -r requirements.txt` and `python yagddb.py`.
