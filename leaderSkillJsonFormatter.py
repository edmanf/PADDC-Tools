import json
import re
# TODO: Fix issues with ignore case: see mini zhao yun


#match 1: attribute
attribute_pattern = r'''
    (fire|water|wood|light|dark|all)

'''
attribute_re = re.compile(attribute_pattern, re.IGNORECASE|re.VERBOSE)

#match 1: type
type_pattern = r'''
    (
    god|balanced|attacker|physical
    |devil|healer|dragon|machine
    |evo[ ]material|awaken[ ]material
    |enhance[ ]material|redeemable[ ]material
    |all
    )
'''
type_re = re.compile(type_pattern, re.IGNORECASE|re.VERBOSE)

#match 1: orb_type
orb_type_pattern = r'''
    (fire|water|wood|light|dark|heal
    |heart|jammer|mortal[ ]poison|poison|all)
'''


# TODO:Fix using non matching groups
basic_re_pattern = r'''
    ((((
    ''' + attribute_pattern + "|" + type_pattern + ''')   #list of attributes and types
    
    \W+ (attribute\W+|type\W+)?)+   #repeat for all attributes and types

    cards\W+
    
    ((hp|atk|rcv|all[ ]stats)[ ]x\d+([.]\d+)?(,[ ])?)+)[.]?$) #followed by multipliers

'''
basic_re = re.compile(basic_re_pattern, re.IGNORECASE|re.VERBOSE)

# match 1: hp multi
# match 2: atk multi
# match 3: rcv multi
# match 4: type
basic_pattern2 = r'''
    (?:hp[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    [ ]to[ ] ''' + type_pattern + '''
    [ ]type[ ]cards
'''

# match 1: all stat multi
# match 2: hp multi
# match 3: atk multi
# match 4: rcv multi
basic_multi_pattern = r'''
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
basic_multi_re = re.compile(basic_multi_pattern, re.IGNORECASE|re.VERBOSE)

scaling_combo_base_pattern = r'''
    \Aatk[ ]x(\d+(?:\.\d+)?)                              #capture atk multiplier
    (?:,[ ]rcv[ ]x(\d+(?:\.\d+)?))?
    
    [ ](?:at|when[ ]reaching)[ ](\d+)[ ]combos                              #capture base start combo
'''
scaling_combo_scale_pattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)                              #capture scaling mutliplier
    (?:,[ ]rcv[ ]x(\d+(?:\.\d+)?))?
    [ ]for[ ]each[ ]additional[ ]combo,
    [ ]up[ ]to[ ]atk[ ]x(\d+(?:\.\d+)?)
    (?:,[ ]rcv[ ]x(\d+(?:\.\d+)?))?[ ]at[ ]         #capture multiplier limit
    (\d+)[ ]combos                                      #capture combo limit
'''

basic_combo_pattern = r'''
    all[ ]attribute[ ]cards[ ]
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:(\d+)%[ ]all[ ]damage[ ]reduction)?
    [ ]when[ ](?:reaching|reaching)[ ](\d+)[ ](?:combos|or).*
'''

# match 1: atk
# match 2: combos
exact_combo_pattern = r'''
    all[ ]attribute[ ]cards[ ]
    (?:atk[ ]x(\d+(?:\.\d+)?))
    [ ]when[ ]reaching[ ]exactly[ ]
    (\d+)[ ]combos
'''

connected_pattern = r'''
    (?:atk[ ]x(\d+(?:\.\d+)?))?                         #capture atk multi
    (?:,[ ])?                                               
    (?:rcv[ ]x(\d+(?:\.\d+)?))?                         #capture rcv multi
    [ ]when[ ]simultaneously[ ]clearing[ ]
    (\d+)\+?[ ]connected[ ]\w+(?:[ ]or[ ].+?)?[ ]orbs      #capture beginning count
'''

connected_scale_pattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)                              #capture atk scale
    [ ]for[ ]each[ ]additional[ ]orb,
    [ ]up[ ]to[ ]atk[ ]x (\d+(?:\.\d+)?)                #capture max atk
    [ ]at[ ](\d+)[ ]connected[ ]orb                     #capture max count
'''

no_skyfall_pattern = r'''
    no[ ]skyfall[ ]matches
'''

board_size_pattern = r'''
    change[ ]the[ ]board[ ]to[ ](\d+)x(\d+)[ ]size        #captures col and row
'''

cross_pattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)                              #captures atk mutliplier
    [ ]for[ ]clearing[ ](?:\w+[ ])+?
    orbs[ ]in[ ]a[ ]cross[ ]formation
'''
heart_cross_pattern = r'''
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:reduce[ ]damage[ ]taken[ ]by[ ](\d+)%)?
    [ ]after[ ]matching[ ](?:heal|heart)[ ]orbs[ ]in[ ]a[ ]cross[ ]formation

'''

move_time_pattern = r'''
    (fixed|increases)[ ]                            #captures fixed or increases
    (?:\w+[ ])*?orb[ ]movement(?:[ ]\w+)+?[ ]
    (\d+(?:\.\d+)?)[ ]seconds                       #captures time value    
'''





orb_type_combo_pattern = r'''
    all[ ]attribute[ ]cards
    (?:[ ]atk[ ]x(\d+(?:\.\d+)?))?
    [ ]when[ ]reaching[ ]
    (\d+)[ ]set[ ]of[ ]
    ''' + orb_type_pattern + '''
    [ ](?:combo|combos)
'''

orb_type_combo_scale_pattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]for[ ]each[ ]additional[ ]combo,[ ]up[ ]to[ ]
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]when[ ]reaching[ ]
    (\d+)[ ]combos
'''

enhanced_match_pattern = r'''
    matched[ ]attribute[ ]
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]when[ ]matching[ ]exactly[ ]
    (\d+)[ ]connected[ ]orbs
    [ ]with[ ]at[ ]least[ ]
    (\d+)[ ]enhanced[ ](?:orbs|orb)
'''

color_match_pattern = r'''
    (?:all[ ]attribute[ ]cards[ ])?
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:(\d+)%[ ]all[ ]damage[ ]reduction)?
    [ ]when[ ]attacking[ ]with
    (.*?)orb[ ]types
    [ ]at[ ]the[ ]same[ ]time
'''

scaling_color_match_pattern = r'''
    (?:all[ ]attribute[ ]cards[ ])?
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    ,?[ ]?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:(\d+)%[ ]all[ ]damage[ ]reduction)?
    [ ]when[ ]attacking[ ]with[ ]
    (\d+)[ ]of(.*)
'''

color_match_scale_pattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]for[ ]each[ ]additional[ ]orb[ ]type,[ ]up[ ]to[ ]
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]for[ ]all[ ](\d+)[ ]matches
'''

two_color_match_pattern = r'''
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

resolve_pattern = r'''
    while[ ]your[ ]hp[ ]is[ ](\d+)%
    [ ]or[ ]above,[ ]a[ ]single[ ]hit[ ]that[ ]normally[ ]kills[ ]you[ ]
    will[ ]instead[ ]leave[ ]you[ ]with[ ]1[ ]hp
'''

resolve_extra_pattern = r'''
    for[ ]the[ ]consecutive[ ]hits,[ ]this[ ]
    skill[ ]will[ ]only[ ]affect[ ]the[ ]first[ ]hit
'''

on_skill_used_pattern = r'''
    (.*?)(?:attribute|type)[ ]cards[ ]
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    [ ]on[ ]the[ ]turn[ ]a[ ]skill[ ]is[ ]used
'''

basic_damage_reduction_pattern = r'''
    (\d+)%[ ](.*?)[ ]damage[ ]reduction
'''

hp_conditional_pattern = r'''
    (.*?[ ]cards[ ])? 
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    [ ]when[ ]hp[ ]is[ ]
    (less[ ]than|greater[ ]than|full)
    (?:[ ](\d+)%)?
'''

# some descriptions have a type where a period is not followed by a space
period_type_pattern = r'''seconds\.([a-zA-Z])'''
period_fix_pattern = r'''seconds. \1'''

paren_orig_pattern = r'''will not stack \) '''
paren_fix_pattern = r'''will not stack \). '''

# fix for some bikkuriman collab skills
hp_paren_orig_pattern = r'''%[ ]\('''
hp_paren_fix_pattern = r'''%. ('''

double_space_orig_pattern = r'''[ ]{2}'''
double_space_fix_pattern = r'''[ ]'''

hp_repeat_typo_pattern = r'''
    \.[ ][ ]when[ ]hp[ ]is[ ]less[ ]than[ ]50%\.
'''

post_orb_elim_pattern = r'''
    (?:heal|deal)
    [ ](atk|rcv)[ ]x
    (\d+(?:\.\d+)?)
    (?:[ ]as[ ]hp|[ ]damage[ ]to[ ]all[ ]enemies)
    [ ]after[ ]every[ ]orbs[ ]elimination
'''

post_orb_elim_extra_pattern = r'''
    ignores[ ]enemy[ ]element,
    [ ]but[ ]can[ ]be[ ]reduced[ ]
    by[ ]enemy[ ]defense[ ]down[ ]to[ ]0[ ]damage
'''

# match 1: all stat multi
# match 2: hp multi
# match 3: atk multi
# match 4: rcv multi
coop_mode_pattern = r'''
    (?:all[ ]stats[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:hp[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
    [ ]in[ ]cooperation[ ]mode
'''

# match 1: chance
# match 2: damage attribute
# match 3: damage multi
counter_pattern = r'''
    (\d+)%[ ]chance[ ]to[ ]deal[ ]counter[ ]
    (\w+)[ ]damage[ ]of[ ]
    (\d+)x[ ]damage[ ]taken
'''


def format_skill_effect(hp=0, atk=0, rcv=0, shield=0,
                      atk_scale_type=None, atk_scale=0, min_atk=0, max_atk=0,
                      rcv_scale=0, min_rcv=0, max_rcv=0,
                      min_combo_count=0, max_combo_count=0,
                      min_connected=0, max_connected=0,
                      rows=0, cols=0,
                      orb_types=None, attributes=None, types=None):
    return ""


def format_combo_skills(description, min_atk=0, max_atk=0, atk_scale=0,
                min_combo=0, max_combo=0, attributes=None, shield=0,
                min_rcv=0, maxRcv=0, rcv_scale=0):
    
    attribute_str = "["
    for attribute in attributes:
        attribute_str += "\"" + attribute + "\","
    attribute_str = attribute_str[:-1] + "]" #because of this, there must be at least 1 attribute
    result = "{\"skilltype\":\"combo\","
    result += "\"effect\":{"
    result += "\"orb_types\":" + attribute_str + ","
    if atk_scale:
        result += "\"atk_scale_type\":\"additive\","
        result += "\"atk_scale\":" + str(atk_scale) + ","
        result += "\"min_atk\":" + str(min_atk) + ","
        result += "\"max_atk\":" + str(max_atk) + ","
    else:
        result += "\"atk_scale_type\":\"none\","
        result += "\"atk\":" + str(min_atk) + ","
        
    if rcv_scale:
        result += "\"min_rcv\":" + str(min_rcv) + ","
        result += "\"maxRcv\":" + str(maxRcv) + "," 
        result += "\"rcv_scale\":" + str(rcv_scale) + ","
    elif min_rcv or maxRcv:
        result += "\"rcv_scale\":\"none\","
        result += "\"rcv\":"
        result += str(min_rcv) if min_rcv else str(maxRcv)
        result += ","
        
    result += "\"start_combo\":" + str(min_combo) + ","
    if max_combo:
        result += "\"end_combo\":" + str(max_combo) + ","
    
    if shield:
        result += "\"shield\":" + str(shield) + ","
    result = result[:-1] + "},"
    result += "\"description\":\"" + description + "\""
    result += "},"
    
    return result

def format_basic_skills(description, hp, atk, rcv, attributes, types):
    hp = hp if hp else 1
    atk = atk if atk else 1
    rcv = rcv if rcv else 1
    result = "{\"skilltype\":\"basic\","
    result += "\"effect\":{"
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
    result += "\"hp\":" + str(hp) + ","
    result += "\"atk\":" + str(atk) + ","
    result += "\"rcv\":" + str(rcv)
    
    result += "},"
    result += "\"description\":\"" + description + "\""
    result += "},"
    return result
    
def format_color_match_skills(description, orb_types, min_atk, 
                           max_atk=None, min_count=None, max_count=None,
                           atk_scale=None, rcv=None, shield=None):
    min_atk = min_atk if min_atk else 1
    max_atk = max_atk if max_atk else min_atk
    rcv = rcv if rcv else 1
    
    min_count = min_count if min_count else len(orb_types)
    max_count = max_count if max_count else min_count
    atk_scale = atk_scale if atk_scale else 0
    shield = shield if shield else 0
    
    result = "{\"skilltype\":\"color_match\","    
    result += "\"effect\":{"
    result += "\"orb_types\":["
    for orb_type in orb_types:
        result += "\"" + orb_type + "\","
    result = result[:-1] + "],"
    result += "\"atk_scale_type\":\"additive\","
    result += "\"min_atk\":" + str(min_atk) + ","
    result += "\"max_atk\":" + str(max_atk) + ","
    result += "\"atk_scale\":" + str(atk_scale) + ","
    result += "\"min_count\":" + str(min_count) + ","
    result += "\"max_count\":" + str(max_count) + ","
    result += "\"rcv\":" + str(rcv) + ","
    result += "\"shield\":" + str(shield)
    result += "},"
    result += "\"description\":\"" + description + "\""
    result += "},"
    return result
    
def get_basic_skill(regex_matches):
    basic_str = regex_matches.group().strip(" ")
    description = basic_str
    
    attributes = attribute_re.findall(basic_str)
    types = type_re.findall(basic_str)

    multiplier_m = basic_multi_re.search(basic_str)
    hp = 1
    atk = 1
    rcv = 1
    if multiplier_m:
        if multiplier_m[1]: # all stats
            hp = multiplier_m[1]
            atk = multiplier_m[1]
            rcv = multiplier_m[1]
        else:
            hp = multiplier_m[2] if multiplier_m[2] else 1
            atk = multiplier_m[3] if multiplier_m[3] else 1
            rcv = multiplier_m[4] if multiplier_m[4] else 1
    return format_basic_skills(description, hp, atk, rcv, attributes, types)

def get_basic_skill2(match):
        des = match[0]
        hp = match[1]
        atk = match[2]
        rcv = match[3]
        type = [match[4]]
        return format_basic_skills(des, hp, atk, rcv, None, type)
  
def get_combo_skill(base_matches, scale_matches):
    description = base_matches[0]
    min_atk = base_matches[1]
    min_rcv = base_matches[2]
    min_combo = base_matches[3]
            
    attributes = ["all"]
    
    if scale_matches:
        description += ". " + scale_matches[0]
        atk_scale = scale_matches[1]
        rcv_scale = scale_matches[2]
        max_atk = scale_matches[3]
        maxRcv = scale_matches[4]
        max_combo = scale_matches[5]
        
        return format_combo_skills(description, attributes=attributes, min_atk=min_atk, max_atk=max_atk, 
                                 atk_scale=atk_scale, min_combo=min_combo, max_combo=max_combo,
                                 rcv_scale=rcv_scale, min_rcv=min_rcv, maxRcv=maxRcv)
    else:
        return format_combo_skills(description, attributes=attributes, min_atk=min_atk,
                                 min_rcv=min_rcv, min_combo=min_combo)
    
def get_basic_combo_skill(match):
    des = match[0]
    min_atk = match[1]
    min_rcv = match[2]
    shield = match[3]
    min_combo = match[4]

    attributes = ["all"]
    
    return format_combo_skills(des, min_atk=min_atk, min_combo=min_combo,
                attributes=attributes, shield=shield, min_rcv=min_rcv)
    
def get_orb_type_combo_skill(match, scale_match):
    des = match[0]
    min_atk = match[1]
    min_combo = match[2]
    attributes = [match[3]]
    
    if scale_match:
        des += ". " + scale_match[0]
        atk_scale = scale_match[1] if scale_match[1] else 0
        max_atk = scale_match[2] if scale_match[2] else min_atk
        max_combo = scale_match[3] if scale_match[3] else min_combo
        return format_combo_skills(des, min_atk=min_atk, max_atk=max_atk, atk_scale=atk_scale,
                                 min_combo=min_combo, max_combo=max_combo, attributes=attributes)
    else:
        return format_combo_skills(des, min_atk=min_atk, min_combo=min_combo, attributes=attributes)

def get_exact_combo_skill(match):
    des = match[0]
    min_atk = match[1]
    min_combo = match[2]
    max_combo = min_combo
    attributes = ["all"]
    
    return format_combo_skills(des, min_atk=min_atk, min_combo=min_combo,
                                  max_combo=max_combo, attributes=attributes)
        
def get_connected_combo(base_matches, scale_matches):    
    min_atk = base_matches[1]
    start_count = base_matches[3]
    rcv = base_matches[2] if base_matches[2] else 1
    atk_scale = 0
    max_atk = min_atk
    end_count = start_count  
    if scale_matches:
        atk_scale = scale_matches[1]
        max_atk = scale_matches[2]
        end_count = scale_matches[3]
    
    orb_type_re = re.compile(orb_type_pattern, re.IGNORECASE|re.VERBOSE)
    orb_type_m = orb_type_re.findall(base_matches[0])
        
    result = "{\"skilltype\":\"connected\","

    result += "\"effect\":{"
    result += "\"orb_types\":["
    # dont check for None, there must be an orb_type
    for orb_type in orb_type_m:
        result += "\"" + orb_type + "\","
    result = result.strip(",") + "],"
    result += "\"atk_scale_type\":\"additive\","
    result += "\"atk_scale\":" + str(atk_scale) + ","
    result += "\"min_atk\":" + str(min_atk) + ","
    result += "\"max_atk\":" + str(max_atk) + ","
    result += "\"start_count\":" + str(start_count) + ","
    result += "\"end_count\":" + str(end_count) + ","
    result += "\"rcv\":" + str(rcv) + ","
    result += "\"description\":\"" + base_matches[0]
    if scale_matches:
        result += ". " + scale_matches[0]
    result += "\""
    result += "}"
    result += "},"
    return result
    
def get_no_skyfall_skill(match):
    result = "{\"skilltype\":\"skyfall\","
    result += "\"effect\":{"
    result += "\"skyfall_type\":\"no skyfall\""
    result += "},"
    result += "\"description\":\"" + match[0] + "\""
    result += "},"
    return result
    
def get_board_size_skill(match):
    rows = match[1]
    cols = match[2]

    result = "{\"skilltype\":\"boardsize\","
    result += "\"effect\":{"
    result += "\"rows\":" + str(rows) + ","
    result += "\"cols\":" + str(cols)
    result += "},"
    result += "\"description\":\"" + match[0] + "\""
    result += "},"
    return result
    
def get_cross_skill(match):
    atk_scale = match[1]
    description = match[0]
    
    orb_type_re = re.compile(orb_type_pattern, re.IGNORECASE|re.VERBOSE)
    orb_type_m = orb_type_re.findall(description)
    
    
    result = "{\"skilltype\":\"cross\","
    result += "\"cross\":["
    
    #dont check for none, because there has to be an orb type
    for orb_type in orb_type_m:
        result += "\"" + orb_type + "\","
    result = result.strip(",") + "],"
    result += "\"effect\":{"
    result += "\"atk_scale_type\":\"multiplicative\","
    result += "\"atk_scale\":" + atk_scale
    result += "},"
    
    result += "\"description\":\"" + description + "\""
    result += "}"
    return result
    
def get_move_time_skill(match):
    move_time_type = "fixed" if match[1] == "Fixed" else "increase"

    result = "{\"skilltype\":\"move_time\","
    result += "\"effect\":{"
    result += "\"move_time_type\":\"" + move_time_type + "\","
    result += "\"time\":" + match[2]
    result += "},"
    result += "\"description\":\"" + match[0] + "\""
    result += "},"
    return result

def get_enhanced_match(match):
    des = match[0]
    atk = match[1]
    orb_count = match[2]
    min_enhanced = match[3]
    
    result = "{\"skilltype\":\"enhanced_match\","
    result += "\"effect\":{"
    result += "\"atk\":" + str(atk) + ","
    result += "\"orb_count\":" + str(orb_count) + ","
    result += "\"min_enhanced\":" + str(min_enhanced)
    result += "},"
    result += "\"description\":\"" + des + "\"},"
    return result
    
def get_color_match_skills(match):
    des = match[0]
    atk = match[1]
    rcv = match[2]
    shield = match[3]
    orbString = match[4]
    orb_type_re = re.compile(orb_type_pattern, re.IGNORECASE|re.VERBOSE)
    orb_types = orb_type_re.findall(orbString)
    return format_color_match_skills(des, orb_types, atk, rcv=rcv, shield=shield)

def get_scaling_color_match_skills(match, scale_match):
    des = match[0]
    min_atk = match[1]
    rcv = match[2]
    min_count = match[3]
    shield = match[4]
    atk_scale = 0
    max_count = min_count
    max_atk = min_atk
    orb_type_re = re.compile(orb_type_pattern, re.IGNORECASE|re.VERBOSE)
    orb_types = orb_type_re.findall(match[5])
    if scale_match:
        des += ". " + scale_match[0]
        atk_scale = scale_match[1]
        max_atk = scale_match[2]
        max_count = scale_match[3]
    
    return format_color_match_skills(des, orb_types, min_atk, max_atk=max_atk,
                                  min_count=min_count, max_count=max_count,
                                  atk_scale=atk_scale, rcv=rcv, shield=shield)
  
def get_two_color_match_skills(match):
    des = match[0]
    atk = match[1]
    rcv = match[2]
    shield = match[3]
    orb_types = [match[4], match[5]]
    return format_color_match_skills(des, orb_types, atk, rcv=rcv, shield=shield)

def get_heart_cross_skill(match):
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
    
    
def get_resolve_skill(resolve_m, extra_m):
    des = resolve_m[0] + ". " + extra_m[0]
    hpThresh = resolve_m[1]
    
    result = "{\"skilltype\":\"resolve\","
    result += "\"effect\":{"
    result += "\"hp_threshold\":" + str(hpThresh)
    result += "},"
    result += "\"description\":\"" + des + "\""
    result += "},"
    return result

def get_skill_used_skill(match, extra):
    des = match[0]
    if extra:
        des += ". " + extra[0]
    condition = match[1]
    atk = match[2] if match[2] else 1
    rcv = match[3] if match[3] else 1
    
    attribute_re = re.compile(attribute_pattern, re.I|re.VERBOSE)
    attributes = attribute_re.findall(condition)
    type_re = re.compile(type_pattern, re.I|re.VERBOSE)
    types = type_re.findall(condition)
        

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
  
def get_basic_damage_reduction_skill(match):
    des = match[0]
    value = match[1]
    attribute_re = re.compile(attribute_pattern, re.I|re.VERBOSE)
    attributes = attribute_re.findall(match[2])
    
    result = "{\"skilltype\":\"shield\","
    result += "\"effect\":{"
    result += "\"attribute\":["
    if attributes:
        for attribute in attributes:
            result += "\"" + attribute + "\","
        result = result[:-1]
    result += "],"
    result += "\"shield\":" + str(value)
    result += "},"
    result += "\"description\":\"" + des + "\""
    result += "},"
    return result
  
def get_hp_cond_skill(match):
    des = match[0]
    attribute_str = match[1]
    atk = match[2] if match[2] else 1
    rcv = match[3] if match[3] else 1
    hp_type = match[4]
    thresh = match[5] if match[5] else 100
    
    result = "{\"skilltype\":\"hp_conditional\","
    result += "\"effect\":{"
    result += "\"conditional_type\":\"" + hp_type + "\","
    result += "\"conditional_value\":" + str(thresh) + ","
    result += "\"atk\":" + str(atk) + ","
    result += "\"rcv\":" + str(rcv)
    result += "},"
    result += "\"description\":\"" + des + "\""
    result += "},"
    return result

def get_post_orb_elim_skill(match, extra=None):
    des = match[0]
    type = match[1].lower()
    value = match[2]
    atk = value if type == "atk" else 0
    rcv = value if type == "rcv" else 0
    
    if extra:
        des += ". " + extra[0]
        
    result = "{\"skilltype\":\"after_match\","
    result += "\"effect\":{"
    result += "\"atk\":" + str(atk) + ","
    result += "\"rcv\":" + str(rcv)
    result += "},"
    
    result += "\"description\":\"" + des + "\""
    result += "},"
    return result
    
    
def get_coop_skills(match):
    des = match[0]
    hp = 1
    atk = 1
    rcv = 1
    
    if match[1]:
        hp = match[1]
        atk = match[1]
        rcv = match[1]
        
    hp = match[2] if match[2] else hp
    atk = match[3] if match[3] else atk
    rcv = match[4] if match[4] else rcv
    
    result = "{\"skilltype\":\"co-op\","
    result += "\"effect\":{"
    result += "\"hp\":" + str(hp) + ","
    result += "\"atk\":" + str(atk) + ","
    result += "\"rcv\":" + str(rcv)
    result += "},"
    result += "\"description\":\"" + des + "\""
    result += "},"
    return result
    
def get_counter_skills(match):
    des = match[0]
    chance = match[1]
    att = match[2]
    value = match[3]
    
    result = "{\"skilltype\":\"counter\","
    result += "\"effect\":{"
    result += "\"chance\":" + str(chance) + ","
    result += "\"attribute\":\"" + att + "\","
    result += "\"atk_multiplier\":" + str(value)
    result += "},"
    result += "\"description\":\"" + des + "\""
    result += "},"
    return result
    
def main():
    file = open("sampleLeaderSkills.json")
    leader_json = json.load(file)
    
    if len(leader_json) is 0:
        return
    
    unfinished = 0
    count = 0
    paren_fix_re = re.compile(paren_orig_pattern, re.I|re.VERBOSE)
    period_typo_re = re.compile(period_type_pattern, re.IGNORECASE|re.VERBOSE)
    hp_paren_typo_re = re.compile(hp_paren_orig_pattern, re.I|re.VERBOSE)
    hp_repeat_typo_re = re.compile(hp_repeat_typo_pattern, re.I|re.VERBOSE)
    
    result = "["
    for skill_json in leader_json:
        
        name = skill_json["name"]
        if name == "N/A":
            continue
        des = period_typo_re.sub(period_fix_pattern, skill_json["effect"])
        des = paren_fix_re.sub(paren_fix_pattern, des)
        des = hp_paren_typo_re.sub(hp_paren_fix_pattern, des)
        des = hp_repeat_typo_re.sub("", des)
        leader_skill_parts = des.split(". ")
        result += "{"
        result += "\"name\":\"" + name + "\","
        result += "\"description\":\"" + des + "\","
        result += "\"skills\":["
        i = 0
        while i < len(leader_skill_parts):
            count += 1
            part = leader_skill_parts[i]
            #print(part)
            i += 1
            basic_m = basic_re.search(part)
            if basic_m:
                result += get_basic_skill(basic_m)
                continue
            
            basic2_re = re.compile(basic_pattern2, re.IGNORECASE|re.VERBOSE)
            basic2_m = basic2_re.search(part)
            if basic2_m:
                result += get_basic_skill2(basic2_m)
                continue
            
            scaling_combo_base_re = re.compile(scaling_combo_base_pattern, re.IGNORECASE|re.VERBOSE)
            scaling_combo_base_m = scaling_combo_base_re.search(part)
            if scaling_combo_base_m:
                if i < len(leader_skill_parts):
                    scale_part = leader_skill_parts[i]    #i already incremented
                    scaling_combo_scale_re = re.compile(scaling_combo_scale_pattern, re.IGNORECASE|re.VERBOSE)
                    scaling_combo_scale_m = scaling_combo_scale_re.search(scale_part)
                    result += get_combo_skill(scaling_combo_base_m, scaling_combo_scale_m)
                    i += 1
                else:
                    result += get_combo_skill(scaling_combo_base_m, None)
                continue
                
            connected_re = re.compile(connected_pattern, re.IGNORECASE|re.VERBOSE)
            connected_m = connected_re.search(part)
            if connected_m:
                scale_part = leader_skill_parts[i] if i < len(leader_skill_parts) else None    #i already incremented
                if scale_part:
                    connected_scale_re = re.compile(connected_scale_pattern, re.IGNORECASE|re.VERBOSE)
                    connected_scale_m = connected_scale_re.search(scale_part)
                    result += get_connected_combo(connected_m, connected_scale_m)
                else:
                    result += get_connected_combo(connected_m, None)
                i += 1
                continue
                
            no_skyfall_re = re.compile(no_skyfall_pattern, re.IGNORECASE|re.VERBOSE)
            no_skyfall_m = no_skyfall_re.search(part)
            if no_skyfall_m:
                result += get_no_skyfall_skill(no_skyfall_m)
                continue
                
            board_size_re = re.compile(board_size_pattern, re.IGNORECASE|re.VERBOSE)
            board_size_m = board_size_re.search(part)
            if board_size_m:
                result += get_board_size_skill(board_size_m)
                continue
                
            cross_re = re.compile(cross_pattern, re.IGNORECASE|re.VERBOSE)
            cross_m = cross_re.search(part)
            if cross_m:
                result += get_cross_skill(cross_m)
                continue
                
            move_time_re = re.compile(move_time_pattern, re.IGNORECASE|re.VERBOSE)
            move_time_m = move_time_re.search(part)
            if move_time_m:
                result += get_move_time_skill(move_time_m)
                continue
                
            basic_combo_re = re.compile(basic_combo_pattern, re.IGNORECASE|re.VERBOSE)
            basic_combo_m = basic_combo_re.search(part)
            if basic_combo_m:
                result += get_basic_combo_skill(basic_combo_m)
                continue
                
            orb_type_combo_re = re.compile(orb_type_combo_pattern, re.IGNORECASE|re.VERBOSE)
            orb_type_combo_m = orb_type_combo_re.search(part)
            orb_type_combo_scale_m = None
            if orb_type_combo_m:
                
                if i < len(leader_skill_parts):
                
                    orb_type_combo_scale_re = re.compile(orb_type_combo_scale_pattern, re.IGNORECASE|re.VERBOSE)
                
                
                    scale_part = leader_skill_parts[i]
                    orb_type_combo_scale_m = orb_type_combo_scale_re.search(scale_part)
                    if orb_type_combo_scale_m:
                        i += 1
                    
                result += get_orb_type_combo_skill(orb_type_combo_m, orb_type_combo_scale_m)
                continue
            
            enhanced_match_re = re.compile(enhanced_match_pattern, re.IGNORECASE|re.VERBOSE)
            enhanced_match_m = enhanced_match_re.search(part)
            if enhanced_match_m:
                result += get_enhanced_match(enhanced_match_m)
                continue
            
            color_match_re = re.compile(color_match_pattern, re.IGNORECASE|re.VERBOSE)
            color_match_m = color_match_re.search(part)
            if color_match_m:
                result += get_color_match_skills(color_match_m)
                continue
                
            scaling_color_match_re = re.compile(scaling_color_match_pattern, re.IGNORECASE|re.VERBOSE)
            scaling_color_match_m = scaling_color_match_re.search(part)
            if scaling_color_match_m:
                if i < len(leader_skill_parts):
                    scale_part = leader_skill_parts[i]
                    scale_re = re.compile(color_match_scale_pattern, re.IGNORECASE|re.VERBOSE)
                    scale_m = scale_re.search(scale_part)
                    result += get_scaling_color_match_skills(scaling_color_match_m, scale_m)
                    if scale_m:
                        i += 1
                else:
                    result += get_scaling_color_match_skills(scaling_color_match_m, None)
                continue
                        
            two_color_match_re = re.compile(two_color_match_pattern, re.IGNORECASE|re.VERBOSE)
            two_color_match_m = two_color_match_re.search(part)
            if two_color_match_m:
                result += get_two_color_match_skills(two_color_match_m)
                continue
            
            
            heart_cross_re = re.compile(heart_cross_pattern, re.IGNORECASE|re.VERBOSE)
            heart_cross_m = heart_cross_re.search(part)
            if heart_cross_m:
                result += get_heart_cross_skill(heart_cross_m)
                continue
            
            resolve_re = re.compile(resolve_pattern, re.IGNORECASE|re.VERBOSE)
            resolve_m = resolve_re.search(part)
            if resolve_m:
                extra_part = None
                if i < len(leader_skill_parts):
                    extra_part = leader_skill_parts[i]
                    extra_part_re = re.compile(resolve_extra_pattern, re.IGNORECASE|re.VERBOSE)
                    extra_m = extra_part_re.search(extra_part)
                    if extra_m:
                        result += get_resolve_skill(resolve_m, extra_m)
                        i += 1
                continue
            
            skill_used_re = re.compile(on_skill_used_pattern, re.IGNORECASE|re.VERBOSE)
            skill_used_match = skill_used_re.search(part)
            if skill_used_match:
                if i < len(leader_skill_parts):
                    extra = leader_skill_parts[i]
                    result += get_skill_used_skill(skill_used_match, extra)
                    i += 1
                continue
            
            basic_damage_reduction_re = re.compile(basic_damage_reduction_pattern, re.I|re.VERBOSE)
            basic_damage_reduction_m = basic_damage_reduction_re.search(part)
            if basic_damage_reduction_m:
                result += get_basic_damage_reduction_skill(basic_damage_reduction_m)
                continue
            
            hp_cond_re = re.compile(hp_conditional_pattern, re.I|re.VERBOSE)
            hp_cond_m = hp_cond_re.search(part)
            if hp_cond_m:
                result += get_hp_cond_skill(hp_cond_m)
                continue
            
            post_orb_elim_re = re.compile(post_orb_elim_pattern, re.I|re.VERBOSE)
            post_orb_elim_m = post_orb_elim_re.search(part)
            if post_orb_elim_m:
                post_orb_elim_extra_re = re.compile(post_orb_elim_extra_pattern, re.I|re.VERBOSE)
                if i < len(leader_skill_parts):
                    extra_part = leader_skill_parts[i]
                    extra_m = post_orb_elim_extra_re.search(extra_part)
                    if extra_m:
                        result += get_post_orb_elim_skill(post_orb_elim_m, extra=extra_m)
                        i += 1
                        continue
                    
                result += get_post_orb_elim_skill(post_orb_elim_m)
                continue
            
            coop_re = re.compile(coop_mode_pattern, re.I|re.VERBOSE)
            coop_m = coop_re.search(part)
            if coop_m:
                result += get_coop_skills(coop_m)
                continue
                
            counter_re = re.compile(counter_pattern, re.I|re.VERBOSE)
            counter_m = counter_re.search(part)
            if counter_m:
                result += get_counter_skills(counter_m)
                continue
                
            exact_combo_re = re.compile(exact_combo_pattern, re.I|re.VERBOSE)
            exact_combo_m = exact_combo_re.search(part)
            if exact_combo_m:
                result += get_exact_combo_skill(exact_combo_m)
                continue
                
            print("NOT DONE: " + part)
            print(name)
            print()
            unfinished += 1
        result = result.strip(",") # fencepost problem
        result += "]},"
    result = result.strip(",")
    result += "]"
    
    print("UNFINISHED: " + str(unfinished) + "/" + str(count))
    
    out_file = open("formattedLeaderSkills.json", "w", encoding="utf-8")
    out_file.write(result)
    out_file.close()
    file.close()
    


if __name__ == "__main__":
    main()