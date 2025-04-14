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

def levelPlacementSearch(query: str)-> int:
    pass

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
        levelIsId = False
        player2 = False
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
        elif not levelPos.isdecimal():
            bracketless = False
            if len(levelPos) > 3:
                if levelPos[-3:] == '_2p' and levelPos[:-3].isdecimal():
                    levelIsId = True
                    player2 = True
            if not levelIsId:
                found = False
                if levelPos[-1] != ')':
                    bracketless = True
                    searchedName = bracketRemover(levelPos).lower()
                for i in levelList:
                    if bracketless:
                        if bracketRemover(i['name']).lower() == searchedName:
                            levelPos = i['position'] - 1
                            found = True
                            break
                    else:
                        if i['name'].lower() == levelPos.lower():
                            levelPos = i['position'] - 1
                            found = True
                            break
                if not found:
                    print('Level with that name not found')
                    continue
            else:   
                levelPos = int(levelPos[:-3]) - 1
        else:
            levelPos = int(levelPos) - 1
        if levelPos < 0 or levelPos >= len(levelList):
            suffix = ''
            if player2:
                suffix = '_2p'
            levelData = requests.get(f'https://api.aredl.net/v2/api/aredl/levels/{str(levelPos+1) + suffix}').json()
            if 'message' in levelData.keys():
                print('Placement out of bounds')
                continue
            else:
                levelPos = levelData['position'] - 1
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