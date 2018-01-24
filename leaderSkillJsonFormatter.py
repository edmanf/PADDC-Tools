import json
import re
# TODO: Fix issues with ignore case: see mini zhao yun


# match 1: attribute
attribute_pattern = r'''
    (Fire|Water|Wood|Light|Dark|All)
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
    (?:ATK[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ]+)?
    (?:RCV[ ]x(\d+(?:\.\d+)?))?
'''

# match 1: hp multi
# match 2: atk multi
# match 3: rcv multi
all_stat_pattern = r'''
    (?:HP[ ]x(\d+(?:[.]\d+)?))?
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

# For skills that reduce something
# match 1: reduction %
# match 2: reduction target
basic_reduction_patter = r'''
    ^(\d+(?:\.\d+)?)%[ ](HP|(?:all[ ]damage))[ ]reduction\.?$
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

# For "attacking with x and/& x"
# match 1: atk multi
# match 2: rcv multi
# match 3: shield
# match 4: orb type
combo_orb_type_pattern = r'''
    all[ ]attribute[ ]cards[ ]''' + active_multi_shield_pattern + r'''
    [ ]when[ ](?:(?:attacking[ ]with)|reaching)[ ](''' + orb_type_pattern + '''
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

# For skills that activate when clearing a number of orb types that dont scale
# match 1: atk
# match 2: rcv
# match 3: shield
# match 4: number of cleared orb types needed
# match 5: possible orb types to choose from
color_match_pattern = r'''
    All[ ]attribute[ ]cards[ ]''' + active_multi_shield_pattern + '''
    [ ]when[ ]attacking[ ]with[ ]
    (\d+)[ ]of[ ](.*)[ ]
    orb[ ]types[ ]at[ ]the[ ]same[ ]time
'''

# For color match skills that can scale
# match 1: atk multi
# match 2: rcv multi
# match 3: shield
# match 4: number of matches needed to activate skill
# match 5: string containing the orb types that count towards the skill
color_scale_pattern = r'''
    ^All[ ]attribute[ ]cards[ ]''' + active_multi_shield_pattern + '''
    [ ]when[ ]attacking[ ]with[ ]
    (\d+)[ ]of[ ]following[ ]orb[ ]types:[ ]
    (.*)$
'''

# The scaling portion of a color match skill
# match 1: atk scale
# match 2: rcv scale
# match 3: atk max
# match 4: rcv max
# match 5: number of matches that the skill with scale up to
color_scale_extra_pattern = r'''
    ^''' + active_multi_pattern + '''
    [ ]for[ ]each[ ]additional[ ]orb[ ]type,[ ]
    up[ ]to[ ]''' + active_multi_pattern + '''
    for[ ]all[ ](\d+)[ ]matches\.?$
'''

# For skills that activate when two specific sets of different orb types are matched
# match 1: atk
# match 2: rcv
# match 3: shield
# match 4: first orb type
# match 5: second orb type
color_two_match_pattern = r'''
    ^All[ ]attribute[ ]cards[ ]''' + active_multi_shield_pattern + '''
    [ ]when[ ](?:(?:attacking[ ]with)|reaching)[ ]
    ''' + orb_type_pattern + '''[ ]
    (?:and|&)[ ](?!(?P=orb_type))(\w+)
    [ ]combos(?:[ ]at[ ]the[ ]same[ ]time)?\.?$
'''


# For skills that activate when a specific unit is in the team
# match 1: hp multi
# match 2: atk multi
# match 3: rcv multi
# match 4: teammate name
teammate_pattern = r'''
All[ ]attribute[ ]cards[ ]''' + all_stat_pattern + '''
[ ]when[ ](.*)
[ ]in[ ]the[ ]same[ ]team
'''

# For skills that activate based on remaining HP%
# match 1: attributes
# match 2: atk multi
# match 3: rcv multi
# match 4: hp threshold type
# match 5: hp threshold value (greater than or less than)
# match 6: hp threshold value/type: full (or = 1)
hp_conditional_pattern = r'''
    (?:(.*)[ ]attribute[ ]cards[ ])?''' + active_multi_pattern + '''
    [ ]when[ ]HP[ ]is[ ]
    (?:
    (?:((?:less[ ]than)|(?:greater[ ]than))[ ](\d+)%)
    |(full))
'''

# For skills that change board size
# match 1: cols
# match 2: rows
board_size_pattern = r'''
    Change[ ]the[ ]board[ ]to[ ]
    (\d+)x(\d+)[ ]size        
'''

# For skill that activate in cooperation mode
cooperation_pattern = all_stat_pattern + r'''
    [ ]in[ ]cooperation[ ]mode
'''

# For skills that change the number of orbs required for a match
# match 1: minimum number of orbs required for a match
minimum_connected_pattern = r'''
    Can[ ]no[ ]longer[ ]clear[ ](\d+)[ ](?:or[ ]less[ ])?connected[ ]orbs
'''

# For skills that prevent matches from skyfall
no_skyfall_pattern = r'''
    No[ ]skyfall[ ]matches
'''

# For skills that change orb movement time
# match 1: either "Fixed" or "Increases"
# match 2: time in seconds that movement is fixed to or increased by
move_time_pattern = r'''
    (Fixed|Increases)[ ]                            
    (?:(?:orb[ ]movement[ ]time[ ]at)
    |(?:time[ ]limit[ ]of[ ]orb[ ]movement[ ]by))[ ]
    (\d+(?:\.\d+)?)[ ]seconds
'''

# For skills that activate after orbs are cleared
# match 1: atk multi for dealing damage
# match 2: rcv multi for heal
post_orb_clear_pattern = r'''
    (?:
    (?:Deal[ ]ATK[ ]x(\d+(?:\.\d+)?)[ ]damage[ ]to[ ]all[ ]enemies[ ])|
    (?:Heal[ ]RCV[ ]x(\d+(?:\.\d+)?)[ ]as[ ]HP[ ])
    after[ ]every[ ]orbs[ ]elimination
    )
'''

# For extra text in post orb clear skills
post_orb_clear_extra_pattern = r'''
    Ignores[ ]enemy[ ]element,
    [ ]but[ ]can[ ]be[ ]reduced[ ]
    by[ ]enemy[ ]defense[ ]down[ ]to[ ]0[ ]damage
'''

# For skills that activate after a skill is used
skill_use_pattern = r'''
    (.*)?[ ]attribute[ ]cards[ ]''' + active_multi_pattern + '''
    [ ]on[ ]the[ ]turn[ ]a[ ]skill[ ]is[ ]used
'''

skill_use_extra_pattern = r'''
    \([ ]Multiple[ ]skills[ ]will[ ]not[ ]stack[ ]\)
'''

# For skills that deal counter damage after taking damage
# match 1: chance
# match 2: damage attribute
# match 3: damage multi
counter_pattern = r'''
    (\d+)%[ ]chance[ ]to[ ]deal[ ]counter[ ]
    (\w+)[ ]damage[ ]of[ ]
    (\d+(?:\.\d+)?)x[ ]damage[ ]taken
'''

# For skills that allow you to survive a lethal hit when above a certain hp
# match 1: hp threshold
resolve_pattern = r'''
    While[ ]your[ ]HP[ ]is[ ](\d+(?:\.\d+)?)%[ ]or[ ]above,[ ]a[ ]single[ ]
    hit[ ]that[ ]normally[ ]kills[ ]you[ ]will[ ]
    instead[ ]leave[ ]you[ ]with[ ]1[ ]HP
'''

resolve_extra_pattern = r'''
    For[ ]the[ ]consecutive[ ]hits,[ ]this[ ]skill[ ]
    will[ ]only[ ]affect[ ]the[ ]first[ ]hit
'''

# For skills that boost rewards after battle
# match 1: boost multiplier
# match 2: boost type
boost_pattern = r'''
    Get[ ]x(\d+(?:\.\d+)?)[ ]
    (experience|coins)[ ]after[ ]a[ ]battle
'''



"""

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

"""


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
                 hp_conditional_type=None, hp_threshold=0,
                 teammate=None, skyfall_matches=None,
                 move_time_type=None, time=None,
                 after_match_type=None, chance=None,
                 damage_multi=None, damage_attribute=None,
                 boost_type=None, boost=None,
                 min_match=None):
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
        
    if teammate:
        result += "\"teammate\":\"" + teammate + "\","
        print(teammate)
    
    if skyfall_matches:
        result += "\"skyfall_matches\":\"" + skyfall_matches + "\","
    
    if move_time_type:
        result += "\"move_time_type\":\"" + move_time_type + "\","
        result += "\"time\":" + str(time) + ","
    
    if after_match_type:
        result += "\"after_match_type\":\"" + after_match_type + "\","
    
    if chance:
        result += "\"chance\":" + str(chance) + ","
        
    if damage_multi:
        result += "\"damage_multi\":" + str(damage_multi) + ","
        result += "\"damage_attribute\":\"" + damage_attribute + "\","
        
    if boost_type:
        result += "\"boost_type\":\"" + boost_type + "\","
        result += "\"boost\":" + str(boost) + ","
        
    if min_match:
        result += "\"min_match\":" + str(min_match) + ","
        
        
    result = result.strip(",") + "},"
    
    result += "\"description\":\"" + description + "\""
    result += "},"
    return result


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

def get_basic_reduction_skill(match):
    des = match[0]
    reduction_type = match[2]
    if reduction_type == "HP":
        hp = float(match[1]) / 100.0
        return format_skill("basic", des, hp=hp)
    elif reduction_type == "all damage":
        return format_skill("basic", des, shield=match[1])
    else:
        return None
        
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

def get_color_two_match_skill(match):
    # match 1: atk
    # match 2: rcv
    # match 3: shield
    # match 4: first orb type
    # match 5: second orb type
    des = match[0]
    min_atk = max_atk = match[1]
    min_rcv = max_rcv = match[2]
    shield = match[3]
    orb_types = [match[4], match[5]]
    min_match = 2
    atk_scale_type = "additive"
    atk_scale = 0
    
    rcv_scale_type = "additive" if min_rcv else None
    rcv_scale = 0
    return format_skill("color_match", des, min_atk=min_atk, max_atk=max_atk,
                        min_rcv=min_rcv, max_rcv=max_rcv, shield=shield,
                        orb_types=orb_types, min_match=min_match,
                        atk_scale_type=atk_scale_type, atk_scale=atk_scale,
                        rcv_scale_type=rcv_scale_type, rcv_scale=rcv_scale)
    
def get_color_match_skill(match, extra):
    # match 1: atk
    # match 2: rcv
    # match 3: shield
    # match 4: number of cleared orb types needed
    # match 5: possible orb types to choose from
    des = match[0]
    atk_scale_type = None
    atk_scale = 0
    rcv_scale_type = None
    rcv_scale = 0
    min_atk = max_atk = match[1]
    if min_atk:
        atk_scale_type = "additive"
    min_rcv = max_rcv = match[2]
    if min_rcv:
        rcv_scale_type = "additive"
    shield = match[3]
    min_match = 4
    orb_types = re.compile(orb_type_pattern, re.I|re.VERBOSE).findall(match[5])
    
    return format_skill("color_match", des, atk_scale_type=atk_scale_type,
                        atk_scale=atk_scale, min_atk=min_atk, max_atk=max_atk,
                        rcv_scale_type=rcv_scale_type, rcv_scale=rcv_scale,
                        min_rcv=min_rcv, max_rcv=max_rcv, orb_types=orb_types,
                        min_match=min_match)
    
                        
def get_enhanced_match(match):
    des = match[0]
    atk = match[1]
    orb_count = match[2]
    min_enhanced = match[3]
    
    return format_skill("enhanced_match", des, atk=atk, min_connected=orb_count,
                        max_connected=orb_count, min_enhanced=min_enhanced)
                        
def get_heart_cross_skill(match):
    des = match[0]
    atk = match[1]
    shield = match[2]

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
    
def get_hp_cond_skill(match):
    """ Returns a json string representation of a hp conditional leader skill
        
        match is an array with the following properties
            match[0] - description of the leader skill
            match[1] - array of attributes that the skill applies to, or None
            match[2] - atk multiplier
            match[3] - rcv multiplier
            match[4] - the type of hp conditional, either "<" or ">"                       
            match[5] - the hp% that gets compared to current hp%
            match[6] - "full" if the skill activates when HP is full
                       None otherwise
    
    """
    des = match[0]
    attributes = None
    if match[1]:
        attributes = attribute_re.findall(match[1])
    atk = match[2]
    rcv = match[3]
    condition = None
    threshold = None
    if match[4]:
        if match[4] == "less than":
            condition = "<"
        elif match[4] == "greater than":
            condition = ">"
        threshold = match[5]
    else:
        # when hp is full
        condition = "="
        threshold = 100
    
    return format_skill("hp_conditional", des, atk=atk, rcv=rcv,
                        attributes=attributes, hp_conditional_type=condition,
                        hp_threshold=threshold)    

def get_post_orb_elim_skill(match, extra=None):
    des = match[0]
    if match[1]:
        atk = match[1]
        des += ". " + extra[0]
        after_match_type = "damage"
        return format_skill("after_match", des, atk=atk,
                            after_match_type="damage")
    else:
        return format_skill("after_match", des, rcv=match[2],
                            after_match_type="heal")

def get_skill_use_skill(match, extra):
    des = match[0]
    if extra:
        des += ". " + extra[0]
    atk = match[2]
    rcv = match[3]
    

    attributes = re.compile(attribute_pattern, re.I|re.VERBOSE).findall(match[1])
    types = re.compile(type_pattern, re.I|re.VERBOSE).findall(match[1])
    return format_skill("skill_use", des, atk=atk, rcv=rcv,
                        attributes=attributes, types=types)



'''  

 


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


    
   
  
  '''
  
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
                
            basic_reduction_m = (re.compile(basic_reduction_patter, re.VERBOSE)
                                   .search(part))
            if basic_reduction_m:
                result += get_basic_reduction_skill(basic_reduction_m)
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
            
            teammate_m = re.compile(teammate_pattern, re.I|re.VERBOSE).search(part)
            if teammate_m:
                result += format_skill("teammate", teammate_m[0], hp=teammate_m[1],
                                       atk=teammate_m[2], rcv=teammate_m[3],
                                       teammate=teammate_m[4])
                continue
            
            hp_conditional_m = (re.compile(hp_conditional_pattern, re.VERBOSE)
                                  .search(part))
            if hp_conditional_m:
                result += get_hp_cond_skill(hp_conditional_m)
                continue
            
            board_size_m = (re.compile(board_size_pattern, re.VERBOSE)
                              .search(part))
            if board_size_m:
                result += format_skill("board_size", board_size_m[0],
                                       cols=board_size_m[1],
                                       rows=board_size_m[2])
                continue
                
            cooperation_m = (re.compile(cooperation_pattern, re.VERBOSE)
                               .search(part))
            if cooperation_m:
                result += format_skill("cooperation", cooperation_m[0],
                                       hp=cooperation_m[1], atk=cooperation_m[2],
                                       rcv=cooperation_m[3])
                continue
              
            minimum_connected_m = (re.compile(minimum_connected_pattern, re.VERBOSE)
                                     .search(part))
            if minimum_connected_m:
                result += format_skill("min_connected", minimum_connected_m[0],
                                       min_connected=int(minimum_connected_m[1]) + 1)
                continue
                
            skyfall_m = (re.compile(no_skyfall_pattern, re.VERBOSE)
                           .search(part))
            if skyfall_m:
                result += format_skill("skyfall_matches", skyfall_m[0],
                                       skyfall_matches="none")
                continue
                   
            move_time_m = (re.compile(move_time_pattern, re.VERBOSE)
                             .search(part))
            if move_time_m:
                result += format_skill("move_time", move_time_m[0],
                                       move_time_type=move_time_m[1],
                                       time=move_time_m[2])
                continue
                
            post_orb_clear_m = (re.compile(post_orb_clear_pattern, re.VERBOSE)
                                  .search(part))
            extra_m = None
            if post_orb_clear_m:
                if i < len(leader_skill_parts):
                    extra_part = leader_skill_parts[i]
                    extra_m = (re.compile(post_orb_clear_extra_pattern, re.VERBOSE)
                                 .search(extra_part))
                    if extra_m:
                        i += 1
            
                result += get_post_orb_elim_skill(post_orb_clear_m, extra_m)
                continue
                        
            skill_use_m = re.compile(skill_use_pattern, re.VERBOSE).search(part)
            if skill_use_m:
                extra_m = None
                # TODO: extra part has typo, no period after ), need to fix
                if i < len(leader_skill_parts) and False:
                    extra_part = leader_skill_parts[i]
                    extra_m = (re.compile(skill_use_extra_pattern, re.VERBOSE)
                                 .search(extra_part))
                    if extra_m:
                        i += 1
                        
                result += get_skill_use_skill(skill_use_m, extra_m)
                continue
                
            counter_m = re.compile(counter_pattern, re.I|re.VERBOSE).search(part)
            if counter_m:
                result += format_skill("counter", counter_m[0], chance=counter_m[1],
                                       damage_multi=counter_m[3],
                                       damage_attribute=counter_m[2])
                continue
                
            resolve_m = re.compile(resolve_pattern, re.VERBOSE).search(part)
            if resolve_m:
                if i < len(leader_skill_parts):
                    extra_part = leader_skill_parts[i]
                    extra_m = (re.compile(resolve_extra_pattern, re.I|re.VERBOSE)
                                 .search(extra_part))
                    if extra_m:
                        i += 1
                        result += format_skill("resolve", resolve_m[0] + ". " + extra_m[0],
                                               hp_threshold=resolve_m[1])
                    else:
                        result += format_skill("resolve", resolve_m[0],
                                               hp_threshold=resolve_m[1])
                continue
                
            boost_m = re.compile(boost_pattern, re.VERBOSE).search(part)
            if boost_m:
                result += format_skill("boost", boost_m[0],
                                       boost=boost_m[1], boost_type=boost_m[2])
                continue
            
            color_two_match_m = (re.compile(color_two_match_pattern, re.I|re.VERBOSE)
                                   .search(part))
            if color_two_match_m:
                result += get_color_two_match_skill(color_two_match_m)
                continue
                
            color_match_m = re.compile(color_match_pattern, re.VERBOSE).search(part)
            if color_match_m:
                result += get_color_match_skill(color_match_m, None)
                continue
                
            color_match2_m = re.compile(color_match_pattern2, re.I|re.VERBOSE).search(part)
            if color_match2_m:
                result += format_skill("color_match2", color_match2_m[0])
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
    file = open("sampleIn\\colormatchSample.json")
    leader_json = json.load(file)
    
    if len(leader_json) is 0:
        return
    
    out_file = open("sampleOut\\colormatchOut.json", "w", encoding="utf-8")
    out_file.write(get_skills(leader_json))
    out_file.close()
    file.close()
    


if __name__ == "__main__":
    main()