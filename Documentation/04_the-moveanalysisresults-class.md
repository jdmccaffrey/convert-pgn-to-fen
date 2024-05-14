<b>The MoveAnalysisResults Class</b>

I realized early on that the most difficult part of converting PGN to FEN would be determining where a piece came from. From a given game state and a move like white Nxf6, in order to update the six fields of a game state, I'd need to know quite a bit of information, including which piece moved (easy), where the moved piece landed (easy), where the moved piece came from (difficult), and so on.

This idea led to a design decision to implement a move_analysis(game_state, move) function where the result is all the information needed to update the current game state. So I defined a MoveAnaysisResults container class to hold the results of move_analysis() like so:

<pre>
# -------------------------------------------------------------------------------------------------

class MoveAnalysisResults:
  # return value for move_analysis()
  # container class for all the info needed for update_game_state()
  def __init__(self):
    self.piece_moved = "T"    # like "N" or "n" or "P"
    self.landing_square = -1  # like 23
    self.landing_piece = "U"  # needed in case of pawn promotion
    self.came_from_square = -1  # like 63
    self.ep_square = "V"        # if a pawn moves 2 squares
    self.capture = False        # for 50-move counter
    self.pawn_moved = False
    self.white_kingside_castle_invalid = False
    self.white_queenside_castle_invalid= False
    self.black_kingside_castle_invalid = False
    self.black_queenside_castle_invalid = False
    self.notes = "::"           # colon-separated error messages, etc.

  def display(self):
    print("piece_moved = " + self.piece_moved)
    print("landing_square = " + str(self.landing_square))
    print("landing_piece = " + self.landing_piece)
    print("came_from_square = " + str(self.came_from_square))
    print("ep_square = " + self.ep_square)
    print("capture = " + str(self.capture))
    print("pawn_moved = " + str(self.pawn_moved))

    print("white_kingside_castle_invalid = " + str(self.white_kingside_castle_invalid))
    print("white_queenside_castle_invalid = " + str(self.white_queenside_castle_invalid))
    print("black_kingside_castle_invalid = " + str(self.black_kingside_castle_invalid))
    print("black_queenside_castle_invalid = " + str(self.black_queenside_castle_invalid))
    print("notes = " + self.notes)

# -------------------------------------------------------------------------------------------------
</pre>

The class has 12 fields. Easy fields to compute directly from the move argument are piece_moved (like "N" or "n"), landing_square (like 18), capture (True or False), and pawn_moved (True or False).

The landing_piece field is needed because a pawn move can result in a new piece via promotion, usually a "Q" or "q" but possibly an underpromotion to knight, rook, or bishop.

To determining if a player/color has lost kingside or queenside castling privleges is mildly tricky. For example, if the white king moves, or castles to either side, or if black captures any white piece on square h1 (which means the captured piece was the white king's rook, or the white king's rook has already moved and the h1 square is now occupied by a different white piece, then white kingside castling privleges are lost.

Determining the en passant square (or "-"if none) is mildly tricky, but only if you know the exact definition of an FEN en passant square (see the 01_overview.md documentation file).

By far the most difficult field to compute is the came_from_square. For example, if the move is (white) Rxc6, the white rook could possibly come from 14 different squares (a6, b6, d6, e6, f6, g6, h6, c1, c2, c3, c4, c5, c7, c8). And if both with rooks could reach c6, then the PGN move must have a file hint, such as RfXc6, or a rank hint, such as R4Xc6.

Notice that there's no need to compute and store something like a color_moved field because a game state object contains that information directly.

Calling move_analysis() and displaying the MoveAnalysis results class looks like:

<pre>
  # first few moves of Ruy Lopez opening
  # 1. e4 e5 2. Nf3 Nf6 3. Bb5 a6 4. Ba4 Nf6 5. O-O
  fen_string = \
    "r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 3 5"
  print("\nFEN string first few moves of Ruy Lopez opening: ")
  print(fen_string)
  gs = GameState.from_fen(fen_string)
  print("\nGame State = ")
  gs.display()

  print("\nAnalysis for b5: ")
  mar = ChessFunctions.move_analysis("b5", gs)
  mar.display()
</pre>

The results are:

<pre>
FEN string first few moves of Ruy Lopez opening:
r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 3 5

Game State =
+---+---+---+---+---+---+---+---+
| r |   | b | q | k | b |   | r | 8
+---+---+---+---+---+---+---+---+
|   | p | p | p |   | p | p | p | 7
+---+---+---+---+---+---+---+---+
| p |   | n |   |   | n |   |   | 6
+---+---+---+---+---+---+---+---+
|   |   |   |   | p |   |   |   | 5
+---+---+---+---+---+---+---+---+
| B |   |   |   | P |   |   |   | 4
+---+---+---+---+---+---+---+---+
|   |   |   |   |   | N |   |   | 3
+---+---+---+---+---+---+---+---+
| P | P | P | P |   | P | P | P | 2
+---+---+---+---+---+---+---+---+
| R | N | B | Q |   | R | K |   | 1
+---+---+---+---+---+---+---+---+
  a   b   c   d   e   f   g   h
r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 3 5

Analysis for b5:
piece_moved = p
landing_square = 25
landing_piece = p
came_from_square = 9
ep_square = b6
capture = False
pawn_moved = True
white_kingside_castle_invalid = False
white_queenside_castle_invalid = False
black_kingside_castle_invalid = False
black_queenside_castle_invalid = False
notes = :::black pawn move to 5th rank, 2-step, therefore e.p. square exists on 4th rank, no capture, no promotion:
</pre>

The MoveAnalysisResults class stores dummy values in the fields to help track down bugs during development I'm not sure if this technique is a good practice or not.
