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
    |evo[ ]material|awaken[ ]material
    |enhance[ ]material|redeemable[ ]material
    |all
    )
'''
typeRe = re.compile(typePattern, re.IGNORECASE|re.VERBOSE)

orbTypePattern = r'''
    (fire|water|wood|light|dark
    |heal|heart|jammer|mortal[ ]poison|poison)
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

basicPattern2 = r'''
    (?:hp[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    [ ]to[ ] ''' + typePattern + '''
    [ ]type[ ]cards
'''

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
    (\d+)[ ]connected[ ]\w+(?:[ ]or[ ].+?)?[ ]orbs      #capture beginning count
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
heartCrossPattern = r'''
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:reduce[ ]damage[ ]taken[ ]by[ ](\d+)%)?
    [ ]after[ ]matching[ ](?:heal|heart)[ ]orbs[ ]in[ ]a[ ]cross[ ]formation

'''

moveTimePattern = r'''
    (fixed|increases)[ ]                            #captures fixed or increases
    (?:\w+[ ])*?orb[ ]movement(?:[ ]\w+)+?[ ]
    (\d+(?:\.\d+)?)[ ]seconds                       #captures time value    
'''

basicComboPattern = r'''
    all[ ]attribute[ ]cards[ ]
    (?:atk[ ]x(\d+(?:\.\d+)?).)?
    (?:rcv[ ]x(\d+(?:\.\d+)?).)?
    when[ ]reaching[ ](\d+)[ ](?:combos|or).*
'''

orbTypeComboPattern = r'''
    all[ ]attribute[ ]cards
    (?:[ ]atk[ ]x(\d+(?:\.\d+)?))?
    [ ]when[ ]reaching[ ]
    (\d+)[ ]set[ ]of[ ]
    ''' + orbTypePattern + '''
    [ ](?:combo|combos)
'''

orbTypeComboScalePattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]for[ ]each[ ]additional[ ]combo,[ ]up[ ]to[ ]
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]when[ ]reaching[ ]
    (\d+)[ ]combos
'''

enhancedMatchPattern = r'''
    matched[ ]attribute[ ]
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]when[ ]matching[ ]exactly[ ]
    (\d+)[ ]connected[ ]orbs
    [ ]with[ ]at[ ]least[ ]
    (\d+)[ ]enhanced[ ](?:orbs|orb)
'''

colorMatchPattern = r'''
    all[ ]attribute[ ]cards[ ]
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:(\d+)%[ ]all[ ]damage[ ]reduction)?
    [ ]when[ ]attacking[ ]with
    (.*?)orb[ ]types
    [ ]at[ ]the[ ]same[ ]time
'''

scalingColorMatchPattern = r'''
    all[ ]attribute[ ]cards[ ]
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    ,?[ ]?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:(\d+)%[ ]all[ ]damage[ ]reduction)?
    [ ]when[ ]attacking[ ]with[ ]
    (\d+)[ ]of[ ]following[ ]orb[ ]types:
    (.*)
'''

colorMatchScalePattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]for[ ]each[ ]additional[ ]orb[ ]type,[ ]up[ ]to[ ]
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]for[ ]all[ ](\d+)[ ]matches
'''

twoColorMatchPattern = r'''
    all[ ]attribute[ ]cards[ ]
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:(\d+)%[ ]all[ ]damage[ ]reduction)?
    [ ]when[ ](?:reaching|attacking[ ]with)[ ]
    ([a-zA-Z]+)[ ](?:&|and)[ ]
    ([a-zA-Z]+)[ ]combos(?:[ ]at[ ]the[ ]same[ ]time)?
'''

resolvePattern = r'''
    while[ ]your[ ]hp[ ]is[ ](\d+)%
    [ ]or[ ]above,[ ]a[ ]single[ ]hit[ ]that[ ]normally[ ]kills[ ]you[ ]
    will[ ]instead[ ]leave[ ]you[ ]with[ ]1[ ]hp
'''

resolveExtraPattern = r'''
    for[ ]the[ ]consecutive[ ]hits,[ ]this[ ]
    skill[ ]will[ ]only[ ]affect[ ]the[ ]first[ ]hit
'''

onSkillUsedPattern = r'''
    (.*?)(?:attribute|type)[ ]cards[ ]
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    [ ]on[ ]the[ ]turn[ ]a[ ]skill[ ]is[ ]used
'''



# some descriptions have a type where a period is not followed by a space
periodTypePattern = r'''seconds\.([a-zA-Z])'''
periodFixPattern = r'''seconds. \1'''

parenOrigPattern = r'''will not stack \) '''
parenFixPattern = r'''will not stack \). '''

def formatComboSkills(description, minAtk, maxAtk, atkScale,
                minCombo, maxCombo, rcv, attributes):
                
    attributeStr = "["
    for attribute in attributes:
        attributeStr += "\"" + attribute + "\","
    attributeStr = attributeStr[:-1] + "]" #because of this, there must be at least 1 attribute
    result = "{\"skilltype\":\"combo\","
    result += "\"combo\":" + attributeStr + ","
    result += "\"effect\":{"
    result += "\"atk_scale_multi_type\":\"additive\","
    result += "\"atk_scale\":" + str(atkScale) + ","
    result += "\"min_atk\":" + str(minAtk) + ","
    result += "\"max_atk\":" + str(maxAtk) + ","
    result += "\"start_combo\":" + str(minCombo) + ","
    result += "\"end_combo\":" + str(maxCombo) + ","
    result += "\"rcv\":" + str(rcv)
    result += "},"
    result += "\"description\":\"" + description + "\""
    result += "},"
    
    return result

def formatBasicSkills(description, hp, atk, rcv, attributes, types):
    hp = hp if hp else 1
    atk = atk if atk else 1
    rcv = rcv if rcv else 1
    result = "{\"skilltype\":\"basic\","
    result += "\"attribute\":["
    if attributes:
        for attribute in attributes:
            result += "\"" + attribute + "\","
        result = result[:-1]
    result += "],"
        
    result += "\"type\":["
    if types:
        for type in types:
            result += "\"" + type + "\","
        result = result[:-1]
    result += "],"
    result += "\"effect\":{"
    result += "\"hp\":" + str(hp) + ","
    result += "\"atk\":" + str(atk) + ","
    result += "\"rcv\":" + str(rcv)
    result += "},"
    result += "\"description\":\"" + description + "\""
    result += "},"
    return result
    
def formatColorMatchSkills(description, orbTypes, minAtk, 
                           maxAtk=None, minCount=None, maxCount=None,
                           atkScale=None, rcv=None, shield=None):
    minAtk = minAtk if minAtk else 1
    maxAtk = maxAtk if maxAtk else minAtk
    rcv = rcv if rcv else 1
    
    minCount = minCount if minCount else len(orbTypes)
    maxCount = maxCount if maxCount else minCount
    atkScale = atkScale if atkScale else 0
    shield = shield if shield else 0
    
    result = "{\"skilltype\":\"color_match\","
    result += "\"color_match\":["
    for orbType in orbTypes:
        result += "\"" + orbType + "\","
    result = result[:-1] + "],"
    
    result += "\"effect\":{"
    result += "\"atk_scale_type\":\"additive\","
    result += "\"min_atk\":" + str(minAtk) + ","
    result += "\"max_atk\":" + str(maxAtk) + ","
    result += "\"atk_scale\":" + str(atkScale) + ","
    result += "\"min_count\":" + str(minCount) + ","
    result += "\"max_count\":" + str(maxCount) + ","
    result += "\"rcv\":" + str(rcv) + ","
    result += "\"shield\":" + str(shield)
    result += "},"
    result += "\"description\":\"" + description + "\""
    result += "},"
    return result
    
def getBasicSkill(regexMatches):
    basicStr = regexMatches.group().strip(" ")
    description = basicStr
    
    attributes = attributeRe.findall(basicStr)
    types = typeRe.findall(basicStr)

    multiplierM = basicMultiRe.search(basicStr)
    hp = 1
    atk = 1
    rcv = 1
    if multiplierM:
        if multiplierM[1]: # all stats
            hp = multiplierM[1]
            atk = multiplierM[1]
            rcv = multiplierM[1]
        else:
            hp = multiplierM[2] if multiplierM[2] else 1
            atk = multiplierM[3] if multiplierM[3] else 1
            rcv = multiplierM[4] if multiplierM[4] else 1
    return formatBasicSkills(description, hp, atk, rcv, attributes, types)

def getBasicSkill2(match):
        des = match[0]
        hp = match[1]
        atk = match[2]
        rcv = match[3]
        type = [match[4]]
        return formatBasicSkills(des, hp, atk, rcv, None, type)
  
def getComboSkill(baseMatches, scaleMatches):
    description = baseMatches[0]
    minAtk = baseMatches[1]
    minCombo = baseMatches[2]
    atkScale = 0
    maxAtk = minAtk
    maxCombo = minCombo
    rcv = 1
    
    if scaleMatches:
        description += ". " + scaleMatches[0]
        atkScale = scaleMatches[1]
        atkMax = scaleMatches[2]
        comboMax = scaleMatches[3]
        
    attributes = ["all"]
        
    
    return formatComboSkills(description, minAtk, maxAtk, atkScale,
                minCombo, maxCombo, rcv, attributes)
    
def getBasicComboSkill(match):
    des = match[0]
    minAtk = match[1] if match[1] else 1
    rcv = match[2] if match[2] else 1
    minCombo = match[3]
    
    atkScale = 0
    maxAtk = minAtk
    maxCombo = minCombo
    attributes = ["all"]
    
    return formatComboSkills(des, minAtk, maxAtk, atkScale,
                minCombo, maxCombo, rcv, attributes)
    
def getOrbTypeComboSkill(match, scaleMatch):
    des = match[0]
    minAtk = match[1]
    minCombo = match[2]
    attribute = match[3]

    atkScale = 0
    maxAtk = minAtk
    maxCombo = minCombo
    
    if scaleMatch:
        des += ". " + scaleMatch[0]
        atkScale = scaleMatch[1] if scaleMatch[1] else 0
        maxAtk = scaleMatch[2] if scaleMatch[2] else minAtk
        maxCombo = scaleMatch[3] if scaleMatch[3] else minCombo
        
        
    attributes = [attribute]
    rcv = 1
    return formatComboSkills(des, minAtk, maxAtk, atkScale,
                             minCombo, maxCombo, rcv, attributes)
    
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
    result += "},"
    return result

def getEnhancedMatch(match):
    des = match[0]
    atk = match[1]
    orbCount = match[2]
    minEnhanced = match[3]
    
    result = "{\"skilltype\":\"enhanced_match\","
    result += "\"effect\":{"
    result += "\"atk\":" + str(atk) + ","
    result += "\"orb_count\":" + str(orbCount) + ","
    result += "\"min_enhanced\":" + str(minEnhanced)
    result += "},"
    result += "\"description\":\"" + des + "\"},"
    return result
    
def getColorMatchSkills(match):
    des = match[0]
    atk = match[1]
    rcv = match[2]
    shield = match[3]
    orbString = match[4]
    orbTypeRe = re.compile(orbTypePattern, re.IGNORECASE|re.VERBOSE)
    orbTypes = orbTypeRe.findall(orbString)
    return formatColorMatchSkills(des, orbTypes, atk, rcv=rcv, shield=shield)

def getScalingColorMatchSkills(match, scaleMatch):
    des = match[0]
    minAtk = match[1]
    rcv = match[2]
    minCount = match[3]
    shield = match[4]
    atkScale = 0
    maxCount = minCount
    maxAtk = minAtk
    orbTypeRe = re.compile(orbTypePattern, re.IGNORECASE|re.VERBOSE)
    orbTypes = orbTypeRe.findall(match[5])
    if scaleMatch:
        des += ". " + scaleMatch[0]
        atkScale = scaleMatch[1]
        maxAtk = scaleMatch[2]
        maxCount = scaleMatch[3]
    
    return formatColorMatchSkills(des, orbTypes, minAtk, maxAtk=maxAtk,
                                  minCount=minCount, maxCount=maxCount,
                                  atkScale=atkScale, rcv=rcv, shield=shield)
  
def getTwoColorMatchSkills(match):
    des = match[0]
    atk = match[1]
    rcv = match[2]
    shield = match[3]
    orbTypes = [match[4], match[5]]
    return formatColorMatchSkills(des, orbTypes, atk, rcv=rcv, shield=shield)

def getHeartCrossSkill(match):
    des = match[0]
    atk = match[1] if match[1] else 1
    shield = match[2] if match[2] else 0
    
    result = "{\"skilltype\":\"heart_cross\","
    result += "\"effect\":{"
    result += "\"atk\":" + str(atk) + ","
    result += "\"shield\":" + str(shield)
    result += "},"
    result += "\"description\":\"" + des + "\""
    result += "},"
    return result
    
    
def getResolveSkill(resolveM, extraM):
    des = resolveM[0] + ". " + extraM[0]
    hpThresh = resolveM[1]
    
    result = "{\"skilltype\":\"resolve\","
    result += "\"effect\":{"
    result += "\"hp_threshold\":" + str(hpThresh)
    result += "},"
    result += "\"description\":\"" + des + "\""
    result += "},"
    return result

def getSkillUsedSkill(match, extra):
    des = match[0]
    if extra:
        des += ". " + extra[0]
    condition = match[1]
    atk = match[2] if match[2] else 1
    rcv = match[3] if match[3] else 1
    
    attributeRe = re.compile(attributePattern, re.I|re.VERBOSE)
    attributes = attributeRe.findall(condition)
    typeRe = re.compile(typePattern, re.I|re.VERBOSE)
    types = typeRe.findall(condition)
        

    result = "{\"skilltype\":\"skill_used\","
    result += "\"attribute\":["
    if attributes:
        for attribute in attributes:
            result += "\"" + attribute + "\","
        result = result[:-1]
    result += "],"
        
    result += "\"type\":["
    if types:
        for type in types:
            result += "\"" + type + "\","
        result = result[:-1]
    result += "],"
        
    result += "\"effect\":{"
    result += "\"atk\":" + str(atk) + ","
    result += "\"rcv\":" + str(rcv)
    result += "},"
    result += "\"description\":\"" + match[0] + "\""
    result += "},"
    return result
    
def main():
    file = open("leaderskills.json")
    leaderJson = json.load(file)
    
    if len(leaderJson) is 0:
        return
    
    unfinished = 0
    count = 0
    parenFixRe = re.compile(parenOrigPattern, re.I|re.VERBOSE)
    
    periodTypoRe = re.compile(periodTypePattern, re.IGNORECASE|re.VERBOSE)
    result = "["
    for skillJson in leaderJson:
        
        name = skillJson["name"]
        des = periodTypoRe.sub(periodFixPattern, skillJson["effect"])
        des = parenFixRe.sub(parenFixPattern, des)
        leaderSkillParts = des.split(". ")
        result += "{"
        result += "\"name\":\"" + name + "\","
        result += "\"description\":\"" + des + "\","
        result += "\"skill\":["
        i = 0
        while i < len(leaderSkillParts):
            count += 1
            part = leaderSkillParts[i]
            #print(part)
            i += 1
            basicM = basicRe.search(part)
            if basicM:
                result += getBasicSkill(basicM)
                continue
            
            basic2Re = re.compile(basicPattern2, re.IGNORECASE|re.VERBOSE)
            basic2M = basic2Re.search(part)
            if basic2M:
                result += getBasicSkill2(basic2M)
                continue
            
            scalingComboBaseRe = re.compile(scalingComboBasePattern, re.IGNORECASE|re.VERBOSE)
            scalingComboBaseM = scalingComboBaseRe.search(part)
            if scalingComboBaseM:
                if i < len(leaderSkillParts):
                    scalePart = leaderSkillParts[i]    #i already incremented
                    scalingComboScaleRe = re.compile(scalingComboScalePattern, re.IGNORECASE|re.VERBOSE)
                    scalingComboScaleM = scalingComboScaleRe.search(scalePart)
                    result += getComboSkill(scalingComboBaseM, scalingComboScaleM)
                    i += 1
                else:
                    result += getComboSkill(scalingComboBaseM, None)
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
                
            basicComboRe = re.compile(basicComboPattern, re.IGNORECASE|re.VERBOSE)
            basicComboM = basicComboRe.search(part)
            if basicComboM:
                result += getBasicComboSkill(basicComboM)
                continue
                
            orbTypeComboRe = re.compile(orbTypeComboPattern, re.IGNORECASE|re.VERBOSE)
            orbTypeComboM = orbTypeComboRe.search(part)
            orbTypeComboScaleM = None
            if orbTypeComboM:
                
                if i < len(leaderSkillParts):
                
                    orbTypeComboScaleRe = re.compile(orbTypeComboScalePattern, re.IGNORECASE|re.VERBOSE)
                
                
                    scalePart = leaderSkillParts[i]
                    orbTypeComboScaleM = orbTypeComboScaleRe.search(scalePart)
                    if orbTypeComboScaleM:
                        i += 1
                    
                result += getOrbTypeComboSkill(orbTypeComboM, orbTypeComboScaleM)
                continue
            
            enhancedMatchRe = re.compile(enhancedMatchPattern, re.IGNORECASE|re.VERBOSE)
            enhancedMatchM = enhancedMatchRe.search(part)
            if enhancedMatchM:
                result += getEnhancedMatch(enhancedMatchM)
                continue
            
            colorMatchRe = re.compile(colorMatchPattern, re.IGNORECASE|re.VERBOSE)
            colorMatchM = colorMatchRe.search(part)
            if colorMatchM:
                result += getColorMatchSkills(colorMatchM)
                continue
                
            scalingColorMatchRe = re.compile(scalingColorMatchPattern, re.IGNORECASE|re.VERBOSE)
            scalingColorMatchM = scalingColorMatchRe.search(part)
            if scalingColorMatchM:
                if i < len(leaderSkillParts):
                    scalePart = leaderSkillParts[i]
                    scaleRe = re.compile(colorMatchScalePattern, re.IGNORECASE|re.VERBOSE)
                    scaleM = scaleRe.search(scalePart)
                    result += getScalingColorMatchSkills(scalingColorMatchM, scaleM)
                    if scaleM:
                        i += 1
                else:
                    result += getScalingColorMatchSkills(scalingColorMatchM, None)
                continue
                        
            twoColorMatchRe = re.compile(twoColorMatchPattern, re.IGNORECASE|re.VERBOSE)
            twoColorMatchM = twoColorMatchRe.search(part)
            if twoColorMatchM:
                result += getTwoColorMatchSkills(twoColorMatchM)
                continue
            
            
            heartCrossRe = re.compile(heartCrossPattern, re.IGNORECASE|re.VERBOSE)
            heartCrossM = heartCrossRe.search(part)
            if heartCrossM:
                result += getHeartCrossSkill(heartCrossM)
                continue
            
            resolveRe = re.compile(resolvePattern, re.IGNORECASE|re.VERBOSE)
            resolveM = resolveRe.search(part)
            if resolveM:
                extraPart = None
                if i < len(leaderSkillParts):
                    extraPart = leaderSkillParts[i]
                    extraPartRe = re.compile(resolveExtraPattern, re.IGNORECASE|re.VERBOSE)
                    extraM = extraPartRe.search(extraPart)
                    if extraM:
                        result += getResolveSkill(resolveM, extraM)
                        i += 1
                continue
            
            skillUsedRe = re.compile(onSkillUsedPattern, re.IGNORECASE|re.VERBOSE)
            skillUsedMatch = skillUsedRe.search(part)
            if skillUsedMatch:
                if i < len(leaderSkillParts):
                    extra = leaderSkillParts[i]
                    result += getSkillUsedSkill(skillUsedMatch, extra)
                    i += 1
                continue
            print("NOT DONE: " + part)
            print()
            unfinished += 1
        result = result.strip(",") # fencepost problem
        result += "]},"
    result = result.strip(",")
    result += "]"
    
    print("UNFINISHED: " + str(unfinished) + "/" + str(count))
    
    outFile = open("formattedLeaderSkills.json", "w", encoding="utf-8")
    outFile.write(result)
    outFile.close()
    file.close()
    


if __name__ == "__main__":
    main()