import json
import re
# TODO: Fix issues with ignore case: see mini zhao yun


# match 1: attribute
attribute_pattern = r'''
    (fire|water|wood|light|dark|all)
'''
attribute_re = re.compile(attribute_pattern, re.IGNORECASE|re.VERBOSE)

# match 1: type
# TODO: make sure removing "all" didn't break anything
type_pattern = r'''
    (
    god|balanced|attacker|physical
    |devil|healer|dragon|machine
    |evo[ ]material|awaken[ ]material
    |enhance[ ]material|redeemable[ ]material
    )
'''
type_re = re.compile(type_pattern, re.IGNORECASE|re.VERBOSE)

# match 1: orb type
orb_type_pattern = r'''
    (?P<orb_type>fire|water|wood|light|dark|heal
    |heart|jammer|mortal[ ]poison|poison|all)
'''

# captures common temporary multipliers
# match 1: atk multi
# match 2: rcv multi
# TODO: fix double space typos in preproccessing so [ ]+ isn't neccessary
active_multi_pattern = r'''
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ]+)?
    (?:rcv[ ]x(\d+(?:\.\d+)?))?
'''

# match 1: hp multi
# match 2: atk multi
# match 3: rcv multi
all_stat_pattern = r'''
    (?:hp[ ]x(\d+(?:[.]\d+)?))?
    (?:,[ ])?''' + active_multi_pattern


# match 1: atk multi
# match 2: rcv multi
# match 3: shield
active_multi_shield_pattern = active_multi_pattern + r'''
    (?:,[ ])?
    (?:(\d+)%[ ]all[ ]damage[ ]reduction)?
'''

# match 1: attributes and types (requires further processing)
# match 2: all multi
# match 3: hp multi
# match 4: atk multi
# match 5: rcv multi
basic_pattern = r'''
    (.*)(?:attribute|type)[ ]cards[ ]
    (?:
    (?:all[ ]stats[ ]x(\d+(?:[.]\d+)?))|''' + all_stat_pattern + '''
    [.]?)$
'''


# match 1: hp multi
# match 2: atk multi
# match 3: rcv multi
# match 4: type
# for ".... to ___ type cards"
basic_type_pattern = all_stat_pattern + r'''
    [ ]to[ ] ''' + type_pattern + '''
    [ ]type[ ]cards
'''

# match 1: min atk multi
# match 2: min rcv multi
# match 3: simultaneously or exactly
# match 4: min connected orbs
connected_pattern = active_multi_pattern + r'''
    [ ]when[ ]
    ((?:simultaneously[ ]clearing[ ])|(?:matching[ ]exactly[ ]))
    (\d+)[+]?[ ]connected[ ]\w+(?:[ ]or[ ].+?)?[ ]orbs
'''

# match 1: atk scale
# match 2: rcv scale
# match 3: atk max
# match 4: rcv max
# match 5: max connected orb
connected_scale_pattern = active_multi_pattern + r'''
    [ ]for[ ]each[ ]additional[ ]orb,
    [ ]up[ ]to[ ]''' + active_multi_pattern + r'''
    [ ]at[ ](\d+)[ ]connected[ ]orb
'''

# match 1: atk multi
# match 2: rcv multi
# match 3: shield
# match 4: min combo
# match 5: orb type
combo_pattern = r'''
    ^(?:all[ ]attribute[ ]cards[ ])?''' + active_multi_shield_pattern + r'''
    [ ](?:when[ ]reaching|at)[ ]
    (\d+)[ ](?:or[ ]more[ ])?
    (?:set[ ]of[ ](\w+)[ ])?
    combo(?:s)?(?:[ ]or[ ]above)?
'''

# match 1: atk multi
# match 2: rcv multi
# match 3: atk max
# match 4: rcv max
# match 5: max combo
combo_scale_pattern = active_multi_pattern + r'''
    [ ]for[ ]each[ ]additional[ ]combo,
    [ ]up[ ]to[ ]''' + active_multi_pattern + r'''
    [ ](?:at|(?:when[ ]reaching))[ ]
    (\d+)[ ]combos                        # max combos can be inferred
'''

# match 1: atk
# match 2: combos
combo_exact_pattern = r'''
    all[ ]attribute[ ]cards[ ]
    (?:atk[ ]x(\d+(?:\.\d+)?))
    [ ]when[ ]reaching[ ]exactly[ ]
    (\d+)[ ]combos
'''

# For "reaching x and/& x"
# match 1: atk multi
# match 2: rcv multi
# match 3: shield
# match 4: orb type
combo_orb_type_pattern = r'''
    all[ ]attribute[ ]cards[ ]''' + active_multi_shield_pattern + r'''
    [ ]when[ ](?:(?:attacking[ ]with))[ ](''' + orb_type_pattern + '''
    )[ ](?:and|&)[ ](?P=orb_type)
    [ ]combos(?:at[ ]the[ ]same[ ]time)?
'''

# For skills that give an atk multiplier for matching exactly 5 orbs with
# at least 1 enhanced
# match 1: atk multiplier
# match 2: number of connected orbs
# match 3: min number of enhanced orbs required
enhanced_match_pattern = r'''
    matched[ ]attribute[ ]
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]when[ ]matching[ ]exactly[ ]
    (\d+)[ ]connected[ ]orbs
    [ ]with[ ]at[ ]least[ ]
    (\d+)[ ]enhanced[ ](?:orbs|orb)
'''

# For skills that happen after matching heal orbs in a cross formation
# match 1: atk multi
# match 2: shield
heart_cross_pattern = r'''
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:reduce[ ]damage[ ]taken[ ]by[ ](\d+)%)?
    [ ]after[ ]matching[ ](?:heal|heart)[ ]orbs[ ]in[ ]a[ ]cross[ ]formation
'''

# For skills that activate when matching crosses of non-heart orbs
# match 1: atk multi
cross_pattern = r'''
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]for[ ]clearing[ ](?:\w+[ ])+?
    orbs[ ]in[ ]a[ ]cross[ ]formation
'''

color_match_pattern2 = r'''
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

# For skills that match exact color combinations
# match 1: atk multi
# match 2: rcv multi
# match 3: shield
# match 4: orb type string; will have punctuation and some other words
color_match_pattern = r'''
    all attribute cards''' + active_multi_shield_pattern + '''
    when attacking with ((?:[a-zA-Z]+\W+)+)at the same time
'''


no_skyfall_pattern = r'''
    no[ ]skyfall[ ]matches
'''

board_size_pattern = r'''
    change[ ]the[ ]board[ ]to[ ](\d+)x(\d+)[ ]size        #captures col and row
'''



move_time_pattern = r'''
    (fixed|increases)[ ]                            #captures fixed or increases
    (?:\w+[ ])*?orb[ ]movement(?:[ ]\w+)+?[ ]
    (\d+(?:\.\d+)?)[ ]seconds                       #captures time value    
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

""" Returns a json string representing a leader skill
parameters:
    skill_type:         the category the skill belongs to
    description:        the text of the skill
    hp, atk, rcv:       listed when the multiplier is decided without
                        any orb matching
    shield:             passive damage reduction. can be always on or
                        conditional
    orb_types:          a list of orbs types that are used in the skill
    attributes:         list of attributes that the skill effects
    types:              list of types that the skill effects
    atk_scale_type:     either "additive" or "multiplicative",
                        depending on the skill. A value here guarantees
                        a value for min_atk and atk_scale
    rcv_scale_type:     either "additive" or "multiplicative",
                        depending on the skill. A value here guarantees
                        a value for min_rcv and rcv_scale
    atk_scale:          the factor the atk multiplier gets increased by.
    rcv_scale:          the factor the rcv multiplier gets increased by.
    min_atk, min_rcv:   the minumum multipliers for skills that can
                        scale
    max_atk, max_rcv:   the maximum multiplier for skills that can
                        scale
    min_combo:          the minimum number of orb sets that need to be
                        matched to have the skill activate
    max_combo:          the maximum number of orb sets that are allowed
                        to be matched to have the skill activate
    min_connected:      minumum number of orbs needed to be in a match
                        for the skill to be activated
    max_connected:      maximum number of orbs allowed in a match for a skill
                        to be activated
    rows:               the number of rows on the board set by the skill
    cols:               the number of columns on the board set by the skill
    enemy_attributes:   the enemy attributes that the skill applies to
    hp_conditional_type:what the team's current hp% needs to be relative to
                        the threshold
                            - "<"
                            - "="
                            -">"
    hp_threshold:       the hp% that is compared to the team's current hp%http://us.asos.com/asos-petite/asos-petite-bardot-fluted-sleeve-midi-dress/prd/8387735?CTARef=Saved%20Items%20Title

"""
def format_skill(skill_type, description, hp=0, atk=0, rcv=0, shield=0,
                 orb_types=None, attributes=None, types=None,
                 atk_scale_type=None, atk_scale=0, min_atk=0, max_atk=0,
                 rcv_scale_type=None, rcv_scale=0, min_rcv=0, max_rcv=0,
                 min_combo=0, max_combo=0, min_connected=0, max_connected=0,
                 min_enhanced=0, min_orb_type_count=0, max_orb_type_count=0,
                 rows=0, cols=0, enemy_attributes=None,
                 hp_conditional_type=None, hp_threshold=0):
    result = "{\"skill_type\":\"" + skill_type + "\","
    result += "\"effect\":{"
    if hp:
        result += "\"hp\":" + str(hp) + ","
    if atk:
        result += "\"atk\":" + str(atk) + ","
    if rcv:
        result += "\"rcv\":" + str(rcv) + ","
    if shield:
        result += "\"shield\":" + str(shield) + ","
       
    if orb_types:
        result += "\"orb_types\":["
        for orb_type in orb_types:
            result += "\"" + orb_type + "\","
        result = result.strip(",") + "],"
        
    if attributes:
        result += "\"attributes\":["
        for attribute in attributes:
            result += "\"" + attribute + "\","
        result = result.strip(",") + "],"
        
    if types:
        result += "\"types\":["
        for type in types:
            result += "\"" + type + "\","
        result = result.strip(",") + "],"
       
    if atk_scale_type:
        result += "\"atk_scale_type\":\"" + atk_scale_type + "\","
        result += "\"atk_scale\":" + str(atk_scale) + ","
        result += "\"min_atk\":" + str(min_atk) + ","
        
    if max_atk:
        result += "\"max_atk\":" + str(max_atk) + ","
        
        
    if rcv_scale_type:
        result += "\"rcv_scale_type\":\"" + rcv_scale_type + "\","
        result += "\"rcv_scale\":" + str(rcv_scale) + ","
        result += "\"min_rcv\":" + str(min_rcv) + ","
        
    if max_rcv:
        result += "\"max_rcv\":" + str(max_rcv) + ","
        
    if min_combo:
        result += "\"min_combo\":" + str(min_combo) + ","
    if max_combo:
        result += "\"max_combo\":" + str(max_combo) + ","
        
    if min_connected:
        result += "\"min_connected\":" + str(min_connected) + ","
    if max_connected:
        result += "\"max_connected\":" + str(max_connected) + ","
     
    if min_enhanced:
        result += "\"min_enhanced\":" + str(min_enhanced) + "," 
     
    if min_orb_type_count:
        result += "\"min_orb_type_count\":" + str(min_orb_type_count) + ","
    if max_orb_type_count:
        result += "\"max_orb_type_count\":" + str(max_orb_type_count) + ","

    if enemy_attributes:
        result += "\"enemy_attributes\":["
        for attribute in enemy_attributes:
            result += "\"" + attribute + "\","
        result = result.strip(",") + "],"
    
    if hp_conditional_type:
        result += "\"hp_conditional_type\":\"" + hp_conditional_type + "\","
    if hp_threshold:
        result += "\"hp_threshold\":" + str(hp_threshold) + ","
    
    if rows:
        result += "\"rows\":" + str(rows) + ","
    if cols:
        result += "\"cols\":" + str(cols) + ","
    result = result.strip(",") + "},"
    
    result += "\"description\":\"" + description + "\""
    result += "},"
    return result

"""
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
"""

def get_basic_skill(regex_matches):
    #basic_str = regex_matches.group().strip(" ")
    description = regex_matches[0]
    
    attributes = attribute_re.findall(regex_matches[1])
    types = type_re.findall(regex_matches[1])

    hp = None
    atk = None
    rcv = None

    # matches all stat multiplier
    if regex_matches[2]:
        hp = regex_matches[2]
        atk = regex_matches[2]
        rcv = regex_matches[2]
    else:
        hp = regex_matches[3]
        atk = regex_matches[4]
        rcv = regex_matches[5]
            
    return format_skill("basic", description, hp=hp, atk=atk, rcv=rcv, attributes=attributes, types=types)

def get_basic_type_skill(match):
        des = match[0]
        hp = match[1]
        atk = match[2]
        rcv = match[3]
        types = [match[4]]
        return format_skill("basic", des, hp=hp, atk=atk, rcv=rcv, types=types)

def get_connected_combo(base_matches, scale_matches):
    # base matches      
    # match 1: min atk multi
    # match 2: min rcv multi
    # match 3: simultaneously or exactly
    # match 4: min connected orbs
    #
    # scale matches
    # match 1: atk scale
    # match 2: rcv scale
    # match 3: atk max
    # match 4: rcv max
    # match 5: max connected orb

    des = base_matches[0]
    min_atk = base_matches[1]
    connected_type = base_matches[3]
    start_count = base_matches[4]
    min_rcv = base_matches[2]
    atk_scale = None
    rcv_scale = None
    atk_scale_type = None
    rcv_scale_type = None
    
    if min_atk:
        atk_scale_type = "additive"
        atk_scale = 0
    
    if min_rcv:
        rcv_scale_type = "additive"
        rcv_scale = 0
    
    max_atk = min_atk
    max_rcv = min_rcv
    
    orb_type_re = re.compile(orb_type_pattern, re.IGNORECASE|re.VERBOSE)
    orb_type_m = orb_type_re.findall(base_matches[0])
    
    end_count = None
    
    if connected_type == "matching exactly ":
        end_count = start_count
    
    if scale_matches:    
        des += ". " + scale_matches[0]
        atk_scale = scale_matches[1]
        rcv_scale = scale_matches[2]
        max_atk = scale_matches[3]
        max_rcv = scale_matches[4]
    
    
        
    return format_skill("connected", des, orb_types=orb_type_m,
                        atk_scale_type=atk_scale_type, rcv_scale_type=rcv_scale_type,
                        atk_scale=atk_scale, min_atk=min_atk, max_atk=max_atk, 
                        rcv_scale=rcv_scale, min_rcv=min_rcv, max_rcv=max_rcv,
                        min_connected=start_count, max_connected=end_count, )
                       
def get_combo_skill(base_matches, scale_matches):
    # base matches
    # match 1: atk multi
    # match 2: rcv multi
    # match 3: shield
    # match 4: min combo
    # match 5: [orb type] 
    #
    # scale matches
    # match 1: atk multi
    # match 2: rcv multi
    # match 3: atk max
    # match 4: rcv max
    description = base_matches[0]
    min_atk = base_matches[1]
    min_rcv = base_matches[2]
    shield = base_matches[3]
    min_combo = base_matches[4]
    orb_types = [base_matches[5]] if base_matches[5] else None
    
    atk_scale_type = None
    rcv_scale_type = None
    atk_scale = None
    rcv_scale = None
    max_atk = min_atk
    max_rcv = min_rcv
    
    if min_atk:
        atk_scale_type = "additive"
        atk_scale = 0
        
    if min_rcv:
        rcv_scale_type = "additive"
        rcv_scale = 0

    if scale_matches:
        print(scale_matches)
        print(scale_matches[2])
        description += ". " + scale_matches[0]
        atk_scale = scale_matches[1]
        rcv_scale = scale_matches[2]
        max_atk = scale_matches[3]
        max_rcv = scale_matches[4]
        
    return format_skill("combo", description, min_atk=min_atk, max_atk=max_atk, 
                        atk_scale_type=atk_scale_type, atk_scale=atk_scale, min_combo=min_combo,
                        rcv_scale_type=rcv_scale_type, rcv_scale=rcv_scale, min_rcv=min_rcv, max_rcv=max_rcv,
                        shield=shield, orb_types=orb_types)

def get_combo_exact_skill(match):
    des = match[0]
    min_atk = match[1]
    max_atk = min_atk
    min_combo = match[2]
    max_combo = min_combo
    atk_scale_type = "additive"
    atk_scale = 0
    
    return format_skill("combo", des, min_atk=min_atk, max_atk=max_atk,
                        min_combo=min_combo, max_combo=max_combo,
                        atk_scale=atk_scale, atk_scale_type=atk_scale_type)

def get_enhanced_match(match):
    des = match[0]
    atk = match[1]
    orb_count = match[2]
    min_enhanced = match[3]
    
    return format_skill("enhanced_match", des, atk=atk, min_connected=orb_count,
                        max_connected=orb_count, min_enhanced=min_enhanced)
                        
def get_heart_cross_skill(match):
    des = match[0]
    atk = match[1] if match[1] else None
    shield = match[2] if match[2] else None

    return format_skill("heart_cross", des, atk=atk, shield=shield)
    
def get_cross_skill(match):
    # match is a list in the form [description, atk_scale]

    atk_scale = match[1]
    description = match[0]
    
    orb_type_re = re.compile(orb_type_pattern, re.IGNORECASE|re.VERBOSE)
    orb_types = orb_type_re.findall(description)
    
    atk_scale_type="multiplicative"
    min_atk=1
    
    return format_skill("cross", description, atk_scale_type=atk_scale_type,
                        min_atk=min_atk, atk_scale=atk_scale,
                        orb_types=orb_types)
    
    
def get_orb_type_combo_skill(match, scale_match):
    des = match[0]
    min_atk = match[1]
    min_combo = match[2]
    attributes = [match[3]]
    
    atk_scale_type = None
    atk_scale = 0
    max_atk = 0
    max_combo = 0
    if scale_match:
        des += ". " + scale_match[0]
        atk_scale_type = "additive"
        atk_scale = scale_match[1]
        max_atk = scale_match[2]
        max_combo = scale_match[3]
    return format_skill("combo", des, min_atk=min_atk, max_atk=max_atk,
                        atk_scale=atk_scale, atk_scale_type=atk_scale_type,
                        min_combo=min_combo, max_combo=max_combo, attributes=attributes)

    
def get_no_skyfall_skill(match):
    result = "{\"skilltype\":\"skyfall\","
    result += "\"effect\":{"
    result += "\"skyfall_type\":\"no skyfall\""
    result += "},"
    result += "\"description\":\"" + match[0] + "\""
    result += "},"
    
    return result
    
def get_board_size_skill(match):
    """
        returns a json string that represents the board size skill given in the
        regex match
        
        the regex match is a list in the format:
            [description, rows, cols]
        
        the format of the returned string is:
            {"skill_type":"board_size",
             "effect":{
                "rows": rows,
                "cols": cols
             },
             "description": description},
    """
    des = match[0]
    skill_type = "board_size"
    rows = match[1]
    cols = match[2]
    
    return format_skill(des, skill_type, rows=rows, cols=cols)
 
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


def get_color_match_skills(match):
    skill_type = "color_match"
    des = match[0]
    atk = match[1]
    rcv = match[2]
    shield = match[3]
    orbString = match[4]
    orb_type_re = re.compile(orb_type_pattern, re.IGNORECASE|re.VERBOSE)
    orb_types = orb_type_re.findall(orbString)
    return format_skill(skill_type, des, orb_types=orb_types, atk=atk, rcv=rcv, shield=shield)

def get_scaling_color_match_skills(match, scale_match):
    des = match[0]
    min_atk = match[1]
    rcv = match[2]
    min_count = match[3]
    shield = match[4]
    atk_scale_type = "additive"
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
    
    return format_skill("color_match", des, orb_types=orb_types, min_atk=min_atk,
                        max_atk=max_atk, atk_scale_type=atk_scale_type,
                        min_orb_type_count=min_count, max_orb_type_count=max_count,
                        atk_scale=atk_scale, rcv=rcv, shield=shield)
  
def get_two_color_match_skills(match):
    des = match[0]
    atk = match[1]
    rcv = match[2]
    shield = match[3]
    orb_types = [match[4], match[5]]
    return format_skill("color_match", des, orb_types=orb_types, atk=atk,
                        rcv=rcv, shield=shield)


def get_resolve_skill(resolve_m, extra_m):
    des = resolve_m[0] + ". " + extra_m[0]
    hp_threshold = resolve_m[1]
    
    return format_skill("resolve", des, hp_threshold=hp_threshold)

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
        
    return format_skill("skill_used", des, atk=atk, rcv=rcv, attributes=attributes, types=types)
  
def get_basic_damage_reduction_skill(match):
    des = match[0]
    value = match[1]
    attribute_re = re.compile(attribute_pattern, re.I|re.VERBOSE)
    enemy_attributes = attribute_re.findall(match[2])
    
    return format_skill("basic", des, enemy_attributes=enemy_attributes,
                        shield=value)
  
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
    return format_skill("hp_conditional", des, atk=atk, rcv=rcv,
                        hp_conditional_type=hp_type, hp_threshold=thresh)

def get_post_orb_elim_skill(match, extra=None):
    des = match[0]
    type = match[1].lower()
    value = match[2]
    atk = value if type == "atk" else 0
    rcv = value if type == "rcv" else 0
    
    if extra:
        des += ". " + extra[0]

    return format_skill("post_match", des, atk=atk, rcv=rcv)
    
    
def get_coop_skills(match):
    des = match[0]
    hp = 1
    atk = 1
    rcv = 1
    
    if match[1]:
        hp = match[1]
        atk = match[1]
        rcv = match[1]
        return format_skill("co-op", des, hp=match[1], atk=match[1], rcv=match[1])
    else:    
        return format_skill("co-op", des, hp=match[2], atk=match[3], rcv=match[4])
    
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
  
def get_skills(leader_json):
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
            i += 1
            

                
 
            basic_m = re.compile(basic_pattern, re.I|re.VERBOSE).search(part)
            if basic_m:
                result += get_basic_skill(basic_m)
                continue
            
            basic_type_m = (re.compile(basic_type_pattern, re.I|re.VERBOSE)
                              .search(part))
            if basic_type_m:
                result += get_basic_type_skill(basic_type_m)
                continue
                
            connected_m = (re.compile(connected_pattern, re.I|re.VERBOSE)
                             .search(part))
            if connected_m:
                scale_part = (leader_skill_parts[i] 
                              if i < len(leader_skill_parts) else None)
                if i < len(leader_skill_parts):
                    connected_scale_m = (re.compile(connected_scale_pattern, re.I|re.VERBOSE)
                                         .search(scale_part))
                    
                    if connected_scale_m:
                        result += get_connected_combo(connected_m, connected_scale_m)
                        i += 1
                        continue
                
                result += get_connected_combo(connected_m, None)
                continue

            combo_m = (re.compile(combo_pattern, re.I|re.VERBOSE)
                         .search(part))
            if combo_m:
                if i < len(leader_skill_parts):
                    scale_part = leader_skill_parts[i]
                    combo_scale_m = (re.compile(combo_scale_pattern, re.I|re.VERBOSE)
                                       .search(scale_part))
                    
                    if combo_scale_m:
                        result += get_combo_skill(combo_m, combo_scale_m)
                        i += 1
                        continue
                
                result += get_combo_skill(combo_m, None)
                continue
                
            combo_exact_m = (re.compile(combo_exact_pattern, re.I|re.VERBOSE)
                               .search(part))
            if combo_exact_m:
                result += get_combo_exact_skill(combo_exact_m)
                continue
                
            combo_orb_type_m = (re.compile(combo_orb_type_pattern, re.I|re.VERBOSE)
                                  .search(part))
            if combo_orb_type_m:
                result += get_combo_skill([combo_orb_type_m[0], 
                                           combo_orb_type_m[1],
                                           combo_orb_type_m[2],
                                           combo_orb_type_m[3],
                                           2, combo_orb_type_m[4]], None)
                continue

            enhanced_match_m = (re.compile(enhanced_match_pattern, re.I|re.VERBOSE)
                                  .search(part))
            if enhanced_match_m:
                result += get_enhanced_match(enhanced_match_m)
                continue
                
            heart_cross_re = re.compile(heart_cross_pattern, re.IGNORECASE|re.VERBOSE)
            heart_cross_m = heart_cross_re.search(part)
            if heart_cross_m:
                result += get_heart_cross_skill(heart_cross_m)
                continue


            cross_m = (re.compile(cross_pattern, re.IGNORECASE|re.VERBOSE)
                         .search(part))
            if cross_m:
                result += get_cross_skill(cross_m)
                continue
                
            """                 
                
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
                
            
            
            """
            """
            
            
            
            two_color_match_re = re.compile(two_color_match_pattern, re.IGNORECASE|re.VERBOSE)
            two_color_match_m = two_color_match_re.search(part)
            if two_color_match_m:
                result += get_two_color_match_skills(two_color_match_m)
                continue
                
                
            no_skyfall_re = re.compile(no_skyfall_pattern, re.IGNORECASE|re.VERBOSE)
            no_skyfall_m = no_skyfall_re.search(part)
            if no_skyfall_m:
                result += get_no_skyfall_skill(no_skyfall_m)
                continue
                
            board_size_re = re.compile(board_size_pattern, re.IGNORECASE|re.VERBOSE)
            board_size_m = board_size_re.search(part)
            if board_size_m:
                result += format_skill("board_size", board_size_m[0], 
                                               rows=board_size_m[1], cols=board_size_m[2])
                continue
                

                
            move_time_re = re.compile(move_time_pattern, re.IGNORECASE|re.VERBOSE)
            move_time_m = move_time_re.search(part)
            if move_time_m:
                result += get_move_time_skill(move_time_m)
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
                
            
                
            
            """
            print("NOT DONE: " + part)
            print(name)
            print()
            unfinished += 1
        result = result.strip(",") # fencepost problem
        result += "]},"
    result = result.strip(",")
    result += "]"
    
    print("UNFINISHED: " + str(unfinished) + "/" + str(count))
    return result
  
def main():
    file = open("comboSample.json")
    leader_json = json.load(file)
    
    if len(leader_json) is 0:
        return
    
    out_file = open("comboFormatted.json", "w", encoding="utf-8")
    out_file.write(get_skills(leader_json))
    out_file.close()
    file.close()
    


if __name__ == "__main__":
    main()