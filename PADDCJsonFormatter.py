import json
import io
import argparse

def replaceArray(jsonString):
    curr = 1        # first character should be [
    last = 1
    res = "{"
    itemCount = 0
    while curr < jsonString:
        c = jsonString[curr]
        res += str(itemCount) + ":"
        while c != "," or "[":
            res += c
            curr += 1
            
        
            

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
            res += replaceArray(jsonString[curr:])
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
	
	
def leaderJsonToFirebase(leaderJson):
    res = "\"leader_skills\":{"
    
    for leader in leaderJson:
        res += addLeader(leader) + ","
        
    return res[:-1] + "}"
    
def addLeader(leader):
    mName = leader["name"]
    mDescription = leader["description"]
    mSkills =  str(leader["skills"])[1:-1]
    
    res = "\"{name}\":{{"
    res += "\"description\":\"{description}\","
    res += "\"skills\":{skills}"
    res += "}}"
    return res.format(name=mName, description=mDescription, skills=mSkills)

def main():
    parser = argparse.ArgumentParser(description="Reformats json for Firebase")
    parser.add_argument("-m", required=True,
                        help="The monster info json file from https://www.padherder.com/api/monster")
    parser.add_argument("-l", required=True,
                        help="The leaderskill json file")
    parser.add_argument("-o", required=True, help="Output file name")
    args = parser.parse_args()
    
    monsterFile = open(args.m)
    monsterJson = json.load(monsterFile)
    monsterFile.close()
    
    leaderFile = open(args.l)
    leaderJsonString = leaderFile.read()
    leaderFile.close()
    leaderJsonString = removeJsonArrays(leaderJsonString)
    leaderJson = json.loads(leaderJsonString)
    
    
    res = "{"
    res += monsterListToFirebase(monsterJson) + ","
    res += leaderJsonToFirebase(leaderJson)
    res += "}"
    outFile = open("firebaseJson.json", "w", encoding="utf-8")
    outFile.write(res)
    outFile.close()
    


if __name__ == "__main__":
    main()