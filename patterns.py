"""
Defines various regex patterns for use in leaderSkillJsonFormatter.py
"""

# match 1: attribute
attributes = r'''
    (Fire|Water|Wood|Light|Dark|All)
'''

# match 1: type
# TODO: make sure removing "all" didn't break anything
types = r'''
    (
    god|balanced|attacker|physical
    |devil|healer|dragon|machine
    |evo[ ]material|awaken[ ]material
    |enhance[ ]material|redeemable[ ]material
    )
'''

# match 1: orb type
orb_types = r'''
    (?P<orb_type>fire|water|wood|light|dark|heal
    |heart|jammer|mortal[ ]poison|poison|all)
'''

# captures atk and/or rcv multipliers
# match 1: atk multi
# match 2: rcv multi
# TODO: fix double space typos in preproccessing so [ ]+ isn't neccessary
active_multi = r'''
    (?:ATK[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ]+)?
    (?:RCV[ ]x(\d+(?:\.\d+)?))?
'''

# match 1: hp multi
# match 2: atk multi
# match 3: rcv multi
all_stat = r'''
    (?:HP[ ]x(\d+(?:[.]\d+)?))?
    (?:,[ ])?''' + active_multi


# match 1: atk multi
# match 2: rcv multi
# match 3: shield
active_multi_shield = active_multi + r'''
    (?:,[ ])?
    (?:(\d+)%[ ]all[ ]damage[ ]reduction)?
'''

# match 1: attributes and types (requires further processing)
# match 2: all multi
# match 3: hp multi
# match 4: atk multi
# match 5: rcv multi
leader_basic = r'''
    (.*)(?:attribute|type)[ ]cards[ ]
    (?:
    (?:all[ ]stats[ ]x(\d+(?:[.]\d+)?))|''' + all_stat + '''
    [.]?)$
'''

# match 1: hp multi
# match 2: atk multi
# match 3: rcv multi
# match 4: type
# for ".... to ___ type cards"
leader_basic_type = all_stat + r'''
    [ ]to[ ] ''' + types + '''
    [ ]type[ ]cards
'''

# For skills that reduce something
# match 1: reduction %
# match 2: reduction target
leader_basic_reduction = r'''
    ^(\d+(?:\.\d+)?)%[ ](HP|(?:all[ ]damage))[ ]reduction\.?$
'''

# match 1: min atk multi
# match 2: min rcv multi
# match 3: simultaneously or exactly
# match 4: min connected orbs
leader_connected = active_multi + r'''
    [ ]when[ ]
    ((?:simultaneously[ ]clearing[ ])|(?:matching[ ]exactly[ ]))
    (\d+)[+]?[ ]connected[ ]\w+(?:[ ]or[ ].+?)?[ ]orbs
'''

# match 1: atk scale
# match 2: rcv scale
# match 3: atk max
# match 4: rcv max
# match 5: max connected orb
leader_connected_scale = active_multi + r'''
    [ ]for[ ]each[ ]additional[ ]orb,
    [ ]up[ ]to[ ]''' + active_multi + r'''
    [ ]at[ ](\d+)[ ]connected[ ]orb
'''

# match 1: atk multi
# match 2: rcv multi
# match 3: shield
# match 4: min combo
# match 5: orb type
leader_combo = r'''
    ^(?:all[ ]attribute[ ]cards[ ])?''' + active_multi_shield + r'''
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
leader_combo_scale = active_multi + r'''
    [ ]for[ ]each[ ]additional[ ]combo,
    [ ]up[ ]to[ ]''' + active_multi + r'''
    [ ](?:at|(?:when[ ]reaching))[ ]
    (\d+)[ ]combos                        # max combos can be inferred
'''

# match 1: atk
# match 2: combos
leader_combo_exact = r'''
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
leader_combo_orb_type = r'''
    all[ ]attribute[ ]cards[ ]''' + active_multi_shield + r'''
    [ ]when[ ](?:(?:attacking[ ]with)|reaching)[ ](''' + orb_types + '''
    )[ ](?:and|&)[ ](?P=orb_type)
    [ ]combos(?:at[ ]the[ ]same[ ]time)?
'''

# For skills that give an atk multiplier for matching exactly 5 orbs with
# at least 1 enhanced
# match 1: atk multiplier
# match 2: number of connected orbs
# match 3: min number of enhanced orbs required
leader_enhanced_match = r'''
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
leader_heart_cross = r'''
    (?:atk[ ]x(\d+(?:\.\d+)?))?
    (?:,[ ])?
    (?:reduce[ ]damage[ ]taken[ ]by[ ](\d+)%)?
    [ ]after[ ]matching[ ](?:heal|heart)[ ]orbs[ ]in[ ]a[ ]cross[ ]formation
'''

# For skills that activate when matching crosses of non-heart orbs
# match 1: atk multi
leader_cross = r'''
    atk[ ]x(\d+(?:\.\d+)?)
    [ ]for[ ]clearing[ ](?:\w+[ ])+?
    orbs[ ]in[ ]a[ ]cross[ ]formation
'''

# For skills that activate when clearing a number of orb types that dont scale
# match 1: atk
# match 2: rcv
# match 3: shield
# match 4: number of cleared orb types needed
# match 5: possible orb types to match
leader_color_match = r'''
    All[ ]attribute[ ]cards[ ]''' + active_multi_shield + '''
    [ ]when[ ]attacking[ ]with[ ]
    (?:(\d+)[ ]of[ ])?(.*)[ ]
    orb[ ]types[ ]at[ ]the[ ]same[ ]time
'''

# For color match skills that can scale
# match 1: atk multi
# match 2: rcv multi
# match 3: shield
# match 4: number of matches needed to activate skill
# match 5: string containing the orb types that count towards the skill
leader_color_scale = r'''
    ^All[ ]attribute[ ]cards[ ]''' + active_multi_shield + '''
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
leader_color_scale_extra = r'''
    ^''' + active_multi + '''
    [ ]for[ ]each[ ]additional[ ]orb[ ]type,[ ]
    up[ ]to[ ]''' + active_multi + '''
    [ ]for[ ]all[ ](\d+)[ ]matches\.?$
'''

# For skills that activate when two specific sets of different orb types are matched
# match 1: atk
# match 2: rcv
# match 3: shield
# match 4: first orb type
# match 5: second orb type
leader_color_two_match = r'''
    ^All[ ]attribute[ ]cards[ ]''' + active_multi_shield + '''
    [ ]when[ ](?:(?:attacking[ ]with)|reaching)[ ]
    ''' + orb_types + '''[ ]
    (?:and|&)[ ](?!(?P=orb_type))(\w+)
    [ ]combos(?:[ ]at[ ]the[ ]same[ ]time)?\.?$
'''


# For skills that activate when a specific unit is in the team
# match 1: hp multi
# match 2: atk multi
# match 3: rcv multi
# match 4: teammate name
leader_teammate = r'''
    All[ ]attribute[ ]cards[ ]''' + all_stat + '''
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
leader_hp_conditional = r'''
    (?:(.*)[ ]attribute[ ]cards[ ])?''' + active_multi + '''
    [ ]when[ ]HP[ ]is[ ]
    (?:
    (?:((?:less[ ]than)|(?:greater[ ]than))[ ](\d+)%)
    |(full))
'''

# For skills that change board size
# match 1: cols
# match 2: rows
leader_board_size = r'''
    Change[ ]the[ ]board[ ]to[ ]
    (\d+)x(\d+)[ ]size        
'''

# For skill that activate in cooperation mode
leader_cooperation = all_stat + r'''
    [ ]in[ ]cooperation[ ]mode
'''

# For skills that change the number of orbs required for a match
# match 1: minimum number of orbs required for a match
leader_minimum_connected = r'''
    Can[ ]no[ ]longer[ ]clear[ ](\d+)[ ](?:or[ ]less[ ])?connected[ ]orbs
'''

# For skills that prevent matches from skyfall
leader_no_skyfall = r'''
    No[ ]skyfall[ ]matches
'''

# For skills that change orb movement time
# match 1: either "Fixed" or "Increases"
# match 2: time in seconds that movement is fixed to or increased by
leader_move_time = r'''
    (Fixed|Increases)[ ]                            
    (?:(?:orb[ ]movement[ ]time[ ]at)
    |(?:time[ ]limit[ ]of[ ]orb[ ]movement[ ]by))[ ]
    (\d+(?:\.\d+)?)[ ]seconds
'''

# For skills that activate after orbs are cleared
# match 1: atk multi for dealing damage
# match 2: rcv multi for heal
leader_post_orb_clear = r'''
    (?:
    (?:Deal[ ]ATK[ ]x(\d+(?:\.\d+)?)[ ]damage[ ]to[ ]all[ ]enemies[ ])|
    (?:Heal[ ]RCV[ ]x(\d+(?:\.\d+)?)[ ]as[ ]HP[ ]))
    after[ ]every[ ]orbs[ ]elimination
'''

# For extra text in post orb clear skills
leader_post_orb_extra_clear = r'''
    Ignores[ ]enemy[ ]element,
    [ ]but[ ]can[ ]be[ ]reduced[ ]
    by[ ]enemy[ ]defense[ ]down[ ]to[ ]0[ ]damage
'''

# For skills that activate after a skill is used
leader_skill_use_pattern = r'''
    (.*)?[ ]attribute[ ]cards[ ]''' + active_multi + '''
    [ ]on[ ]the[ ]turn[ ]a[ ]skill[ ]is[ ]used
'''

leader_skill_use_extra_pattern = r'''
    \([ ]Multiple[ ]skills[ ]will[ ]not[ ]stack[ ]\)
'''

# For skills that deal counter damage after taking damage
# match 1: chance
# match 2: damage attribute
# match 3: damage multi
leader_counter = r'''
    (\d+)%[ ]chance[ ]to[ ]deal[ ]counter[ ]
    (\w+)[ ]damage[ ]of[ ]
    (\d+(?:\.\d+)?)x[ ]damage[ ]taken
'''

# For skills that allow you to survive a lethal hit when above a certain hp
# match 1: hp threshold
leader_resolve = r'''
    While[ ]your[ ]HP[ ]is[ ](\d+(?:\.\d+)?)%[ ]or[ ]above,[ ]a[ ]single[ ]
    hit[ ]that[ ]normally[ ]kills[ ]you[ ]will[ ]
    instead[ ]leave[ ]you[ ]with[ ]1[ ]HP
'''

leader_resolve_extra = r'''
    For[ ]the[ ]consecutive[ ]hits,[ ]this[ ]skill[ ]
    will[ ]only[ ]affect[ ]the[ ]first[ ]hit
'''

# For skills that boost rewards after battle
# match 1: boost multiplier
# match 2: boost type
leader_boost = r'''
    Get[ ]x(\d+(?:\.\d+)?)[ ]
    (experience|coins)[ ]after[ ]a[ ]battle
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
