import json
import re

def main():
    file = open("sampleLeaderSkills.json")
    leaderJson = json.load(file)
    
    if len(leaderJson) is 0:
        return
        
    ex1 = "Dark attribute cards HP x2.5, ATK x2, RCV x1.5. All attribute cards ATK x3.5 when reaching Dark & Water combos."
    ex2 = "Attacker & Devil type cards HP x2, ATK x2. All attribute cards ATK x3.5 when reaching Fire & Water combos."
    ex3 = "Fire attribute & God type cards HP x1.5, ATK x2.5."
    ex4 = "God, Attacker & Devil type cards HP x1.5, ATK x3.5. All attribute cards ATK x2, RCV x2 when reaching Dark & Water combos."
    ex5 = "Fire & Water attribute cards ATK x2."
    ex6 = "Wood attribute cards ATK x3.5. Fire attribute cards HP x2."
    ex7 = "Wood attribute cards ATK x3.5. Fire attribute cards HP x2. ATK x1.5 for clearing each Wood orbs in a cross formation."
    ex8 = "Devil attribute cards All Stats x1.5. All attribute cards ATK x5 when attacking with Fire, Water, Wood & Dark orb types at the same time."
    #basic skills are just are type and attribute multipliers
    basicRePattern = r'''
        ((((
        fire|water|wood|light|dark      #attributes
        |god|balanced|attacker           #types
        |physical|devil|healer
        |dragon|machine) 
        \W+ (attribute\W+|type\W+)?)+   #repeat for all attributes and types
   
        cards\W+
        
        ((hp|atk|rcv|all[ ]stats)[ ]x\d([.]\d)?(,[ ])?)+)[.]?$) #followed by multipliers

    '''
    basicRe = re.compile(basicRePattern, re.IGNORECASE|re.VERBOSE)
    
    attributeRePattern = r'''
        (fire|water|wood|light|dark)
    
    '''
    attributeRe = re.compile(attributeRePattern, re.IGNORECASE|re.VERBOSE)
    result = "["
    for skillJson in leaderJson:
        name = skillJson["name"]
        des = skillJson["effect"]
        leaderSkillParts = des.split(". ")
        result += "{"
        result += "\"name\":\"" + name + "\","
        result += "\"description\":\"" + des + "\","
        result += "\"skill\":["
        
        i = 0
        while i < len(leaderSkillParts):
            part = leaderSkillParts[i]
            m = basicRe.search(part)
            print(part)
            if m:
                print("yes")
                basicStr = m.group().strip(" ")
                attributeM = attributeRe.findall(basicStr)
                result += "{\"skilltype\":\"basic\","
                result += "\"attribute\":["
                if attributeM:
                    for attribute in attributeM:
                        result += "\"" + attribute + "\","
                result = result.strip(",")
                result += "],"
                result += "\"type\":[],"
                result += "\"effect\":{},"
                result += "\"description\":\"" + basicStr + "\""
                result += "},"
            i += 1
        result = result.strip(",") # fencepost problem
        result += "]},"
    result = result.strip(",")
    result += "]"
    
    outFile = open("formattedLeaderSkills.json", "w", encoding="utf-8")
    outFile.write(result)
    outFile.close()
    file.close()
    
    

if __name__ == "__main__":
    main()