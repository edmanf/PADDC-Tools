import json
import re

def main():
    file = open("sampleLeaderSkills.json")
    leaderJson = json.load(file)
    
    if len(leaderJson) is 0:
        return
    
    attributeRePattern = r'''
        (fire|water|wood|light|dark)
    
    '''
    attributeRe = re.compile(attributeRePattern, re.IGNORECASE|re.VERBOSE)
    
    typeRePattern = r'''
        (
        god|balanced|attacker|physical
        |devil|healer|dragon|machine
        |evo material|awaken material
        |enhance material|redeemable material
        )
    '''
    typeRe = re.compile(typeRePattern, re.IGNORECASE|re.VERBOSE)
    
    #basic skills are just are type and attribute multipliers
    basicRePattern = r'''
        ((((
        ''' + attributeRePattern + "|" + typeRePattern + ''')   #list of attributes and types
        
        \W+ (attribute\W+|type\W+)?)+   #repeat for all attributes and types
   
        cards\W+
        
        ((hp|atk|rcv|all[ ]stats)[ ]x\d([.]\d)?(,[ ])?)+)[.]?$) #followed by multipliers

    '''
    basicRe = re.compile(basicRePattern, re.IGNORECASE|re.VERBOSE)
    
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
                typeM = typeRe.findall(basicStr)
                
                result += "{\"skilltype\":\"basic\","
                result += "\"attribute\":["
                if attributeM:
                    for attribute in attributeM:
                        result += "\"" + attribute + "\","
                result = result.strip(",") + "],"
                result += "\"type\":["
                if typeM:
                    for type in typeM:
                        result += "\"" + type + "\","
                result = result.strip(",") + "],"

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