import json
import io
import argparse

def replaceArray(jsonString):
    """
        Replaces json arrays with pseudo arrays for firebaseStr
        Example: ["Foo", "Bar"] -> {"0": "Foo", "1": "Bar"}
    """
    if jsonString[0] != "[" or jsonString[-1] != "]":
        # return None if its not a valid json array
        return None
        
    origIndex = 1
    resIndex = 1
    res = "{"
    itemCount = 0
    bracketCount = 0
    
    
    
    # check if its an object array or string array
    isJsonObjectArray = jsonString[origIndex] == "{"
    
    if not isJsonObjectArray:
        res += "\"" + str(itemCount) + "\":"
        resIndex += len(str(itemCount)) + 3
        
    while origIndex < len(jsonString):
        c = jsonString[origIndex]
        if c == "]":
            # because we recurse everytime we see "[", "]" is always a return
            res += "}"
            resIndex += 1
            origIndex += 1
            return (res, origIndex, resIndex)
        elif c == "[":
            subRes = replaceArray(jsonString[origIndex:])
            origIndex += subRes[1]
            resIndex += subRes[2]
            res += subRes[0]
        elif c == "{" and isJsonObjectArray:
            if bracketCount == 0:
                res += "\"" + str(itemCount) + "\":"
                resIndex += len(str(itemCount)) + 3
            bracketCount += 1
            res += c
            resIndex += 1
            origIndex += 1
        elif c == "}" and isJsonObjectArray and bracketCount == 1:
            # end of object in array reached
            res += c
            resIndex += 1
            origIndex += 1
            itemCount += 1
            bracketCount -= 1
        elif c == "}" and isJsonObjectArray:
            res += c
            resIndex += 1
            origIndex += 1
            bracketCount -= 1
        elif c == "," and jsonString[origIndex - 1] == "\"" and not isJsonObjectArray:
            # no arrays of mixed type so ", means you're in an array of strings
            itemCount += 1
            res += c + "\"" + str(itemCount) + "\":"
            resIndex += 2 + len(str(itemCount))
            origIndex += 1
            
        else:
            res += c
            resIndex += 1
            origIndex += 1
        

    print("DEBUG: WHY AM I HERE")
    return (res, origIndex)     # should not happen because string should always end in "]"
                 

def removeJsonArrays(jsonString):
    """ Takes a json string and returns a json string that is accetable
    by Firebase
    """
    curr = 0
    last = 0
    res = ""
    while curr < len(jsonString):
        if jsonString[curr] == "[":
            res += jsonString[last:curr]
            last = curr
            (subRes, curr, __ignore__) = replaceArray(jsonString[curr:])
            print(subRes)
            res += subRes.strip(",")
        curr += 1
    return res


def monsterListToFirebase(monsterJson):
    """ Returns a json string that has been formatted to work with Firebase
        monsterJson:    the original json file with monster info
    """
    firebaseStr = "\"monsters\" : {"
	
    for monster in monsterJson:
        firebaseStr += addMonster(monster) + ","
	
    #all except last character to fix fencepost comma
    firebaseStr = firebaseStr[:-1] + " }"
    return firebaseStr
    	
def addMonster(monster):
    mId = monster["id"]
    mName = monster["name"]
    mAtk = monster["atk_max"]
    mHp = monster["hp_max"]
    mRcv = monster["rcv_max"]
    mElement = monster["element"]
    mElement2 = monster["element2"] if monster["element2"] else -1
    types = [monster["type"], monster["type2"], monster["type3"]]
    types = [type for type in types if type is not None]
    mLeaderSkill = monster["leader_skill"] if monster["leader_skill"] else "N/A"
    
    res = " \"{id}\" : {{ \"name\" : \"{name}\", "
    res += "\"num\" : {id}, "
    res += "\"hp\" : {hp}, "
    res += "\"atk\" : {atk}, "
    res += "\"rcv\" : {rcv}, "
    res += "\"attributes\" : {{\"0\": {element}, \"1\": {element2}}}, "
    res += "\"leader_skill\" : \"{leaderSkill}\""
    res += "}}"
	
    return res.format(id=mId, name=mName, hp=mHp, atk=mAtk, rcv=mRcv,
                      element=mElement, element2=mElement2,
                      leaderSkill=mLeaderSkill)
	
def indexByName(leaderJson):
    res = "{"
    leaderArray = json.loads(leaderJson)
    for i in leaderArray:
        skill = leaderArray[i]
        
        name = skill["name"]
        description = skill["description"]
        
        res += "\"" + name + "\": {"
        res += "\"description\":\"" + description + "\","
        if "skills" in skill:
            res += "\"skills\":" + json.dumps(skill["skills"])
        res = res.strip(",") + "},"
    res = res.strip(",") + "}"
    return res
        
        
    
    
def leaderJsonToFirebase(leaderJson):
    res = "\"leader_skills\":"
    res += indexByName(removeJsonArrays(leaderJson))
    
    
    return res

def main():
    parser = argparse.ArgumentParser(description="Reformats json for Firebase")
    parser.add_argument("-m", required=True,
                        help="The monster info json file from https://www.padherder.com/api/monster")
    parser.add_argument("-l", required=True,
                        help="The leaderskill json file")
    parser.add_argument("-o", required=True, help="Output file name")
    args = parser.parse_args()
    
    monsterFile = open(args.m, encoding="utf-8")
    monsterJson = json.load(monsterFile)
    monsterFile.close()
    
    leaderFile = open(args.l, encoding="utf-8")
    leaderJsonString = leaderFile.read()
    leaderFile.close()
    
    
    
    res = "{"
    res += monsterListToFirebase(monsterJson) + ","
    res += leaderJsonToFirebase(leaderJsonString)
    res += "}"

    outFile = open(args.o, "w", encoding="utf-8")
    outFile.write(res)
    outFile.close()
    


if __name__ == "__main__":
    main()