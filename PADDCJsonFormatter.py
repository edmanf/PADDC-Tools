import json
import io

def monsterListToFirebase():
	file = open("padjson.json")
	monstersJson = json.load(file)
	firebaseStr = "{ \"monsters\" : {"
	
	for monster in monstersJson:
		firebaseStr += addMonster(monster) + ","
	
	#all except last character to fix fencepost
	firebaseStr = firebaseStr[:-1] + " } }"
		 
	outFile = open("firebaseJson.json", "w", encoding="utf-8")
	outFile.write(firebaseStr)

		
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
	
	res = " \"{id}\" : {{ \"name\" : \"{name}\", "
	res += "\"num\" : {id}, "
	res += "\"hp\" : {hp}, "
	res += "\"atk\" : {atk}, "
	res += "\"rcv\" : {rcv}, "
	res += "\"attributes\" : {{\"0\": {element}, \"1\": {element2}}}"
	res += "}}"
	
	return res.format(id=mId, name=mName, hp=mHp, atk=mAtk, rcv=mRcv, element=mElement, element2=mElement2)
	
	
monsterListToFirebase()