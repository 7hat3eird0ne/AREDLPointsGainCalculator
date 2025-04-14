# Info
Hi, this small project I am making for fun uses [AREDL](https://aredl.net) (All Rated Extreme Demons List, list made for game Geometry Dash sorting the hardest levels in the game) API so that it can calculate amount of AREDL points you would get under assumption that you would beat any level you want, also taking into account packs.

## How to use
Running the APGC.py file with python (requires requests module) will ask you for AREDL profile username (in the exact spelling as on the website) and after that the level(s) you want to calculate the points you gain from, which you can enter in using:
- the level placement, just enter the standalone number (1 for the hardest level, 10 for the tenth, etc...)
- the level in game ID, enter the ID and then put at the end "_"
    - to search for 2 player option also add "2p"
- or the level name, enter the exact level name and it will find the hardest level with that name
    - to search for a level, which shares its name with other levels, add a bracket in style of "(CREATORUSERNAME)" or "(2P/Solo)" in the exact same way as on the website

## APGCv2.py
This is a slightly remade version of the first calculator, which will support multiple levels and will have bit more cleaner code. Right now running it raises NotImplementedError.