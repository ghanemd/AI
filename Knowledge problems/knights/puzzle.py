from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(

    Or(AKnight,AKnave) ,    # A is a knight or a knave
    Not(And(AKnave,AKnight)) ,   #but not both at the same time

    Implication(AKnight,And(AKnave,AKnight)),     #If A is a knight then what he says is true
    Implication(AKnave,Not(And(AKnave,AKnight)))   #If A is a knave , then what he says is not true

)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(

    Or(AKnave,AKnight) ,
    Not(And(AKnight,AKnave)) ,

    Or(BKnave,BKnight) ,
    Not(And(BKnight,BKnave)) ,

    Implication(AKnight , And(AKnave,BKnave)) ,
    Implication(AKnave,Not(And(AKnave,BKnave)))

)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(

    Or(AKnave,AKnight) ,
    Not(And(AKnight,AKnave)) ,

    Or(BKnave,BKnight) ,
    Not(And(BKnave,BKnight)) ,

    Implication(AKnight , Or(And(AKnight , BKnight) , And(AKnave,BKnave)) ) ,
    Implication(AKnave , Not(Or(And(AKnight , BKnight) , And(AKnave,BKnave)))) ,

    Implication(BKnight , Or(And(AKnave,BKnight) , And(AKnight , BKnave)) ) ,
    Implication(BKnave , Not(Or(And(AKnave,BKnight) , And(AKnight , BKnave))))

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(

    Or(AKnave , AKnight) ,
    Not(And(AKnave , AKnight)) ,

    Or(BKnave , BKnight) , 
    Not(And(BKnave , BKnight)) ,

    Or(CKnave , CKnight) ,
    Not(And(CKnight , CKnave)) ,

    Or(
        # A said "I am a knight"
        And (
            Implication(AKnight , AKnight) ,
            Implication(AKnave , Not(AKnight))
        ) ,
        # A said "I am a knave"
        And(
            Implication(AKnight , AKnave) ,
            Implication(AKnave , Not(AKnave))
        )

    ) ,

    Not(And(
        # A said "I am a knight"
        And (
            Implication(AKnight , AKnight) ,
            Implication(AKnave , Not(AKnight))
        ) ,
        # A said "I am a knave"
        And(
            Implication(AKnight , AKnave) ,
            Implication(AKnave , Not(AKnave))
        )

    ) ) ,

    Implication(BKnight ,And(
            Implication(AKnight , AKnave) ,
            Implication(AKnave , Not(AKnave))
        ) ) ,

    Implication(BKnave , Not( And(
            Implication(AKnight , AKnave) ,
            Implication(AKnave , Not(AKnave))
        ) ) ) ,

    Implication(BKnight , CKnave) ,
    Implication(BKnave , Not(CKnave)) ,

    Implication(CKnight , AKnight) ,
    Implication(CKnave , Not(AKnight))

)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
