import sys
import copy
import random

from collections import deque
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP (constraint satisfaction problem) crossword generate.
        """
        self.crossword = crossword
        self.domains = {    # The domains must be restricted
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains_copy = copy.deepcopy(self.domains)
        for variable in domains_copy :
            for word in domains_copy[variable] :
                if len(word) != variable.length :
                    self.domains[variable].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False
        overlap = self.crossword.overlaps[x,y]
        if overlap is not None :
            i , j = overlap
            x_domain_copy = copy.deepcopy(self.domains[x])
            for wordX in x_domain_copy :
                if not any (wordX[i] == wordY[j] for wordY in self.domains[y] ) :
                    self.domains[x].remove(wordX)
                    revision = True
        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
         
        if arcs is None :
            arcs_list = []
            for x in self.domains :
                for y in self.crossword.neighbors(x) :
                    if self.crossword.overlaps[x,y] is not None :
                        arcs_list.append((x,y))
        else :
            arcs_list = list(arcs)
        queue = deque(arcs_list)
        while queue :
            x,y = queue.popleft()
            if self.revise(x,y) :
                if len(self.domains[x]) == 0 :
                    return False
                else :
                    for z in self.crossword.neighbors(x) :
                        if z != y :
                            queue.append((z,x))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains :
            if variable not in assignment or assignment[variable] is None :
                return False
        return True 

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check unary constraints
        for variable in assignment :
            if len(assignment[variable]) != variable.length :
                return False
        # Check binary constraints
        for variable1 in assignment :
            for variable2 in assignment :
                if variable1 == variable2 :
                    continue
                if assignment[variable1] == assignment[variable2] :
                    return False
        for variable in assignment :
            for neighbor in self.crossword.neighbors(variable) :
                i , j = self.crossword.overlaps[variable,neighbor]
                if neighbor not in assignment :
                    continue
                if assignment[variable][i] != assignment[neighbor][j] :
                    return False
        return True

    def order_domain_values(self, var, assignment):   # Least constraining value (LCV) heuristic
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        var_domain = self.domains[var]   # a set of words
        var_neighbors = self.crossword.neighbors(var)
        conflicts = {value : 0 for value in var_domain }
        for value in var_domain :
            for neighbor in var_neighbors :
                if neighbor in assignment :
                    continue
                i , j = self.crossword.overlaps[var,neighbor]
                for word_neighbor in self.domains[neighbor] :
                    if value[i] != word_neighbor[j] :
                        conflicts[value] += 1
        # look for the key with smallest value 
        return sorted(conflicts , key = lambda value : conflicts[value] )


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = [ var for var in self.domains if var not in assignment ]
        return min(unassigned_variables ,
                   key=lambda var : ( len(self.domains[var]) , -len(self.crossword.neighbors(var)) ) )

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment) :
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.domains[var] :
            assignment_copy = copy.deepcopy(assignment)
            assignment_copy[var] = value
            if self.consistent(assignment_copy) :
                result = self.backtrack(assignment_copy)
                if result is not None :
                    return result
        return None 


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
