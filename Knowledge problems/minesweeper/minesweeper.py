import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count :
            return self.cells
        return set()
        

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0 :
            return self.cells
        return set()
        

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells :
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells :
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # Mark the cell as a move that has been made 
        self.moves_made.add(cell)

        # Mark the cell as safe
        self.mark_safe(cell)

        # Add a new sentence to the knowledge base
        i , j = cell
        set_neighbors = set()
        new_count = count

        for row in range(i-1 , i+2) :
            for col in range(j-1 , j+2) :
                # Skip the cell itself
                if (row,col) == (i,j) :
                    continue
                if 0 <= row < self.height and 0 <= col < self.width :
                    neighbor = (row,col)
                    if neighbor in self.mines :
                        new_count -= 1
                    if neighbor in self.safes :
                        continue
                    else :
                        set_neighbors.add(neighbor)
        if len(set_neighbors) > 0 :
            new_sentence = Sentence(set_neighbors,new_count)
            self.knowledge.append(new_sentence)

        # Mark new cells as safe or as mines based on the knowledge
        self.check_new_cells()
        
        # Add new conclusions based on the existing knowledge
        self.inference()


    def check_new_cells(self):
        """
        mark any additional cells as safe or as mines
        if it can be concluded based on the AI's knowledge base
        """
        found_new = False
        knowledge_copy = copy.deepcopy(self.knowledge)
        for sentence in knowledge_copy :
            if len(sentence.cells) != 0 :
                mines = sentence.known_mines()
                safes = sentence.known_safes()
                if len(mines) != 0 :
                    for mine in mines :
                        self.mark_mine(mine)
                        found_new = True
                if len(safes) != 0 :
                    for safe in safes :
                        self.mark_safe(safe)
                        found_new = True
            else :
                try :
                    self.knowledge.remove(sentence)
                except Exception :
                    pass
        if found_new :
            self.check_new_cells()
 

    def inference(self) :
        """
        If, based on any of the sentences in the knowledge base , 
        new sentences can be inferred (using the subset method),
        then those sentences should be added to the knowledge base as well
        """
        new_sentences = []
        for sentence1 in self.knowledge :
            for sentence2 in self.knowledge :
                if sentence1 == sentence2 :
                    continue
                if sentence1.cells.issubset(sentence2.cells) :
                    new_cells = sentence2.cells - sentence1.cells 
                    new_count = sentence2.count - sentence1.count 
                    if new_count < 0 or len(new_cells) < new_count :
                        continue
                    new_sentence = Sentence(new_cells,new_count)
                    if len(new_cells) > 0 and new_sentence not in self.knowledge :
                        new_sentences.append(new_sentence)
        self.knowledge.extend(new_sentences)
        

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes :
            if move not in self.moves_made :
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = []
        for i in range(self.height) :
            for j in range(self.width) :
                move = (i,j)
                if move not in self.mines and move not in self.moves_made :
                    possible_moves.append(move)
        if len(possible_moves) > 0 :
            return random.choice(possible_moves)
        return None
