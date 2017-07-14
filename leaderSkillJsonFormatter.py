import json
import re

attributePattern = r'''
    (fire|water|wood|light|dark|all)

'''
attributeRe = re.compile(attributePattern, re.IGNORECASE|re.VERBOSE)

typePattern = r'''
    (
    god|balanced|attacker|physical
    |devil|healer|dragon|machine
    |evo material|awaken material
    |enhance material|redeemable material
    |all
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

scalingComboBasePattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)                              #capture atk multiplier
    [ ]at[ ](\d+)[ ]combos                              #capture base start combo
'''
scalingComboScalePattern = r'''
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

noSkyfallPattern = r'''
    no[ ]skyfall[ ]matches
'''

boardSizePattern = r'''
    change[ ]the[ ]board[ ]to[ ](\d+)x(\d+)[ ]size        #captures col and row
'''

crossPattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)                              #captures atk mutliplier
    [ ]for[ ]clearing[ ](?:\w+[ ])+?
    orbs[ ]in[ ]a[ ]cross[ ]formation
'''

moveTimePattern = r'''
    (fixed|increases)[ ]                            #captures fixed or increases
    (?:\w+[ ])*?orb[ ]movement(?:[ ]\w+)+?[ ]
    (\d+(?:\.\d+)?)[ ]seconds                       #captures time value    
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
    atkScale = 0
    atkMax = baseAtkMulti
    comboMax = baseComboStart
    if scaleMatches:
        atkScale = scaleMatches[1]
        atkMax = scaleMatches[2]
        comboMax = scaleMatches[3]
    result = "{\"skilltype\":\"combo\","
    result += "\"effect\":{"
    result += "\"atk_scale_multi_type\":\"additive\","
    result += "\"atk_scale\":" + str(atkScale) + ","
    result += "\"min_atk\":" + str(baseAtkMulti) + ","
    result += "\"max_atk\":" + str(atkMax) + ","
    result += "\"start_combo\":" + str(baseComboStart) + ","
    result += "\"end_combo\":" + str(comboMax)
    result += "},"
    result += "\"description\":\"" + baseMatches[0] 
    if scaleMatches:
        result += ". " + scaleMatches[0]
    result += "\""
    result += "}"
    
    return result

def getConnectedCombo(baseMatches, scaleMatches):    
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
    
    orbTypeRe = re.compile(orbTypePattern, re.IGNORECASE|re.VERBOSE)
    orbTypeM = orbTypeRe.findall(baseMatches[0])
        
    result = "{\"skilltype\":\"connected\","
    result += "\"connected\":["
    # dont check for None, there must be an orbType
    for orbType in orbTypeM:
        result += "\"" + orbType + "\","
    result = result.strip(",") + "],"

    result += "\"effect\":{"
    result += "\"atk_scale_type\":\"additive\","
    result += "\"atk_scale\":" + str(atkScale) + ","
    result += "\"min_atk\":" + str(minAtk) + ","
    result += "\"max_atk\":" + str(maxAtk) + ","
    result += "\"start_count\":" + str(startCount) + ","
    result += "\"end_count\":" + str(endCount) + ","
    result += "\"rcv\":" + str(rcv) + ","
    result += "\"description\":\"" + baseMatches[0]
    if scaleMatches:
        result += ". " + scaleMatches[0]
    result += "\""
    result += "}"
    result += "},"
    return result
    
def getNoSkyfallSkill(match):
    result = "{\"skilltype\":\"skyfall\","
    result += "\"skyfall\":[\"no skyfall\"],"
    result += "\"description\":\"" + match[0] + "\""
    result += "},"
    return result
    
def getBoardSize(match):
    rows = match[1]
    cols = match[2]

    result = "{\"skilltype\":\"boardsize\","
    result += "\"boardsize\":{"
    result += "\"rows\":" + str(rows) + ","
    result += "\"cols\":" + str(cols)
    result += "},"
    result += "\"description\":\"" + match[0] + "\""
    result += "}"
    return result
    
def getCrossSkill(match):
    atkScale = match[1]
    description = match[0]
    
    orbTypeRe = re.compile(orbTypePattern, re.IGNORECASE|re.VERBOSE)
    orbTypeM = orbTypeRe.findall(description)
    
    
    result = "{\"skilltype\":\"cross\","
    result += "\"cross\":["
    
    #dont check for none, because there has to be an orb type
    for orbType in orbTypeM:
        result += "\"" + orbType + "\","
    result = result.strip(",") + "],"
    result += "\"effect\":{"
    result += "\"atk_scale_type\":\"multiplicative\","
    result += "\"atk_scale\":" + atkScale
    result += "},"
    
    result += "\"description\":\"" + description + "\""
    result += "}"
    return result
    
def getMoveTimeSkill(match):
    moveTimeType = "fixed" if match[1] == "Fixed" else "increase"

    result = "{\"skilltype\":\"move_time\","
    result += "\"move_time\":\"" + moveTimeType + "\","
    result += "\"effect\":{"
    result += "\"time\":" + match[2]
    result += "},"
    result += "\"description\":\"" + match[0] + "\""
    result += "}"
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
            scalingComboBaseRe = re.compile(scalingComboBasePattern, re.IGNORECASE|re.VERBOSE)
            scalingComboBaseM = scalingComboBaseRe.search(part)
            if scalingComboBaseM:
                if i < len(leaderSkillParts):
                    scalePart = leaderSkillParts[i]    #i already incremented
                    scalingComboScaleRe = re.compile(scalingComboScalePattern, re.IGNORECASE|re.VERBOSE)
                    scalingComboScaleM = scalingComboScaleRe.search(scalePart)
                    result += getGenericComboSkill(scalingComboBaseM, scalingComboScaleM)
                    i += 1
                else:
                    result += getGenericComboSkill(scalingComboBaseM, None)
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
                
            noSkyfallRe = re.compile(noSkyfallPattern, re.IGNORECASE|re.VERBOSE)
            noSkyfallM = noSkyfallRe.search(part)
            if noSkyfallM:
                result += getNoSkyfallSkill(noSkyfallM)
                continue
                
            boardSizeRe = re.compile(boardSizePattern, re.IGNORECASE|re.VERBOSE)
            boardSizeM = boardSizeRe.search(part)
            if boardSizeM:
                result += getBoardSize(boardSizeM)
                continue
                
            crossRe = re.compile(crossPattern, re.IGNORECASE|re.VERBOSE)
            crossM = crossRe.search(part)
            if crossM:
                result += getCrossSkill(crossM)
                continue
                
            moveTimeRe = re.compile(moveTimePattern, re.IGNORECASE|re.VERBOSE)
            moveTimeM = moveTimeRe.search(part)
            if moveTimeM:
                result += getMoveTimeSkill(moveTimeM)
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