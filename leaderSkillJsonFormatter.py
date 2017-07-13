import json
import re

attributePattern = r'''
    (fire|water|wood|light|dark)

'''
attributeRe = re.compile(attributePattern, re.IGNORECASE|re.VERBOSE)

typePattern = r'''
    (
    god|balanced|attacker|physical
    |devil|healer|dragon|machine
    |evo material|awaken material
    |enhance material|redeemable material
    )
'''
typeRe = re.compile(typePattern, re.IGNORECASE|re.VERBOSE)

orbTypePattern = r'''
    (fire|water|wood|light|dark
    |heal|heart|jammer|moprtal[ ]poison|poison)
'''


#basic skills are just are type and attribute multipliers
basicRePattern = r'''
    ((((
    ''' + attributePattern + "|" + typePattern + ''')   #list of attributes and types
    
    \W+ (attribute\W+|type\W+)?)+   #repeat for all attributes and types

    cards\W+
    
    ((hp|atk|rcv|all[ ]stats)[ ]x\d+([.]\d+)?(,[ ])?)+)[.]?$) #followed by multipliers

'''
basicRe = re.compile(basicRePattern, re.IGNORECASE|re.VERBOSE)

basicMultiPattern = r'''
    cards[ ]
    (?:
    (?:all[ ]stats[ ]x(\d(?:[.]\d)?))|
    (?:HP[ ]x(\d+(?:[.]\d+)?))?                         #captures the HP multiplier
    (?:,[ ])?
    (?:atk[ ]x(\d+(?:\.\d+)?))?                         #captures atk multiplier
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?                         #captures rcv multiplier
    [.]?
    )
'''
basicMultiRe = re.compile(basicMultiPattern, re.IGNORECASE|re.VERBOSE)

genericComboBasePattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)                              #capture atk multiplier
    [ ]at[ ](\d+)[ ]combos                              #capture base start combo
'''
genericComboScalePattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)                              #capture scaling mutliplier
    [ ]for[ ]each[ ]additional[ ]combo,
    [ ]up[ ]to[ ]atk[ ]x(\d+(?:\.\d+)?)[ ]at[ ]         #capture multiplier limit
    (\d+)[ ]combos                                      #capture combo limit
'''

connectedPattern = r'''
    (?:atk[ ]x(\d+(?:\.\d+)?))?                         #capture atk multi
    (?:,[ ])?                                               
    (?:rcv[ ]x(\d+(?:\.\d+)?))?                         #capture rcv multi
    [ ]when[ ]simultaneously[ ]clearing[ ]
    (\d+)[ ]connected[ ]\w+(?:[ ]or[ ]\w+)?[ ]orbs      #capture beginning count
'''

connectedScalePattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)                              #capture atk scale
    [ ]for[ ]each[ ]additional[ ]orb,
    [ ]up[ ]to[ ]atk[ ]x (\d+(?:\.\d+)?)                #capture max atk
    [ ]at[ ](\d+)[ ]connected[ ]orb                     #capture max count
'''

def getBasicSkill(regexMatches):
    result = ""
    basicStr = regexMatches.group().strip(" ")
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

    multiplierM = basicMultiRe.search(basicStr)
    hp = 1
    atk = 1
    rcv = 1
    if multiplierM:
        if multiplierM[1]:
            hp = multiplierM[1]
            atk = multiplierM[1]
            rcv = multiplierM[1]
        else:
            hp = multiplierM[2] if multiplierM[2] else 1
            atk = multiplierM[3] if multiplierM[3] else 1
            rcv = multiplierM[4] if multiplierM[4] else 1
    result += "\"effect\":{"
    result += "\"hp\":" + str(hp) + ","
    result += "\"atk\":" + str(atk) + ","
    result += "\"rcv\":" + str(rcv)

    result += "},"
    result += "\"description\":\"" + basicStr + "\""
    result += "},"
    return result
    
def getGenericComboSkill(baseMatches, scaleMatches):
    baseAtkMulti = baseMatches[1]
    baseComboStart = baseMatches[2]
    atkScale = scaleMatches[1]
    atkMax = scaleMatches[2]
    comboMax = scaleMatches[3]
    result = "{\"skilltype\":\"combo\","
    result += "\"effect\":{"
    result += "\"atk_scale_multi_type\":\"additive\","
    result += "\"atk_scale\":" + atkScale + ","
    result += "\"min_atk\":" + baseAtkMulti + ","
    result += "\"max_atk\":" + atkMax + ","
    result += "\"start_combo\":" + baseComboStart + ","
    result += "\"end_combo\":" + comboMax
    result += "},"
    result += "\"description\":\"" + baseMatches[0] + ". " + scaleMatches[0] + "\""
    result += "}"
    return result

def getConnectedCombo(baseMatches, scaleMatches):
    print("CONNECTED")
    result = "{\"skilltype\":\"connected\","
    result += "\"description\":\"" + baseMatches[0]
    if scaleMatches:
        result += ". " + scaleMatches[0]
        
        
    minAtk = baseMatches[1]
    startCount = baseMatches[3]
    rcv = baseMatches[2] if baseMatches[2] else 1
    atkScale = 0
    maxAtk = minAtk
    endCount = startCount  
    if scaleMatches:
        atkScale = scaleMatches[1]
        maxAtk = scaleMatches[2]
        endCount = scaleMatches[3]
    
    result += "\","
    result += "\"effect\":{"
    result += "\"atk_scale_type\":\"additive\","
    result += "\"atk_scale\":" + str(atkScale) + ","
    result += "\"min_atk\":" + str(minAtk) + ","
    result += "\"max_atk\":" + str(maxAtk) + ","
    result += "\"start_count\":" + str(startCount) + ","
    result += "\"end_count\":" + str(endCount) + ","
    result += "\"rcv\":" + str(rcv)
    result += "}"
    result += "},"
    return result
    
def main():
    file = open("sampleLeaderSkills.json")
    leaderJson = json.load(file)
    
    if len(leaderJson) is 0:
        return
    
    
    
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
            i += 1
            basicM = basicRe.search(part)
            if basicM:
                result += getBasicSkill(basicM)
                continue
            
            genericComboBaseRe = re.compile(genericComboBasePattern, re.IGNORECASE|re.VERBOSE)
            genericComboBaseM = genericComboBaseRe.search(part)
            if genericComboBaseM:
                scalePart = leaderSkillParts[i]     #i already incremented
                genericComboScaleRe = re.compile(genericComboScalePattern, re.IGNORECASE|re.VERBOSE)
                genericComboScaleM = genericComboScaleRe.search(scalePart)
                result += getGenericComboSkill(genericComboBaseM, genericComboScaleM)
                i += 1
                continue
                
            connectedRe = re.compile(connectedPattern, re.IGNORECASE|re.VERBOSE)
            connectedM = connectedRe.search(part)
            if connectedM:
                scalePart = leaderSkillParts[i] if i < len(leaderSkillParts) else None    #i already incremented
                if scalePart:
                    connectedScaleRe = re.compile(connectedScalePattern, re.IGNORECASE|re.VERBOSE)
                    connectedScaleM = connectedScaleRe.search(scalePart)
                    result += getConnectedCombo(connectedM, connectedScaleM)
                else:
                    result += getConnectedCombo(connectedM, None)
                i += 1
                continue
                
            print("NOT DONE: " + part)
        result = result.strip(",") # fencepost problem
        result += "]},"
        print()
    result = result.strip(",")
    result += "]"
    
    outFile = open("formattedLeaderSkills.json", "w", encoding="utf-8")
    outFile.write(result)
    outFile.close()
    file.close()
    


if __name__ == "__main__":
    main()