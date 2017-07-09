import json
import re

def main():
    #file = open("leaderskill.json")
    #leaderJson = json.load(file)
    
    #if len(leaderJson) is 0:
    #    return
        
    ex1 = "Dark attribute cards HP x2.5, ATK x2, RCV x1.5. All attribute cards ATK x3.5 when reaching Dark & Water combos."
    ex2 = "Attacker & Devil type cards HP x2, ATK x2. All attribute cards ATK x3.5 when reaching Fire & Water combos."
    ex3 = "Fire attribute & God type cards HP x1.5, ATK x2.5."
    ex4 = "God, Attacker & Devil type cards HP x1.5, ATK x3.5. All attribute cards ATK x2, RCV x2 when reaching Dark & Water combos."
    ex5 = "Fire & Water attribute cards ATK x2."
    ex6 = "Wood attribute cards ATK x3.5. Fire attribute cards HP x2."
    ex7 = "Wood attribute cards ATK x3.5. Fire attribute cards HP x2. ATK x1.5 for clearing each Wood orbs in a cross formation."
    ex8 = "Devil attribute cards All Stats x1.5. All attribute cards ATK x5 when attacking with Fire, Water, Wood & Dark orb types at the same time."
    #basic skills are just are type and attribute multipliers
    basicRe = re.compile(r'''
        ((((
        fire|water|wood|light|dark      #attributes
        |god|balance|attacker           #types
        |physical|devil|healer) 
        \W+ (attribute\W+|type\W+)?)+   #repeat for all attributes and types
   
        cards\W+
        
        ((hp|atk|rcv|all[ ]stats)[ ]x\d([.]\d)?,?[ ]?)+)[.][ ]?)+ #followed by multipliers

    ''', re.IGNORECASE|re.VERBOSE)
    
    
    
    m1 = basicRe.search(ex1)
    m2 = basicRe.search(ex2)
    m3 = basicRe.search(ex3)
    m4 = basicRe.search(ex4)
    m5 = basicRe.search(ex5)
    m6 = basicRe.search(ex6)
    m7 = basicRe.search(ex7)
    m8 = basicRe.search(ex8)
    print(ex1)
    print(m1.group())
    print()
    print(ex2)
    print(m2.group())
    print()
    print(ex3)
    print(m3.group())
    print()
    print(ex4)
    print(m4.group())
    print()
    print(ex5)
    print(m5.group())
    print()
    print(ex6)
    print(m6.group())
    print()
    print(ex7)
    print(m7.group())
    print()
    print(ex8)
    print(m8.group())
    
    
    

if __name__ == "__main__":
    main()