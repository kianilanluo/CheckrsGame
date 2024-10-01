import tkinter as tk

# Constants for the game
BOARD_SIZE = 8
SQUARE_SIZE = 100
WHITE = "white"
BLACK = "black"
LIGHT_SQUARE = "#F0D9B5"
DARK_SQUARE = "#B58863"
HIGHLIGHT = "orange"
EMPTY = None


class CheckersGame:
    """
       A CheckersGame class that encapsulates the logic and graphical user interface for a game of Checkers.

       Attributes:
           master (tk.Tk): The main window for the tkinter application.
           canvas (tk.Canvas): A canvas widget to draw and manage the game's graphical components.
           current_player (str): Tracks the current player's turn, initially set to 'black'.
           board (list): A 2D list representing the state of the board, where each cell can hold a piece's color or None.
           selected_piece (tuple): Holds the row and column of the currently selected piece.
           ai_depth (tk.IntVar): Represents the depth of the AI's decision-making tree, used to control difficulty.
           hints_enabled (tk.BooleanVar): A boolean flag to toggle the display of possible moves for the player.

       Methods:
           __init__(self, master): Initializes the Checkers game with a given master widget.
           setup_ui(self): Sets up the user interface elements like buttons and bindings for the game.
           toggle_hints(self): Toggles the hint display on or off.
           show_hints(self): Displays possible moves for the current player's pieces if hints are enabled.
           clear_hints(self): Clears any move hints displayed on the board.
           ai_hint(self): Highlights the best moves determined by the AI based on current board state.
           initialize_board(self): Initializes the board with pieces placed in their standard starting positions.
           draw_board(self): Draws the board and pieces based on the current state of the game.
           board_click(self, event): Handles mouse clicks on the board to select pieces and make moves.
           process_click(self, row, col): Processes a click event based on the piece at the specified location.
           highlight_moves(self, row, col): Highlights all valid moves for the selected piece.
           possible_moves(self, board, player_color, row, col, is_chaining=False): Generates all possible moves for a given piece.
           simulate_move(self, board, start_row, start_col, end_row, end_col, is_capture=False): Simulates a move on the board and returns the new board state.
           is_within_board(self, row, col): Checks if a given row and column are within the board's boundaries.
           move_piece(self, row, col): Moves a piece from the selected position to the specified row and column.
           check_for_win(self): Checks if the current game state meets any of the win conditions.
           switch_players(self): Switches the turn between the two players.
           ai_move(self): Determines and executes the AI's move based on the current game state.
           minimax(self, board, depth, alpha, beta, maximizing_player): Implements the minimax algorithm for AI decision-making.
           evaluate_board(self, board): Evaluates and returns a score for the given board state.
           generate_moves_for_ai(self, board): Generates all possible moves for the AI player.
           generate_moves_for_player(self, board): Generates all possible moves for the human player.
           generate_moves_for_color(self, board, color): Generates all valid moves for pieces of the specified color.
           reset_game(self): Resets the game to its initial state.
           show_rules(self): Displays the game rules in a new window.
       """

    def __init__(self, master):
        self.master = master
        self.master.title("Checkers")
        self.canvas = tk.Canvas(self.master, width=SQUARE_SIZE * BOARD_SIZE, height=SQUARE_SIZE * BOARD_SIZE)
        self.canvas.pack()
        self.current_player = BLACK  # User starts as BLACK
        self.board = self.initialize_board()
        self.selected_piece = None
        self.ai_depth = tk.IntVar(value=2)  # Default to easy difficulty
        # Toggle hints button
        self.hints_enabled = tk.BooleanVar(value=False)
        hint_button = tk.Checkbutton(self.master, text="Toggle Hints", variable=self.hints_enabled,
                                     command=self.toggle_hints)
        hint_button.pack(side=tk.TOP, anchor='w')

        self.setup_ui()
        self.draw_board()

    def setup_ui(self):
        """
          Sets up the user interface elements of the Checkers game. This method is responsible for creating and
          positioning the UI components such as buttons and radio buttons for difficulty settings, and also establishes
          the event bindings for user interactions with the game canvas.

          This includes:
          - A button to show the game rules.
          - A button to start a new game.
          - Radio buttons to select the difficulty level of the AI (Easy, Normal, Hard).
          - Binding the left mouse click event to handle board clicks which drive the game's logic.

          Raises:
              None

          Returns:
              None
          """
        rules_button = tk.Button(self.master, text="Show Rules", command=self.show_rules)
        rules_button.pack(side=tk.TOP, anchor='e')
        reset_button = tk.Button(self.master, text="New Game", command=self.reset_game)
        reset_button.pack(side=tk.RIGHT)
        # Difficulty buttons
        tk.Radiobutton(self.master, text="Easy", variable=self.ai_depth, value=2).pack(side=tk.LEFT)
        tk.Radiobutton(self.master, text="Normal", variable=self.ai_depth, value=4).pack(side=tk.LEFT)
        tk.Radiobutton(self.master, text="Hard", variable=self.ai_depth, value=6).pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.board_click)

    def toggle_hints(self):
        """
        Toggles the display of possible move hints on the board. If hints are enabled, it shows them;
        otherwise, it clears any displayed hints and redraws the board.

        Raises:
            None

        Returns:
            None
        """
        if self.hints_enabled.get():
            self.show_hints()
        else:
            self.clear_hints()
            self.draw_board()

    def show_hints(self):
        """
         Displays possible moves for the current player's pieces as highlighted squares, if hints are enabled.
         It scans the board for potential moves and updates the board state to reflect these hints visually.

         Raises:
             None

         Returns:
             None
         """
        if not self.hints_enabled.get():
            return  # Ignore if hints are disabled

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == HIGHLIGHT:
                    self.board[r][c] = EMPTY

        has_moves = False
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.lower() == self.current_player:
                    moves = self.possible_moves(self.board, piece, row, col)
                    if moves:
                        has_moves = True
                        for _, (new_row, new_col), _ in moves:
                            self.board[new_row][new_col] = HIGHLIGHT

        if has_moves:
            self.draw_board()

    def clear_hints(self):
        """
        Clears any move hints displayed on the board by resetting the highlighted squares to their original state.

        Raises:
            None

        Returns:
            None
        """
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == HIGHLIGHT:
                    self.board[row][col] = EMPTY

    def ai_hint(self):
        """
        Highlights the best move(s) for the AI according to the minimax algorithm. It updates the board visually to
        show these moves.

        Raises:
            None

        Returns:
            None
        """
        best_score = float('-inf')
        best_moves = []
        for start_pos, end_pos, new_board in self.generate_moves_for_ai(self.board):
            score = self.minimax(new_board, self.ai_depth.get(), float('-inf'), float('inf'), False)
            if score > best_score:
                best_score = score
                best_moves = [end_pos]  # Store the best move end positions
            elif score == best_score:
                best_moves.append(end_pos)  # Add equally good moves

        # Highlight all the best moves
        for (row, col) in best_moves:
            self.canvas.create_rectangle(col * SQUARE_SIZE, row * SQUARE_SIZE,
                                         (col + 1) * SQUARE_SIZE, (row + 1) * SQUARE_SIZE,
                                         fill="blue", outline="")

    def initialize_board(self):
        """
        Initializes the board with a standard starting layout for a game of checkers.

        Raises:
            None

        Returns:
            list: A 2D list representing the initial state of the checkers board.
        """
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    if row < 3:
                        board[row][col] = BLACK
                    elif row > 4:
                        board[row][col] = WHITE
        return board

    def draw_board(self):
        """
        Draws the board and its pieces. This method refreshes the entire canvas based on the current board state, including drawing pieces and highlights.

        Raises:
            None

        Returns:
            None
        """
        self.canvas.delete("all")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x0, y0 = col * SQUARE_SIZE, row * SQUARE_SIZE
                x1, y1 = x0 + SQUARE_SIZE, y0 + SQUARE_SIZE
                fill_color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color)
                piece = self.board[row][col]
                if piece is not EMPTY and piece != HIGHLIGHT:
                    piece_color = BLACK if piece.lower() == BLACK else WHITE
                    self.canvas.create_oval(x0 + 10, y0 + 10, x1 - 10, y1 - 10, fill=piece_color, outline="")
                    if piece.isupper():
                        self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text='K', font=('Arial', 24), fill='red')
                elif piece == HIGHLIGHT:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=HIGHLIGHT, outline="")

    def board_click(self, event):
        """
        Handles mouse click events on the board, determining actions based on the location of the click.

        Args:
            event: The mouse event with coordinates.

        Raises:
            None

        Returns:
            None
        """
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        print(f"Clicked on row {row}, col {col}")
        possible_moves = self.generate_moves_for_player(self.board)
        if not possible_moves:  # Check if there are no possible moves for the player
            self.canvas.create_text(SQUARE_SIZE * BOARD_SIZE // 2, SQUARE_SIZE * BOARD_SIZE // 2,
                                    text="AI wins!", font=('Arial', 28, 'bold'), fill="blue")
            self.canvas.unbind("<Button-1>")
            return
        self.process_click(row, col)

    def process_click(self, row, col):
        """
        Processes a click on the board, determining whether it is a selection of a piece, a move, or an invalid action.

        Raises:
            None

        Returns:
            None
        """
        piece = self.board[row][col]
        if piece is not None and piece.lower() == self.current_player:
            if (self.current_player == BLACK and piece.islower()) or \
                    (self.current_player is WHITE and piece.islower()) or piece.isupper():
                self.highlight_moves(row, col)
            else:
                print("It's not your piece!")
        elif piece == HIGHLIGHT:
            self.move_piece(row, col)
        else:
            print("Not your turn or invalid move.")

    def highlight_moves(self, row, col):
        """
         Highlights valid moves for the selected piece, updating the board state to show these possibilities visually.

         Raises:
             None

         Returns:
             None
         """
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == HIGHLIGHT:
                    self.board[r][c] = EMPTY

        # Set the selected piece
        self.selected_piece = (row, col)
        player_color = self.board[row][col]
        possible_moves_list = self.possible_moves(self.board, player_color, row, col)

        # Apply new highlights for possible moves
        for _, (new_row, new_col), _ in possible_moves_list:
            self.board[new_row][new_col] = HIGHLIGHT

        # Redraw the board with new highlights
        self.draw_board()

    def possible_moves(self, board, player_color, row, col, is_chaining=False):
        """
        Generates all possible moves for a given piece on the board.

        Args:
            board (list): The current board state.
            player_color (str): The color of the player making the move.
            row (int): The row index of the piece.
            col (int): The column index of the piece.
            is_chaining (bool): Whether the move is part of a chain in multi-capture.

        Raises:
            None

        Returns:
            list: A list of tuples representing possible moves.
        """
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if board[row][col].isupper() else \
            [(-1, -1), (-1, 1)] if player_color == WHITE else [(1, -1), (1, 1)]
        capture_moves = []
        normal_moves = []

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_within_board(new_row, new_col):
                if board[new_row][new_col] == EMPTY and not is_chaining:
                    normal_moves.append(
                        ((row, col), (new_row, new_col), self.simulate_move(board, row, col, new_row, new_col)))
                elif board[new_row][new_col] not in [EMPTY, player_color, player_color.upper()] and board[new_row][
                    new_col].lower() != player_color.lower():
                    jump_row, jump_col = new_row + dr, new_col + dc
                    if self.is_within_board(jump_row, jump_col) and board[jump_row][jump_col] == EMPTY:
                        temp_board = self.simulate_move(board, row, col, jump_row, jump_col, True)
                        capture_moves.append(((row, col), (jump_row, jump_col), temp_board))
                        # Recursively check for further jumps from the new position
                        further_jumps = self.possible_moves(temp_board, player_color, jump_row, jump_col, True)
                        capture_moves.extend(further_jumps)

        if is_chaining:
            return capture_moves
        return capture_moves + normal_moves  # Normal moves are only added if not chaining

    def simulate_move(self, board, start_row, start_col, end_row, end_col, is_capture=False):
        """
        Simulates a move on the board and returns the new board state.

        Args:
            board (list): The current board state.
            start_row (int): The start row index of the move.
            start_col (int): The start column index of the move.
            end_row (int): The destination row index.
            end_col (int): The destination column index.
            is_capture (bool): Indicates if the move involves a capture.

        Raises:
            None

        Returns:
            list: The new board state after the move.
        """
        new_board = [row[:] for row in board]
        new_board[end_row][end_col] = new_board[start_row][start_col]
        new_board[start_row][start_col] = EMPTY
        if is_capture:
            mid_row, mid_col = (start_row + end_row) // 2, (start_col + end_col) // 2
            # Check if the captured piece is a king
            captured_piece = board[mid_row][mid_col]
            new_board[mid_row][mid_col] = EMPTY
            # If the captured piece is a king, the capturing piece becomes a king
            if captured_piece.isupper():
                new_board[end_row][end_col] = new_board[end_row][end_col].upper()
        if (end_row == 0 and new_board[end_row][end_col] == WHITE) or \
                (end_row == BOARD_SIZE - 1 and new_board[end_row][end_col] == BLACK):
            new_board[end_row][end_col] = new_board[end_row][end_col].upper()
        return new_board

    def is_within_board(self, row, col):
        """
        Checks if the specified position is within the valid range of the board's coordinates.

        Args:
            row (int): The row index to check.
            col (int): The column index to check.

        Raises:
            None

        Returns:
            bool: True if the position is within the board, False otherwise.
        """
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def move_piece(self, row, col):
        """
        Executes a move by updating the board state and redrawing the board.

        Args:
            row (int): The destination row index for the moving piece.
            col (int): The destination column index for the moving piece.

        Raises:
            None

        Returns:
            None
        """
        sr, sc = self.selected_piece
        new_board = self.simulate_move(self.board, sr, sc, row, col, abs(row - sr) == 2)
        self.board = new_board
        self.selected_piece = None

        # Clear any highlights after the move
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == HIGHLIGHT:
                    self.board[r][c] = EMPTY

        # Redraw the board with no highlights
        self.draw_board()
        self.master.update()

        # Check for win condition
        if not self.check_for_win():
            self.switch_players()
        else:
            # Unbind mouse clicks if the game is over to prevent further moves
            self.canvas.unbind("<Button-1>")

    def check_for_win(self):
        """
        Checks if the game has reached a win condition for either player.

        Raises:
            None

        Returns:
            bool: True if there is a winner or a draw, False otherwise.
        """
        white_count = sum(piece in [WHITE, WHITE.upper()] for row in self.board for piece in row)
        black_count = sum(piece in [BLACK, BLACK.upper()] for row in self.board for piece in row)
        if white_count == 0 or black_count == 0:
            winner = "Black" if white_count == 0 else "White"
            self.canvas.create_text(SQUARE_SIZE * BOARD_SIZE // 2, SQUARE_SIZE * BOARD_SIZE // 2,
                                    text=f"{winner} wins!", font=('Arial', 28, 'bold'), fill="blue")
            self.canvas.unbind("<Button-1>")
            return True
        return False

    def switch_players(self):
        """
        Alternates the turn between the two players.

        Raises:
            None

        Returns:
            None
        """
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        if self.current_player == WHITE:
            self.ai_move()

    def ai_move(self):
        """
        Determines and executes the best move for the AI based on the current board state.

        Raises:
            None

        Returns:
            None
        """
        possible_moves = self.generate_moves_for_ai(self.board)
        if not possible_moves:  # Check if there are no possible moves for AI
            self.canvas.create_text(SQUARE_SIZE * BOARD_SIZE // 2, SQUARE_SIZE * BOARD_SIZE // 2,
                                    text="User wins!", font=('Arial', 28, 'bold'), fill="red")
            self.canvas.unbind("<Button-1>")
            return
        best_score = float('-inf')
        best_move = None
        for start_pos, end_pos, new_board in self.generate_moves_for_ai(self.board):
            score = self.minimax(new_board, self.ai_depth.get(), float('-inf'), float('inf'), False)
            if score > best_score:
                best_score = score
                best_move = (start_pos, end_pos, new_board)
        if best_move:
            _, _, best_board = best_move
            self.board = best_board
            self.draw_board()
            if self.check_for_win():
                self.canvas.unbind("<Button-1>")
            else:
                self.current_player = BLACK
        self.hints_enabled.set(False)

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        A minimax algorithm with alpha-beta pruning to determine the best move for the AI.

        Args:
            board (list): The current board state.
            depth (int): The maximum depth to search.
            alpha (float): The alpha value for alpha-beta pruning.
            beta (float): The beta value for alpha-beta pruning.
            maximizing_player (bool): True if maximizing player, otherwise False.

        Raises:
            None

        Returns:
            float: The evaluation score of the board state.
        """
        if depth == 0:
            return self.evaluate_board(board)
        if maximizing_player:
            max_eval = float('-inf')
            for _, _, child in self.generate_moves_for_ai(board):
                evaluation = self.minimax(child, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for _, _, child in self.generate_moves_for_player(board):
                evaluation = self.minimax(child, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate_board(self, board):
        """
        Evaluates the board and returns a score based on the position and number of pieces for each player.

        Args:
            board (list): The board to evaluate.

        Raises:
            None

        Returns:
            int: The calculated score of the board.
        """
        score = 0
        for row in board:
            for piece in row:
                if piece == WHITE:
                    score += 1
                elif piece == WHITE.upper():
                    score += 2
                elif piece == BLACK:
                    score -= 1
                elif piece == BLACK.upper():
                    score -= 2
        return score

    def generate_moves_for_ai(self, board):
        """
        Generates all possible moves for the AI player based on the current board state.

        Args:
            board (list): The current board state.

        Raises:
            None

        Returns:
            list: A list of all possible moves for the AI.
        """
        return self.generate_moves_for_color(board, WHITE)

    def generate_moves_for_player(self, board):
        """
        Generates all possible moves for the human player based on the current board state.

        Args:
            board (list): The current board state.

        Raises:
            None

        Returns:
            list: A list of all possible moves for the player.
        """
        return self.generate_moves_for_color(board, BLACK)

    def generate_moves_for_color(self, board, color):
        """
        Generates all valid moves for pieces of the specified color.

        Args:
            board (list): The current board state.
            color (str): The color of the pieces for which to generate moves.

        Raises:
            None

        Returns:
            list: A list of all possible moves for the specified color.
        """
        all_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == color or board[row][col] == color.upper():
                    piece_moves = self.possible_moves(board, color, row, col)
                    all_moves.extend(piece_moves)
        return all_moves

    def reset_game(self):
        """
        Resets the game to its initial state, including the board and player turns.

        Raises:
            None

        Returns:
            None
        """
        self.board = self.initialize_board()
        self.current_player = BLACK
        self.draw_board()
        # Rebind the board click event
        self.canvas.bind("<Button-1>", self.board_click)

    def show_rules(self):
        """
        Displays the game rules in a new window.

        Raises:
            None

        Returns:
            None
        """
        rules_window = tk.Toplevel(self.master)
        rules_window.title("Checkers Rules")
        rules_text = """
        Checkers Rules
        Checkers is a classic board game, dating back to around 3000 BC. It is very simple, but a lot of fun! Checkers
        is known as Draughts in England and there are multiple variations of it all around the world.
        The game is played on an 8x8 chequered board, essentially a chess board. Each player starts with 12 pieces,
        placed on the dark squares of the board closest to them.
        The objective of the game is to capture all the opponent's pieces by jumping over them.


        Gameplay
        Pieces can only move diagonally on the dark squares, the light squares of the board are never used.
        A normal move is moving a piece diagonally forward one square. The initial pieces can only move
        forward diagonally, not backwards. You cannot move onto a square that is occupied by another piece.
        However, if an opponent piece is on the square diagonally in front of you and the square behind it is empty
        then you can (and must!) jump over it diagonally, thereby capturing it. If you land on a square where you can
        capture another opponent piece you must jump over that piece as well, immediately.
        One turn can capture many pieces. It is required to jump over pieces whenever you can.

        If a piece reaches the end row of the board, on the opponent's side, it becomes a King.
        Kings can move diagonally forwards and backwards, making them more powerful in jumping over opponent pieces.
        However, if you jump over a piece to become a King you can not jump backwards over another piece in the same
        move, you have to wait until the next turn to start moving backwards.

        Jumping over opponents is required. However, if you have two possible moves, where one jumps over one opponent
        and the other jumps over two or more opponents you are not required to take the jump with the most opponents
        captured, you are just required to take any jump move.


        Winning
        The game can end in four different ways:

        If a player has lost all his pieces he loses.
        If a player can't move at all, all his pieces are blocked, he loses.
        The exact same board state has come up three times without any men captured in between. The game ends in a draw.
        This is to avoid situation with two pieces left just moving around never being able to capture each other.
        There have been 100 moves (50 for each player) with no piece captured. The game ends in a draw.
        """
        tk.Label(rules_window, text=rules_text, justify=tk.LEFT, padx=10, pady=10, font=("Arial", 14), ).pack()
        close_button = tk.Button(rules_window, text="Close", command=rules_window.destroy)
        close_button.pack(pady=5)


def main():
    root = tk.Tk()
    game = CheckersGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()

