raise NotImplementedError

import requests

ascii_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def bracketRemover(string):
    inBracket = False
    resultString = ''
    for j in string:
        if j == '(':
            inBracket = True
        if not inBracket:
            resultString += j
        elif j == ')':
            inBracket = False
    return resultString.strip()

def urlConvert(string: str)-> str:
    if not isinstance(string, str):
        raise TypeError
    urlEscapeChars = {' ', '<', '>', '#', '%', '&', '$', '@', '=', '+', '{', '}', '/', '|', '\\', '^', '~', '[', ']', '\'', ';', ':', '?'}    
    safeChars = set(list(ascii_letters)).union(set(list(digits)), {'$', '-', '_', '.', '+', '!', '*', '\'', '(', ')', ','}, urlEscapeChars)
    queryString = ''
    for i in string:
        if not  i in safeChars:
            raise ValueError('Not convertable into a URL friendly string')
        elif i in urlEscapeChars:
            queryString += '%' + hex(ord(i))[2:].upper()
        else:
            queryString += i
    return queryString

def userAccess(username: str)-> dict|None:
    if not isinstance(username, str):
        raise TypeError
    qUsername = urlConvert(username.strip())
    users = requests.get(f'https://api.aredl.net/v2/api/users?name_filter={qUsername}').json()
    if len(users['data']) == 0:
           return None
    id = users['data'][0]['id']
    profile = requests.get(f'https://api.aredl.net/v2/api/aredl/profile/{id}').json()
    leaderboard = requests.get(f'https://api.aredl.net/v2/api/aredl/leaderboard?name_filter={qUsername}').json()
    if len(leaderboard['data']) == 0:
        lbProfile = None
    else:
        lbProfile = leaderboard['data'][0]
    return profile, lbProfile

def levelPointsAddition(username: str, levelPos: int, profileData: dict|None = None, levelList: list|None = None, packsList: list|None = None)-> int:
    if not isinstance(levelPos, int) or not isinstance(username, str):
        raise TypeError
    levelPos -= 1
    if profileData is None:
        profileData = userAccess(username)[0]
    else:
        username = profileData['global_name']
    if levelList is None:
        levelList = requests.get('https://api.aredl.net/v2/api/aredl/levels').json()
    if packsList is None:
        packsList = requests.get('https://api.aredl.net/v2/api/aredl/pack-tiers').json()
    
    if levelPos < 0 or levelPos >= len(levelList):
        raise ValueError('Placement outside of bounds')
    levelData = levelList[levelPos]
    if levelData['legacy']:
        return 0.0
    else:
        points = levelData['points']
        levelId = levelData['id']
        qLevelId = urlConvert(levelId)
        levelsBeaten = list(map(lambda x : x['level']['position'], profileData['records']))
        levelPacks = requests.get(f'https://api.aredl.net/v2/api/aredl/levels/{qLevelId}/packs').json()
        nameBased = False
        nameBased = True
        for i in levelPacks:
            pack = i['id']
            tier = i['tier']['id']
            packName = i['name']
            tierName = i['tier']['name']
            for j in packsList:
                if j['id'] == tier or (nameBased and j['name'] == tierName):
                    for k in j['packs']:
                        if k['id'] == pack or (nameBased and k['name'] == packName):
                            completedLevelsPack = []
                            for l in k['levels']:
                                completedLevelsPack.append(not(l['position'] in levelsBeaten or l['position'] == levelPos + 1))
                            if not any(completedLevelsPack):
                                points += k['points']
        return points

def levelPlacementSearch(query: str, levelList: list|None = None)-> int:
    if not isinstance(query, str):
        raise TypeError
    if levelList is None:
        levelList = requests.get('https://api.aredl.net/v2/api/aredl/levels').json()

    #GUIDE TO QUERY IN LEVEL PLACEMENT SEARCHING:
    # A query representing an int will search for a level which is at the placement in the query (starting at 1 going up), an integer outside of the bounds of the list raises IndexError
    # A query representing an int BUT with either _ or _2p appended at the end will search for a level with a GD ID in the query, _ takes solo or regular results, _2p gives 2 player placement, _2p with non-2player level will give the regular version, raises KeyError if  the ID is not present on the list
    # A query with the exact name of the level will search for the hardest level with the exact name, if the query ends with ")" (meaning brackets are in the query), it will search for the exact same name as shown on the website, raises KeyError if it fails to find a level with the name

    if query.isdecimal():
        levelPos = int(query) - 1
        if levelPos < 0 or levelPos >= len(levelList):
            raise IndexError('Placement out of bounds')
    else:
        query = (query.lower()).strip()
        levelIsId = False
        player2 = False
        if len(query) > 3:
            if query[-3:] == '_2p' and query[:-3].isdecimal():
                levelIsId = True
                player2 = True
        if len(query) > 1:
            if query[:-1].isdecimal() and query[-1] == '_':
                levelIsId = True
                player2 = False
        if levelIsId and player2:
            levelData = requests.get(f'https://api.aredl.net/v2/api/aredl/levels/{query}').json()
            if 'position' in levelData.keys():
                levelPos = levelData['position'] - 1
            else:
                levelData = requests.get(f'https://api.aredl.net/v2/api/aredl/levels/{query[:-3]}').json()
                if 'position' in levelData.keys():
                    levelPos = levelData['position'] - 1
                else:
                    raise KeyError('Level ID is not present in the list')
        elif levelIsId:
            levelData = requests.get(f'https://api.aredl.net/v2/api/aredl/levels/{query[:-1]}').json()
            if 'position' in levelData.keys():
                levelPos = levelData['position'] - 1
            else:
                raise KeyError('Level ID is not present in the list')
        else:
            found = False
            if query[-1] != ')':
                bracketless = True
                searchedName = bracketRemover(query).strip()
            else:
                bracketless = False
                searchedName = query.strip()
            for i in levelList:
                if bracketless:
                    if bracketRemover(i['name']).lower() == searchedName:
                        levelPos = i['position'] - 1
                        found = True
                        break
                else:
                    if i['name'].lower() == searchedName:
                        levelPos = i['position'] - 1
                        found = True
                        break
            if not found:
                raise KeyError('Level with that name not found')
    return levelPos


def main():
    usernameSet = False
    levelList = requests.get('https://api.aredl.net/v2/api/aredl/levels').json()
    packsList = requests.get('https://api.aredl.net/v2/api/aredl/pack-tiers').json()
    while True:
        if not usernameSet:
            username = input('Enter your username (without clan)-')
            userData = userAccess(username)
            if userData is None:
                print('Profile not found')
                continue
            profileData = userData[0]
            lbProfileData = userData[1]
            usernameSet = True
        levelPos = input('Level placement (1 for the hardest level) (1r), "#" to change username (2r), "." to refresh (4r)-')
        levelPos = levelPos.strip()
        if len(levelPos) == 0:
            print('No command entered')
            continue
        elif levelPos[0] == '#':
            usernameSet = False
            continue
        elif levelPos[0] == '.':
            levelList = requests.get('https://api.aredl.net/v2/api/aredl/levels').json()
            packsList = requests.get('https://api.aredl.net/v2/api/aredl/pack-tiers').json()
            userData = userAccess(username)
            if userData is None:
                print('Profile not found')
                continue
            profileData = userData[0]
            lbProfileData = userData[1]
            usernameSet = True
            continue
        else:
            try:
                levelPos = levelPlacementSearch(levelPos, levelList)
            except KeyError:
                print('Level with that name or ID not found')
                continue
            except IndexError:
                print('Placement outside of bounds of the list')
                continue
            except:
                print('Unknown error happened')
                continue
        levelsBeaten = list(map(lambda x : x['level']['position'], profileData['records']))
        levelName = levelList[levelPos]['name']
        if levelPos+1 in levelsBeaten:
            print(f'{levelName} already beaten - 0.0 points gained')
        try:
            totalPoints = levelPointsAddition('', levelPos + 1, profileData, levelList, packsList)
        except:
            print('Point calculation failed')            
            continue
        if lbProfileData is None:
            prevPoints = 0
        else:
            prevPoints = lbProfileData['total_points']-1
        print(f'{totalPoints/10} points gained on completion of {levelName}, resulting in total amount of points: {(totalPoints + prevPoints)/10}')

if __name__ == '__main__':
    main()