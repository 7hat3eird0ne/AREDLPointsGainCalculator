import requests
import time
from copy import deepcopy

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

def userAccess(username: str)-> tuple|None:
    if not isinstance(username, str):
        raise TypeError
    delete = False
    clanlessUser = ''
    for i in username:
        if i == '[':
            delete = True
        if not delete:
            clanlessUser += i
        if i == ']':
            delete = False
    qUsername = urlConvert(clanlessUser.strip())
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

def initialsSequences(sequences: str, levelList: list|None = None)-> tuple:
    if levelList is None:
        levelList = requests.get('https://api.aredl.net/v2/api/aredl/levels').json()
    if not isinstance(sequences, str) or not isinstance(levelList, list):
        raise TypeError
    sequences = sequences.strip().lower()
    if len(sequences) == 0:
        return ()
    currentsequencesIndex = 0
    h = 0
    result = []
    while h < len(levelList):
        i = levelList[h]
        levelName = i['name'].strip().lower()
        if levelName[0] == sequences[currentsequencesIndex]:
            currentsequencesIndex += 1
            if currentsequencesIndex == len(sequences):
                currentsequencesIndex = 0
                result.append(tuple(range(h+2-len(sequences),h+2)))
                h -= len(sequences)-1
        elif levelName[0] == sequences[0]:
            currentsequencesIndex = 1
            if currentsequencesIndex == len(sequences):
                result.append(tuple(range(h+2-len(sequences),h+2)))
                h -= len(sequences)            
        else:
            currentsequencesIndex = 0
            
        h += 1
    return tuple(result)

def sequenceInfo():
    while True:
        sequences = input('Enter sequence<')
        levelList = requests.get('https://api.aredl.net/v2/api/aredl/levels').json()
        result = initialsSequences(sequences, levelList)
        if len(result) == 0:
            print('No result found')
            continue
        records = []
        acrossRecords = []
        fullFirst = True
        for i in result:
            first = True
            for j in i:
                print('-', end='')
                if first:
                    print(end=' ')
                    first = False
                print(j, end='')
            print('\n  - Levels:')
            for j in i:
                levelData = levelList[j-1]
                print('    - ' + levelData['name'])
                if len(levelData['tags']) == 0:
                    print('      - No Tags')
                else:
                    for k in levelData['tags']:
                        print('      - ' + k)
            first = True
            for j in i:
                levelId = levelList[j-1]['id']
                newRecords = requests.get(f'https://api.aredl.net/v2/api/aredl/levels/{levelId}/records').json()
                newRecords = list(map(lambda x : x['submitted_by']['global_name'], newRecords))
                if fullFirst:
                    first = False
                    fullFirst = False
                    records = newRecords
                    acrossRecords = newRecords
                    continue
                elif first:
                    first = False
                    records = newRecords
                    continue
                tempRecords = records.copy()
                ch = 0
                for h in range(len(tempRecords)):
                    i = tempRecords[h]
                    if not i in newRecords:
                        records.pop(ch)
                    else:
                        ch += 1
                tempRecords = acrossRecords.copy()
                ch = 0
                for h in range(len(tempRecords)):
                    i = tempRecords[h]
                    if not i in newRecords:
                        acrossRecords.pop(ch)
                    else:
                        ch += 1
            print('  - Completed by:')
            if len(records) == 0:
                print('    - None')
            else:
                for i in records:
                    print('    - ' + i)
            print()
        if False:
            print('- All sequences completed by:')
            if len(acrossRecords) == 0:
                print('  - None')
            else:
                for i in acrossRecords:
                    print('  - ' + i)

def levelPointsAddition(levelPoses: set, username: str = '', profileData: dict|None = None, levelList: list|None = None, packsList: list|None = None)-> tuple:
    if levelList is None:
        levelList = requests.get('https://api.aredl.net/v2/api/aredl/levels').json()
    if not isinstance(levelPoses, set) or not isinstance(username, str):
        raise TypeError
    else:
        for i in levelPoses:
            if not isinstance(i, int):
                raise TypeError
            elif i < 1 or i >= len(levelList):
                raise IndexError('Placement(s) out of bounds of the list')

    levelPoses = set(map(lambda x : x - 1, levelPoses))
    if profileData is None:
        profileData = userAccess(username)[0]
    if packsList is None:
        packsList = requests.get('https://api.aredl.net/v2/api/aredl/pack-tiers').json()
    levelPacks = dict()
    points = 0
    levelsBeaten = list(map(lambda x : x['level']['position'], profileData['records']))
    for i in levelPoses:
        levelData = levelList[i]
        if levelData['legacy']:
            levelPoses.remove(i)
            continue
        points += levelData['points']
        for j in requests.get(f'https://api.aredl.net/v2/api/aredl/levels/{urlConvert(levelData['id'])}/packs').json():
            if not j['id'] in levelPacks.keys():
                levelPacks[j['id']] = j
        levelsBeaten.append(i+1)
    packPoints = 0
    #make nameBased = True a comment once v2 of API officialy releases, since right now for some reason IDs of same tiers/packs in different areas do not match sometimes, this can be left on but it is recomended to remove nameBased if the ids are more stable then
    nameBased = False
    nameBased = True
    for i in levelPacks.values():
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
                            completedLevelsPack.append(not(l['position'] in levelsBeaten))
                        if not any(completedLevelsPack):
                            points += k['points']
                            packPoints += k['points']
    return points, packPoints

def main():
    usernameSet = False
    levelList = requests.get('https://api.aredl.net/v2/api/aredl/levels').json()
    packsList = requests.get('https://api.aredl.net/v2/api/aredl/pack-tiers').json()
    levelPoses = []
    guest = False
    modes = {
        0: [sequenceInfo, 'Sequence Finder']
    }
    print('Do "?" for help')
    while True:
        if not usernameSet:
            username = input('Enter your username>')
            if len(username.strip()) == 0:
                guest = True
                profileData = {'records':[]}
                lbProfileData = None
                usernameSet = True
                print('Entered guest mode')
                continue
            userData = userAccess(username)
            if userData is None:
                print('Profile not found')
                continue
            rawUserData = []
            for i in userData:
                rawUserData.append(deepcopy(i))
            profileData = userData[0]
            lbProfileData = userData[1]
            usernameSet = True
            guest = False
            print('Profile found')
        levelsBeaten = list(map(lambda x : x['level']['position'], profileData['records']))
        levelName = ''
        skipSearch = False
        calculatePoints = False
        assumeAsBeaten = False
        completePointCalc = False
        levelPos = input('Enter a command>')
        levelPos = levelPos.strip()
        if len(levelPos) == 0:
            print('No command entered')
            continue

        elif levelPos[0] == '?':
            print('List of available commands:')
            print(' - "?" - prints this message')
            print(' - "#" - lets you change your username*')
            print(' - "." - refreshes all lists which have been stored to remove useless additional requests being called*')
            print(' - "-XXX" - adds a new level and calculates')
            print('  - "-" - calculates without adding new level, if no levels are present does nothing (also resets everything)')
            print('  - "-%" - same as "-" but calculates the entire percentage manually, can be used if points are being given unreliably, takes around 10 seconds for 50 levels')
            print(' - ":XXX" - adds a new level and assumes it as beaten')
            print('  - ":" - assumes all levels as beaten')
            print(' - ",M" - temporarily enters a different mode, then by running EOFError or keyboard interupt (to actually interupt, do it twice) you can exit (does not affect the main mode)')
            for key, value in modes.items():
                print(f'  - ",{str(key)}" - {value[1]}')
            print('* commands with asterisk are not runnable when there is one or more levels stored waiting for calculation')

        elif levelPos[0] == '#':
            if len(levelPoses) == 0:
                usernameSet = False 
                continue
            else:
                print('Unable to run when there is a level waiting for calculation')
                continue

        elif levelPos[0] == '.':
            if len(levelPoses) == 0:
                levelList = requests.get('https://api.aredl.net/v2/api/aredl/levels').json()
                packsList = requests.get('https://api.aredl.net/v2/api/aredl/pack-tiers').json()
                if not guest:
                    userData = userAccess(username)
                    if userData is None:
                        print('Profile not found')
                        usernameSet = False
                        continue
                    rawUserData = []
                    for i in userData:
                        rawUserData.append(deepcopy(i))
                    profileData = userData[0]
                    lbProfileData = userData[1]
                    continue
                else:
                    profileData = {'records':[]}
                    lbProfileData = None
            else:
                print('Unable to run when there is a level waiting for calculation')
                continue

        elif levelPos == '-':
            calculatePoints = True
            skipSearch = True
        elif levelPos == '-%':
            calculatePoints = True
            skipSearch = True
            completePointCalc = True
        elif levelPos[0] == '-':
            calculatePoints = True
            levelPos = levelPos[1:]
        
        elif levelPos == ':':
            skipSearch = True
            for i in levelPoses:
                profileData['records'].append({'level':{'position':i}})
            print(f'All levels ({len(levelPoses)}) assumed to be beaten and removed')
            levelPoses = []
        elif levelPos[0] == ':':
            assumeAsBeaten = True
            levelPos = levelPos[1:]

        elif len(levelPos) == 1:
            pass

        elif levelPos[0] == ',' and levelPos[1:].isdecimal():
            if not int(levelPos[1:]) in modes.keys():
                print('Invalid mode')
            else:
                print(f'Entering {modes[int(levelPos[1:])][1]}')
                try:
                    modes[int(levelPos[1:])][0]()
                except (KeyboardInterrupt, EOFError):
                    print('Exitting the mode (raise error again to quit)')
                except:
                    print('Unknown error happened')

        if not skipSearch:
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
            levelName = levelList[levelPos]['name']
            levelPlacemenet = levelPos + 1
            if levelPos+1 in levelsBeaten or levelPos+1 in levelPoses:
                print(f'{levelName} (#{levelPlacemenet}) already beaten/in the list, ignored')
            else:
                if assumeAsBeaten:
                    profileData['records'].append({'level':{'position':levelPos+1}})
                    print(f'{levelName} (#{levelPlacemenet}) assumed to be beaten')
                else:
                    levelPoses.append(levelPos+1)
                    print(f'{levelName} (#{levelPlacemenet}) added to the list, current amount of levels stored: {len(levelPoses)}')

        if calculatePoints:
            setLevelPoses = set()
            setLevelsFicTotal = set()
            setLevelsReal = set()
            for i in levelPoses:
                setLevelPoses.add(i)
            for i in profileData['records']:
                if not 'id' in i.keys():
                    setLevelsFicTotal.add(i['level']['position'])
                else:
                    setLevelsReal.add(i['level']['position'])
            setLevelsFicTotal = setLevelsFicTotal.union(setLevelPoses)
            if len(setLevelPoses) == 0:
                print('No levels to be calculated')
            else:
                try:
                    start = time.time()
                    totalPoints = levelPointsAddition(setLevelPoses, '', profileData, levelList, packsList)
                    packPoints = totalPoints[1]
                    totalPoints = totalPoints[0]
                    ficPoints = levelPointsAddition(setLevelsFicTotal, '', profileData, levelList, packsList)
                    ficPoints = ficPoints[0]
                    if completePointCalc:
                        prevPoints = levelPointsAddition(setLevelsReal, '', profileData, levelList, packsList)[0]
                    end = time.time()
                    calctime = int(1000*(end-start))
                    if (1000*(end-start))%1 != 0:
                        calctime += 1
                    print(str(calctime) + 'ms')
                except:
                    print('Point calculation failed')
                else:
                    if not completePointCalc:
                        if lbProfileData is None:
                            prevPoints = 0
                        else:
                            prevPoints = lbProfileData['total_points']-1
                    levelNames = ''
                    for i in levelPoses:
                        levelNames += ', ' + levelList[i-1]['name'] + ' (#' + str(i) + ')'
                    levelNames = levelNames[2:]
                    print(f'{totalPoints/10} points ({packPoints/10} pack points) gained on completion of {levelNames}, resulting in total amount of points: {(ficPoints + prevPoints)/10} (Global total: {prevPoints/10})')
                    levelPoses = []
            if guest:
                profileData = {'records':[]}
                lbProfileData = None
            else:
                profileData = rawUserData[0]
                lbProfileData = rawUserData[1]
            continue

if __name__ == '__main__':
    main()