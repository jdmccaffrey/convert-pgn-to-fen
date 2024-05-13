# convert_pgn_to_fen.py

import numpy as np

# -------------------------------------------------------------------------------------------------

class GameState:
  # corresponds loosely to FEN string
  def __init__(self):
    self.board_position = np.empty(64, dtype=object)
    starting = "rnbqkbnr" + "pppppppp" + \
        "11111111" + "11111111" + "11111111" + "11111111" + \
        "PPPPPPPP" + "RNBQKBNR"
    for i in range(64):
      self.board_position[i] = starting[i]
    self.color_to_move = "w"
    self.castling_info = "KQkq"
    self.ep_square = "-"
    self.fifty_move_ctr = 0
    self.full_move_ctr = 1

  @staticmethod  # make a non-starting position state
  def from_fen(fen_string):
    result = GameState()  # no self. here
    tokens = fen_string.split(' ')
    board = ChessFunctions.fen_string_to_board_position(tokens[0])
    for i in range(64):
      result.board_position[i] = board[i]
    result.color_to_move = tokens[1]
    result.castling_info = tokens[2]
    result.ep_square = tokens[3]
    result.fifty_move_ctr = int(tokens[4])
    result.full_move_ctr = int(tokens[5])
    return result

  def display(self):
    self.show_board(self.board_position)
    fen_board = ChessFunctions.board_position_to_fen(self.board_position)
    print(fen_board + " ", end="")
    print(self.color_to_move + " ", end="")
    print(self.castling_info + " ", end="")
    print(self.ep_square + " ", end="")
    print(str(self.fifty_move_ctr) + " ", end="")
    print(str(self.full_move_ctr))

  def get_fen(self):
    fen = ChessFunctions.board_position_to_fen(self.board_position) + " " + \
      self.color_to_move + " " + self.castling_info + " " + self.ep_square + " " + \
      str(self.fifty_move_ctr) + " " + str(self.full_move_ctr)
    return fen
    
  @staticmethod
  def show_board(board_position):
    print("+---+---+---+---+---+---+---+---+")
    ptr = 0
    for i in range(8):  # 8 rows
      for j in range(8):  # 8 cols
        piece = board_position[ptr]
        if piece == "1": piece = " "
        print("| " + piece + " ", end="")
        ptr += 1
      print("| " + str(8 - i))
      print("+---+---+---+---+---+---+---+---+")
    print("  a   b   c   d   e   f   g   h  ")

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
    self.white_kingside_castle_invalid= False
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
    print("white_queenside_castle_invalid = " + str(self.white_kingside_castle_invalid))
    print("black_kingside_castle_invalid = " + str(self.black_kingside_castle_invalid))
    print("black_queenside_castle_invalid = " + str(self.black_queenside_castle_invalid))
    print("notes = " + self.notes)

# -------------------------------------------------------------------------------------------------

class ChessFunctions:

  # ------------------------------------------------------------------------------------------
  # primary: file_pgn_to_file_fen(), pgn_to_fen
  # secondary: update_game_state() calls move_analysis() calls can_reach
  # helpers: 
  # square_algebraic_to_int(), square_int_to_algebraic(),
  # square_matches_file_hint(), square_matches_rank_hint(),
  # square_color(), square_file(), square_rank(), 
  # copy_of(), board_position_to_fen_string(), fen_string_to_board_position()
  # ------------------------------------------------------------------------------------------

  def __init__(self):
    return

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def file_pgn_to_file_fen(source_pgn_file, dest_fen_file):
    # extract the pgn moves from src file, clean, send to pgn_to_fen(), write results
    ifp = open(source_pgn_file, "r")
    pgn = ""
    for line in ifp:
      if line.startswith("["): continue
      if line.startswith(" "): continue
      if line.startswith(";"): continue
      idx = line.find(";")  # remove to-end-of-line style comments
      if idx >= 0:
        line = line[:idx]
      line = line.strip()  # remove newline
      line += " "  # for parsing
      pgn += line
    ifp.close()

    # remove { xxx } style embedded comments
    start = pgn.find("{")
    while start >= 0:
      end = pgn.find("}")
      pgn = pgn[:start] + pgn[end+1:]
      start = pgn.find("{")  # look for next comment

    # remove triple dots
    pgn = pgn.replace("...", "")  # gets all occurences

    # add space after move numbers if not already there
    pgn = pgn.replace(".", ". ")
    # no double spaces allowed
    while pgn.find("  ") >= 0:
      pgn = pgn.replace("  ", " ")
    pgn = pgn.strip()  # final tidy up

    # get FEN strings
    fen_list = ChessFunctions.pgn_to_fen(pgn)

    # write FEN strings to output file
    ofp = open(dest_fen_file, "w")
    for i in range(len(fen_list)):
      ofp.write(fen_list[i] + "\n")
    ofp.close()

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def pgn_to_fen(pgn):
    # pgn is one big clean PGN string like 1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Bxf6 1-0
    # pgn ends with 1-0 or 0-1 or 1/2-1/2 or *
    # pgn string cannot have { } style comments or 17... Nf6 style black moves

    # checking anyway . . .
    pgn = pgn.replace(".", ". ")  # move numbers might have space after . or not
    pgn = pgn.replace("  ", " ")   # but double spaces not allowed

    results = []

    curr = GameState()
    results.append(curr.get_fen())  # initial position

    tokens = pgn.split(" ")  # like "e4", "e5", "Nf6", . . 
    for i in range(len(tokens)):
      if tokens[i][0] == "0" or tokens[i][0] == "1" or tokens[i][0] == "2" or \
        tokens[i][0] == "3" or tokens[i][0] == "4" or tokens[i][0] == "5" or \
        tokens[i][0] == "6" or tokens[i][0] == "7" or tokens[i][0] == "8" or \
        tokens[i][0] == "9":  # move number
        continue;
      if tokens[i] == "*": break  # special incomplete game

      move = tokens[i].strip()
      next = ChessFunctions.update_game_state(curr, move)
      fen = next.get_fen()
      results.append(fen)
      curr = ChessFunctions.copy_of(next)
    return results

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def update_game_state(curr_state, move):
    # 
    next_state = ChessFunctions.copy_of(curr_state)
    mar = ChessFunctions.move_analysis(move, curr_state)  # all info needed to update
    # GameState:
    # 1. board_position # not in FEN format 
    # 2. color_to_move # "w" or "b"
    # 3. castling_info # like "KQkq" or "Kq" or "-"
    # 4. ep_square # like "f3" or "-"
    # 5. fifty_move_ctr # number half-moves since pawn move or piece captured
    # 6. full_move_ctr

    # 1. update the board
    # special case of O-O and O-O-O. could have + or # appended
    # move_analysis() results not needed
    if move.find("O-O-O") >= 0 and curr_state.color_to_move == "w":
      next_state.board_position[58] = "K"
      next_state.board_position[59] = "R"
      next_state.board_position[56] = "1" # empty
      next_state.board_position[57] = "1"
      next_state.board_position[60] = "1"
    elif move.find("O-O") >= 0 and curr_state.color_to_move == "w":
      # checking this second -- would be caught by "O-O-O"
      next_state.board_position[62] = "K"
      next_state.board_position[61] = "R"
      next_state.board_position[60] = "1" # empty
      next_state.board_position[63] = "1"
    elif move.find("O-O-O") >= 0 and curr_state.color_to_move == "b":
      next_state.board_position[2] = "k"
      next_state.board_position[3] = "r"
      next_state.board_position[0] = "1" # empty
      next_state.board_position[1] = "1"
      next_state.board_position[4] = "1"
    elif move.find("O-O") >= 0 and curr_state.color_to_move == "b":
      next_state.board_position[6] = "k"
      next_state.board_position[5] = "r"
      next_state.board_position[4] = "1" # empty
      next_state.board_position[7] = "1"
    else:  # any move other than castles
      next_state.board_position[mar.landing_square] = mar.landing_piece
      next_state.board_position[mar.came_from_square] = "1"  # empty square code

    # 2. update player/color to move
    if curr_state.color_to_move == "w":
      next_state.color_to_move = "b"
    elif curr_state.color_to_move == "b":
        next_state.color_to_move = "w"

    # 3. update castling privilege info from KQkq to whatever
    if curr_state.castling_info == "-":
      next_state.castling_info = "-" # once privileges lost, never return
    else:
      new_info = ""
      for i in range(len(curr_state.castling_info)):  # 15 combinations
        symbol = curr_state.castling_info[i]  # like K or q
        if symbol == "K" and mar.white_kingside_castle_invalid == False: # ugly
          new_info += "K"  # king side castling still valid
        elif symbol == "Q" and mar.white_queenside_castle_invalid == False:
          new_info += "Q"
        elif symbol == "k" and mar.black_kingside_castle_invalid == False:
          new_info += "k"
        elif symbol == "q" and mar.black_queenside_castle_invalid == False:
          new_info += "q"
      
      if new_info == "":
        next_state.castling_info = "-"
      else:
        next_state.castling_info = new_info

    # 4. update the e.p. square (using FEN spec loose definition)
    next_state.ep_square = mar.ep_square

    # 5. update 50-move counter (half-move clock)
    if mar.pawn_moved == True or mar.capture == True:
      next_state.fifty_move_ctr = 0
    elif mar.pawn_moved == False and mar.capture == False:
      next_state.fifty_move_ctr = curr_state.fifty_move_ctr + 1

    # 6. update full-move counter
    if curr_state.color_to_move == "b":
      next_state.full_move_ctr = curr_state.full_move_ctr + 1
    else:
      next_state.full_move_ctr = curr_state.full_move_ctr

    return next_state
 
  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def board_position_to_fen(board_position):
    fen = ""
    consec_spaces = 0
    for i in range(len(board_position)):  # 64
      if i > 0 and i % 8 == 0: # just finished a row
        if consec_spaces > 0:  # flush
          fen += str(consec_spaces)
          consec_spaces = 0
        fen += "/"
      curr = board_position[i]
      if curr == "1":
        consec_spaces += 1
      else:   # curr is a piece token like "N" or "p"
        if consec_spaces > 0:
          fen += str(consec_spaces)  # flush
          fen += curr
          consec_spaces = 0
        else:
          fen += curr
    if consec_spaces > 0:  # flush blank spaces lower-right
      fen += str(consec_spaces)
      # consecSpaces = 0

    return fen

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def move_analysis(move, gs):
    # get all info needed to update curr GameState gs

    results = MoveAnalysisResults()
    # fill in with dummy values to find logic errors
    results.piece_moved = "J"
    results.landing_square = -100
    results.landing_piece = "K"
    results.came_from_square = -101
    results.ep_square = "m9"
    results.capture = False
    results.pawn_moved = False
    results.white_kingside_castle_invalid = False
    results.white_queenside_castle_invalid = False
    results.black_kingside_castle_invalid = False
    results.black_queenside_castle_invalid = False
    results.notes = "::" # error messages, etc.

    # deal with trailing + and # - strip to make move easier to parse
    if str(move[len(move) - 1]) == "+":
      move = move.replace("+", "")
    if str(move[len(move) - 1]) == "#":
      move = move.replace("#", "")

    # check for capture and remove "x" if there
    idx = move.find("x")  # -1 if not found
    if idx >= 0:
      move = move[:idx] + move[idx+1:]
      results.capture = True
    else:
      results.capture = False

    # ------------------------------------------------------------------------------------------

    # logic for non-pawns. (pawn moves and castling need separate logic)
    # very complicated so buckle up.

    if str(move[0]) == "R" or str(move[0]) == "N" or str(move[0]) == "B" or \
      str(move[0]) == "K" or str(move[0]) == "Q":
    
      results.pawn_moved = False
      results.ep_square = "-"  # FEN code

      piece_type_uncased = str(move[0]) # strictly upper like B
      piece_type_cased = piece_type_uncased  # for white
      if gs.color_to_move == "b": piece_type_cased = piece_type_cased.lower() # r b n k q

      results.piece_moved = piece_type_cased # N or n
      results.landing_piece = piece_type_cased  # only pawn can change via promotion

      # check for hints. trailing "+" "#" and "x" have been removed
      # moves with hints now look like Bac3 or N1c3 or Ba1c3
      has_full_hint = False # 
      has_file_hint = False # letter hint like the "a" in Raf7
      has_rank_hint = False # number hint like the "3" in R3f7

      file_hint = "z" # dummy value
      rank_hint = "z" # dummy value

      # move has full hint so came-from-square is completely known
      if len(move) == 5: # like Ba1c3 so full hint
        if has_full_hint == False:
          print("Fatal logic error in has_full_hint branch ")
        has_full_hint = True

        hint = move[1:3]  # Python strings are just arrays
        results.came_from_square = \
          ChessFunctions.square_algebraic_to_int(hint)  # no logic needed
        results.landing_square = \
          ChessFunctions.square_algebraic_to_int(move[3:5]) # like "c3"
        # TODO: check that move is possible

      # at this point, +, #, x removed, len(5) eliminated so len is 3 or 4
      elif len(move) == 4: # move has a file or rank hint like "a" in Raf7 or "3" in R3f7
        hint = str(move[1]) # could be file or rank hint
        if hint == "a" or hint == "b" or hint == "c" or \
          hint == "d" or hint == "e" or hint == "f" or \
          hint == "g" or hint == "h":
          has_file_hint = True
          file_hint = hint
        elif hint == "1" or hint == "2" or hint == "3" or \
          hint == "4" or hint == "5" or hint == "6" or \
          hint == "7" or hint == "8":
          has_rank_hint = True
          rank_hint = hint

        move = move[:1] + move[2:]  # strip the hint at [1] away (but it's been saved)

      # ----------------------------------------------------------------------------------------

      # at this point, all piece moves have been trimmed to len = 3, like Nf3

      if len(move) != 3: print("Fatal logic error. move len not 3 in move_analysis()")
      results.landing_square = \
        ChessFunctions.square_algebraic_to_int(move[1:3]) # like "f3"

      # we know the piece being moved, and square where it lands. where did it come from?
      # find all existing moved-pieces of correct color on the board that meet
      # file hint or rank hint if they exist. there should be only 1 piece
      # that meets all the criteria
      # note: full hint case has already been dealt with

      existing_piece_list = []  # actually the squares as int
      for i in range(64):  # check each square
        # no hint constraint
        if has_file_hint == False and \
        has_rank_hint == False and \
        ChessFunctions.can_reach(piece_type_uncased, i, results.landing_square,
          gs.board_position) == True and \
        gs.board_position[i] == piece_type_cased:
          existing_piece_list.append(i)

        # file hint constraint like the "c" in Nce6
        elif has_file_hint == True and \
        has_rank_hint == False and \
        ChessFunctions.square_matches_file_hint(i, file_hint) == True and \
        ChessFunctions.can_reach(piece_type_uncased, i, results.landing_square,
          gs.board_position) == True and \
        gs.board_position[i] == piece_type_cased:
          existing_piece_list.append(i)

        # rank hint constraint like the "5" in N5e6
        elif has_file_hint == False and \
        has_rank_hint == True and \
        ChessFunctions.square_matches_rank_hint(i, rank_hint) == True and \
        ChessFunctions.can_reach(piece_type_uncased, i, results.landing_square,
          gs.board_position) == True and \
        gs.board_position[i] == piece_type_cased:
          existing_piece_list.append(i)

      if len(existing_piece_list) == 0:
        print("Fatal Logic: no possible piece came-from squares found")
      elif len(existing_piece_list) >= 2:
        print("Fatal logic: 2 or more possible piece came-from squares")
      elif len(existing_piece_list) == 1:
        results.came_from_square = existing_piece_list[0]

      # filled in at this point: results.piece_moved, results.landing_piece,
      # results.came_from_square, results.landing_square, results.capture,
      # results.pawn_moved, results.ep_square.
      # need to deal with castling after a piece move. logic for white:
      # if K moved, kingside and queenside invalid.
      # if R moved from a1 queenside invalid
      # if R moved from h1, kingside invalid
      # if black captures on a1 or h1, white queenside, kingside invalid

      # if black pawn captures on a1 or h1 -- check in pawn logic
      # if O-O or O-O-O, -- check in the O-O and O-O-O branch

      # assume all castling is valid. if invalid, the reset to True isn't harmful
      if gs.color_to_move == "w": # check castling statuses after a white move
        if results.piece_moved == "K":
          results.white_kingside_castle_invalid = True
          results.white_queenside_castle_invalid = True
        elif results.piece_moved == "R" and results.came_from_square == 56: # a1
          results.white_queenside_castle_invalid = True
        elif results.piece_moved == "R" and results.came_from_square == 63: # h1
          results.white_kingside_castle_invalid = True
        elif results.capture == True and results.landing_square == 0:
          results.black_queenside_castle_invalid = True  # white captured on a8
        elif results.capture == True and results.landing_square == 7:
          results.black_kingside_castle_invalid = True   # white captured on h8
      elif gs.color_to_move == "b": # check castling statuses after a black move
        if results.piece_moved == "k":
          results.black_kingside_castle_invalid = True
          results.black_queenside_castle_invalid = True
        elif results.piece_moved == "r" and results.came_from_square == 0: # a8
          results.black_queenside_castle_invalid = True
        elif results.piece_moved == "r" and results.came_from_square == 7: # h8
          results.black_kingside_castle_invalid = True
        elif results.capture == True and results.landing_square == 56:
          results.white_queenside_castle_invalid = True # black captured on a1
        elif results.capture == True and results.landing_square == 63:
          results.white_kingside_castle_invalid = True # black captured on h1

      # TODO: add granular notes instead of this
      results.notes += ":RBNKQ  move or capture:"
      return results

    # end piece move or capture, R B N K Q (non-pawns)

    # ------------------------------------------------------
    # now the logic for pawn moves and captures - very tricky stuff
    # ------------------------------------------------------

    elif str(move[0]) == "a" or str(move[0]) == "b" or str(move[0]) == "c" or \
      str(move[0]) == "d" or str(move[0]) == "e" or str(move[0]) == "f" or \
      str(move[0]) == "g" or str(move[0]) == "h":
    
      # 1. if color = w and results.capture = False and pawn promo = False
      # 2. else if color = w and results.capture = False and pawn promo = True
      # 3. else if color = w and results.capture = True and pawn promo = False
      # 4. else if color = w and results.capture = True and pawn promo = True

      # 5. else if color = b and results.capture = False and pawn promo = False
      # 6. else if color = b and results.capture = False and pawn promo = True
      # 7. else if color = b and results.capture = True and pawn promo = False
      # 8. else if color = b and results.capture = True and pawn promo = True

      # at this point
      #  + , #, x, have already been removed. results.capture is set.
      #  = could be in move (promotion), no hints

      is_promotion = False
      if move.find("=") > 0:
        is_promotion = True

      # pawn mode or capture, branch 1
      if gs.color_to_move == "w" and results.capture == False and is_promotion == False: 
        # move like "e4" (2-step) or e4 (1-step from e3) or e7 (alaways 1-step)
        if len(move) != 2:
          print("logic error: move length not 2 in branch 1 pawn logic")

        if int(move[1]) != 4: # ordinary 1-step pawn move (not to 4th rank)
          results.piece_moved = "P"
          results.landing_piece = "P"
          results.landing_square = \
            ChessFunctions.square_algebraic_to_int(move)
          results.came_from_square = results.landing_square + 8
          results.ep_square = "-"
          results.capture = False
          results.pawn_moved = True  # reset 50-move ctr
          results.notes += ":white pawn move, 1-step, no capture, no promotion:"
          return results
        elif int(move[1]) == 4: # to 4th rank is possible 2-step move
          results.piece_moved = "P"
          results.landing_piece = "P"
          results.landing_square = \
            ChessFunctions.square_algebraic_to_int(move)
          if gs.board_position[results.landing_square + 8] == "P": # pawn came 1-step away
            results.came_from_square = results.landing_square + 8
            results.ep_square = "-"
            results.notes += ":white pawn move to 4th rank, " + \
              "could have been 2-step but was 1-step, no e.p., no capture, no promotion:"
          elif gs.board_position[results.landing_square + 16] == "P": # came 2-steps away
            #
            # "En passant target square: This is a square over which a pawn
            # has just passed while moving two squares it is given in
            # algebraic notation. If there is no en passant target square,
            # this field uses the character "-". This is recorded regardless
            # of whether there is a pawn in position to capture en passant.
            # An updated version of the spec has since made it so the target
            # square is recorded only if a legal en passant capture is
            # possible, but the old version of the standard is the one most
            # commonly used."
            #
            # this code uses the older, more common definiton
            #

            # ex: white move d4, not from d3, so e.p. square is d3
            results.came_from_square = results.landing_square + 16
            results.ep_square = \
              ChessFunctions.square_int_to_algebraic(results.landing_square + 8)
            results.notes += ":white pawn move to 4th rank, 2-step, therefore e.p. square" + \
              " exists, no capture, no promotion:"

          results.capture = False
          results.pawn_moved = True # reset 50-move ctr
          return results
      # branch 1

      # branch 2
      elif gs.color_to_move == "w" and results.capture == False and is_promotion == True:
        # move like e8=Q
        if len(move) != 4:
          print("move length not 4 in branch 2 pawn logic")
        results.piece_moved = "P"
        results.landing_piece = move[3] # usually Q
        results.landing_square = \
          ChessFunctions.square_algebraic_to_int(move[0:3])
        results.came_from_square = results.landing_square + 8
        results.ep_square = "-"
        results.capture = False
        results.pawn_moved = True  # reset 50-move ctr
        results.notes += ":white pawn move, no capture, promotion:"
        return results
      # branch 2 white no capture promo

      # pawn branch 3
      elif gs.color_to_move == "w" and results.capture == True and is_promotion == False:
        # move like exf6 or exf6+ but +,#,x have been zapped so only ef6 
        if len(move) != 3:
          print("logic error: move len not 3 in pawn move or capture branch 3")
        # a pawn capture cannot create an e.p. square
        results.piece_moved = "P"
        results.landing_piece = "P"
        results.landing_square = \
          ChessFunctions.square_algebraic_to_int(move[1:3])
        fromFile = move[0]  # for exf6+ -> ef6, the "e" part
        toFile = move[1]    # the "f" part
        if fromFile < toFile: # ex: ef6
          results.came_from_square = results.landing_square + 7
        elif fromFile > toFile: # ex: fe6
          results.came_from_square = results.landing_square + 9
        results.ep_square = "-"
        results.capture = True    # reset 50-move ctr
        results.pawn_moved = True # reset 50-move ctr
        results.notes += ":white pawn capture without promotion:"
        return results
      # branch 3 white capture no promo

      # pawn branch 4
      elif gs.color_to_move == "w" and results.capture == True and is_promotion == True:
        # move like exf8=Q has been shaved to ef8=Q
        if len(move) != 5:
          print("error: move length not 5 as expected to be, in pawn branch 4")
        results.piece_moved = "P"
        results.landing_piece = move[4] # usually a Q
        results.landing_square = \
          ChessFunctions.square_algebraic_to_int(move[1:3])
        fromFile = move[0]
        toFile = move[1]
        if fromFile < toFile: # ex: ef8
          results.came_from_square = results.landing_square + 7
        elif fromFile > toFile: # ex: fe6
          results.came_from_square = results.landing_square + 9

        results.ep_square = "-" # no e.p. happened
        results.capture = True  # reset 50-move ctr
        results.pawn_moved = True # reset 50-move ctr
        results.notes += ":white pawn capture on 8th rank with promotion to " + \
          results.landing_piece + ":"
        return results
      # branch 4 white capture promotion

      # =======================
      # ----- black pawn is moving
      # =======================

      # pawn move branch 5.
      elif gs.color_to_move == "b" and results.capture == False and is_promotion == False:
        # move like "d5" (possible 2-step) or d6 (1-step from e3) or d2 (always 1-step)
        if len(move) != 2:
          print("logic error: length not 2 in branch 5 pawn logic")

        if int(move[1]) != 5: # ordinary 1-step pawn move (not to 5th rank)
          results.piece_moved = "p"
          results.landing_piece = "p"
          results.landing_square = \
            ChessFunctions.square_algebraic_to_int(move)
          results.came_from_square = results.landing_square - 8
          results.ep_square = "-"
          results.capture = False
          results.pawn_moved = True   # reset 50-move ctr
          results.notes += ":black pawn move, 1-step, no capture, no promotion:"
          return results
        elif int(move[1]) == 5: # to 5th rank is possible 2-step move
          # move like "d5"
          results.piece_moved = "p"
          results.landing_piece = "p"
          results.landing_square = \
            ChessFunctions.square_algebraic_to_int(move)
          if gs.board_position[results.landing_square - 8] == "p": # from 1-step away
            results.came_from_square = results.landing_square - 8
            results.ep_square = "-"
            results.notes += ":black pawn move to 5th rank, could have been 2-step " + \
              "but was 1-step, no e.p., no capture, no promotion:"
          elif gs.board_position[results.landing_square - 16] == "p": # from 2-steps away
            # ex: black move d5, not from d6, so came from d7, so e.p. square is d6
            results.came_from_square = results.landing_square - 16
            results.ep_square = \
              ChessFunctions.square_int_to_algebraic(results.landing_square - 8)
            results.notes += ":black pawn move to 5th rank, 2-step, therefore e.p. " + \
              "square exists on 4th rank, no capture, no promotion:"

          results.capture = False
          results.pawn_moved = True  # reset 50-move ctr
          return results
      # branch 5

      # pawn branch 6
      elif gs.color_to_move == "b" and results.capture == False and is_promotion == True:
        # move like d1=Q
        if len(move) != 4:
          print("logic error: move length not 4 in branch 6 pawn logic")
        results.piece_moved = "p"
        results.landing_piece = move[3].lower() # usually Q -> to q
        results.landing_square = \
          ChessFunctions.square_algebraic_to_int(move[0:2])
        results.came_from_square = results.landing_square - 8
        results.ep_square = "-"
        results.capture = False
        results.pawn_moved = True # reset 50-move ctr
        results.notes += ":black pawn move, no capture, promotion:"
        return results
      # branch 6 black no capture promo

      # pawn branch 7
      elif gs.color_to_move == "b" and results.capture == True and is_promotion == False:
        # move like exf3 or exf3+ but +,#,x have been zapped so only ef3 
        if len(move) != 3:
          print("logic error: move len not 3 in pawn move or capture branch 7")
        # a pawn capture cannot create an e.p. square
        results.piece_moved = "p"
        results.landing_piece = "p"
        results.landing_square = \
          ChessFunctions.square_algebraic_to_int(move[1:3]) # the f3 part
        fromFile = move[0]  # for exf3+ -> ef3, the "e" part
        toFile = move[1]    # the "f" part
        if fromFile < toFile: # ex: ef3
          results.came_from_square = results.landing_square - 9
        elif fromFile > toFile: # ex: fe6
          results.came_from_square = results.landing_square - 7
        results.ep_square = "-"
        results.capture = True  # reset 50-move ctr
        results.pawn_moved = True # reset 50-move ctr
        results.notes += ":black pawn capture without promotion:"
        return results
      # branch 7 black capture no promo

      # pawn branch 8
      elif gs.color_to_move == "b" and results.capture == True and is_promotion == True:
        # move like exf1=Q has been shaved to ef1=Q
        if len(move) != 5:
          print("logic error: move length not 5 as expected to be," \
            + " in pawn branch 8")

        results.piece_moved = "p"
        results.landing_piece = move[4].lower()  # usually a Q (to q)
        results.landing_square = \
          ChessFunctions.square_algebraic_to_int(move[1:3]) # "f1"

        fromFile = move[0]
        toFile = move[1]
        if fromFile < toFile: # ex: ef1
          results.came_from_square = results.landing_square - 9
        elif fromFile > toFile: # ex: fe1
          results.came_from_square = results.landing_square - 7

        results.ep_square = "-" # no e.p. happened
        results.capture = True  # reset 50-move ctr
        results.pawn_moved = True # reset 50-move ctr
        results.notes += ":black pawn capture on 1st rank with promotion to " + \
          results.landing_piece + ":"
        return results
      # branch 8 black capture promotion

      # ----------------------------------------------------------------------------------------

      # now deal with castling validity after a pawn move or capture
      if gs.color_to_move == "w":
        if results.capture == True and results.landing_square == 0:
          results.black_queenside_castle_invalid = True # white pawn captured on a8
        elif results.capture == True and results.landing_square == 7:
          results.black_kingside_castle_invalid = True # white pawn captured on h8
      elif gs.color_to_move == "b":
        if results.capture == True and results.landing_square == 56:
          results.white_queenside_castle_invalid = True # black pawn captured on a1
        elif results.capture == True and results.landing_square == 63:
          results.white_kingside_castle_invalid = True # black pawn captured on h1

      return results

    # end pawn move or capture

    # ------------------------------------------------------------------------------------------

    elif move == "O-O" or move == "O-O-O":  # + and # have been stripped
      if gs.color_to_move == "w" and move == "O-O":
        results.piece_moved = "K"
        results.landing_square = 62 # g1
        results.landing_piece = "K"
        results.came_from_square = 60  # e1
        results.ep_square = "-"
        results.capture = False
        results.pawn_moved = False
        results.white_kingside_castle_invalid = True # cannot castle again
        results.white_queenside_castle_invalid = True
        results.black_kingside_castle_invalid = False
        results.black_queenside_castle_invalid = False
        results.notes = ":white kingside castle:"
      elif gs.color_to_move == "w" and move == "O-O-O":
        results.piece_moved = "K"
        results.landing_square = 58 # c1
        results.landing_piece = "K"
        results.came_from_square = 60  # e1
        results.ep_square = "-"
        results.capture = False
        results.pawn_moved = False
        results.white_kingside_castle_invalid = True
        results.white_queenside_castle_invalid = True
        results.black_kingside_castle_invalid = False
        results.black_queenside_castle_invalid = False
        results.notes = ":white queenside castle:"
      elif gs.color_to_move == "b" and move == "O-O":
        results.piece_moved = "k"
        results.landing_square = 6 # g8
        results.landing_piece = "k"
        results.came_from_square = 4  # e8
        results.ep_square = "-"
        results.capture = False
        results.pawn_moved = False
        results.white_kingside_castle_invalid = False
        results.white_queenside_castle_invalid = False
        results.black_kingside_castle_invalid = True
        results.black_queenside_castle_invalid = True
        results.notes = ":black kingside castle:"
      elif gs.color_to_move == "b" and move == "O-O-O":
        results.piece_moved = "k"
        results.landing_square = 2 # c8
        results.landing_piece = "k"
        results.came_from_square = 4  # e8
        results.ep_square = "-"
        results.capture = False
        results.pawn_moved = False
        results.white_kingside_castle_invalid = False
        results.white_queenside_castle_invalid = False
        results.black_kingside_castle_invalid = True
        results.black_queenside_castle_invalid = True
        results.notes = ":black queenside castle:"

      return results
    # castling moves

    return results  # default dummy values
  # move_analysis()

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def can_reach(piece_type_uncased, came_from_square, landing_square, board_position):
    # can landing square be reached from the specified (possible) came-from square?
    # similar logic for N B R Q K regradless of color
    # called by move_analysis()

    # knight jumps. order not critical here
    knight_offsets = np.array([-17, -15, -10, -6, 6, 10, 15, 17], dtype=np.int64)

    # bishop and queen diagonals. order critical to discover blocked paths
    up_offsets_left = np.array([-9, -18, -27, -36, -45, -54, -63], dtype=np.int64)
    up_offsets_right = np.array([-7, -14, -21, -28, -35, -42, -49], dtype=np.int64)
    down_offsets_left = np.array([ 9, 18, 27, 36, 45, 54, 63], dtype=np.int64)
    down_offsets_right = np.array([ 7, 14, 21, 28, 35, 42, 49], dtype=np.int64)

    # rook and queen left-right, up-down. order critical
    left_offsets = np.array([-1, -2, -3, -4, -5, -6, -7], dtype=np.int64)
    right_offsets = np.array([1, 2, 3, 4, 5, 6, 7 ], dtype=np.int64)
    up_offsets = np.array([-8, -16, -24, -32, -40, -48, -56], dtype=np.int64)
    down_offsets = np.array([8, 16, 24, 32, 40, 48, 56], dtype=np.int64)

    # king one square any direction (except castling)
    king_offsets = np.array([-1, 1, -8, 8, -9, 9, -7, 7], dtype=np.int64)

  # -----------------------------------------------------------------------------------------------

    if piece_type_uncased == "N":
      for i in range(len(knight_offsets)):
        test_square = landing_square + knight_offsets[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square:
          return True
      return False # unable to reach landing square from came-from-square
    # knight logic

  # -----------------------------------------------------------------------------------------------

    elif piece_type_uncased == "B": # same logic for white and black bishops
      # could make this efficient by computing which offsets to use (maybe later) 
      # work away from the landing square to try and eventually hit the came-from square
      # need a clear path

      # check up and to the left squares
      for i in range(len(up_offsets_left)):
        test_square = landing_square + up_offsets_left[i]  # possible came-from square
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_color(landing_square) == \
          ChessFunctions.square_color(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path
      # check up and to the right squares
      for i in range(len(up_offsets_right)):
        test_square = landing_square + up_offsets_right[i]  # possible came-from square
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_color(landing_square) == \
          ChessFunctions.square_color(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path
      # check down and to the left
      for i in range(len(down_offsets_left)):
        test_square = landing_square + down_offsets_left[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_color(landing_square) == \
          ChessFunctions.square_color(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path
      # check down and to right
      for i in range(len(down_offsets_right)):
        test_square = landing_square + down_offsets_right[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_color(landing_square) == \
          ChessFunctions.square_color(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path
 
      return False
    # end bishop logic

  # -----------------------------------------------------------------------------------------------

    elif piece_type_uncased == "R":
      # work away from the landing square to try and eventually hit the came-from square
      # need a clear path so order is important
      # left_offsets = [-1, -2, -3, -4, -5, -6, -7 ]
      # right_offsets = [1, 2, 3, 4, 5, 6, 7 ]
      # up_offsets = [-8, -16, -24, -32, -40, -48, -56 ]
      # down_offsets = [8, 16, 24, 32, 40, 48, 56 ]

      # could make this more efficient in severl ways . .
      for i in range(len(left_offsets)):
        test_square = landing_square + left_offsets[i]  # could wrap to wrong file
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_rank(landing_square) == \
          ChessFunctions.square_rank(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path

      for i in range(len(right_offsets)):
        test_square = landing_square + right_offsets[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_rank(landing_square) == \
          ChessFunctions.square_rank(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path

      for i in range(len(up_offsets)):
        test_square = landing_square + up_offsets[i]  # could wrap to wrong rank
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_file(landing_square) == \
          ChessFunctions.square_file(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path
 
      for i in range(len(down_offsets)):
        test_square = landing_square + down_offsets[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_file(landing_square) == \
          ChessFunctions.square_file(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path
 
      return False
    # end rook logic

  # -----------------------------------------------------------------------------------------------

    elif piece_type_uncased == "Q":
      # bishop-style movements
      for i in range(len(up_offsets_left)):
        test_square = landing_square + up_offsets_left[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_color(landing_square) == \
          ChessFunctions.square_color(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path

      for i in range(len(up_offsets_right)):
        test_square = landing_square + up_offsets_right[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_color(landing_square) == \
          ChessFunctions.square_color(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path

      for i in range(len(down_offsets_left)):
        test_square = landing_square + down_offsets_left[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_color(landing_square) == \
          ChessFunctions.square_color(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path
 
      for i in range(len(down_offsets_right)):
        test_square = landing_square + down_offsets_right[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_color(landing_square) == \
          ChessFunctions.square_color(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path

      # rook-style movements
      for i in range(len(left_offsets)):
        test_square = landing_square + left_offsets[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_rank(landing_square) == \
          ChessFunctions.square_rank(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path 

      for i in range(len(right_offsets)):
        test_square = landing_square + right_offsets[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_rank(landing_square) == \
          ChessFunctions.square_rank(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path

      for i in range(len(up_offsets)):
        test_square = landing_square + up_offsets[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_file(landing_square) == \
          ChessFunctions.square_file(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path

      for i in range(len( down_offsets)):
        test_square = landing_square + down_offsets[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square and ChessFunctions.square_file(landing_square) == \
          ChessFunctions.square_file(came_from_square):
          return True
        if board_position[test_square] != "1": break  # blocked path 

      return False
    # queen logic

  # -----------------------------------------------------------------------------------------------

    elif piece_type_uncased == "K":
      # king_offsets =[-1, 1, -8, 8, -9, 9, -7, 7]
      for i in range(len(king_offsets)):
        test_square = landing_square + king_offsets[i]
        if test_square < 0 or test_square > 63: continue
        if test_square == came_from_square:
          return True
        # blocked path not possible

      return False
    # king logic

    return False  # to keep compiler happy
  # can_reach()

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_color(square_id):
    if square_id == 0 or square_id == 2 or square_id == 4 or square_id == 6 or \
      square_id == 9 or square_id == 11 or square_id == 13 or square_id == 15 or \
      square_id == 16 or square_id == 18 or square_id == 20 or square_id == 22 or \
      square_id == 25 or square_id == 27 or square_id == 29 or square_id == 31 or \
      square_id == 32 or square_id == 34 or square_id == 36 or square_id == 38 or \
      square_id == 41 or square_id == 43 or square_id == 45 or square_id == 47 or \
      square_id == 48 or square_id == 50 or square_id == 52 or square_id == 54 or \
      square_id == 57 or square_id == 59 or square_id == 61 or square_id == 63:
      return "w"
    else:
      return "b"

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_file(square_id):
    if square_id % 8 == 0: return "a"
    elif (square_id - 1) % 8 == 0: return "b"
    elif (square_id - 2) % 8 == 0: return "c"
    elif (square_id - 3) % 8 == 0: return "d"
    elif (square_id - 4) % 8 == 0: return "e"
    elif (square_id - 5) % 8 == 0: return "f"
    elif (square_id - 6) % 8 == 0: return "g"
    elif (square_id - 7) % 8 == 0: return "h"
    return "z"  # error

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_rank(square_id):
    if square_id >= 0 and square_id <= 7: return "8"
    elif square_id >= 8 and square_id <= 15: return "7"
    elif square_id >= 16 and square_id <= 23: return "6"
    elif square_id >= 24 and square_id <= 31: return "5"
    elif square_id >= 32 and square_id <= 39: return "4"
    elif square_id >= 40 and square_id <= 47: return "3"
    elif square_id >= 48 and square_id <= 55: return "2"
    elif square_id >= 56 and square_id <= 63: return "1"
    return "0"  # error

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_algebraic_to_int(algebraic_id):
    # input like "h8", result like 7
    lookup = [
      "a8","b8","c8", "d8","e8", "f8", "g8", "h8",
      "a7","b7","c7", "d7","e7", "f7", "g7", "h7",
      "a6","b6","c6", "d6","e6", "f6", "g6", "h6",
      "a5","b5","c5", "d5","e5", "f5", "g5", "h5",
      "a4","b4","c4", "d4","e4", "f4", "g4", "h4",
      "a3","b3","c3", "d3","e3", "f3", "g3", "h3",
      "a2","b2","c2", "d2","e2", "f2", "g2", "h2",
      "a1","b1","c1", "d1","e1", "f1", "g1", "h1" ]
    idx = lookup.index(algebraic_id)  # not same as string find()
    return idx   # -1 on error

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_int_to_algebraic(integer_id):
    # input like 63, result like "h1"
    lookup = [
      "a8","b8","c8", "d8","e8", "f8", "g8", "h8",
      "a7","b7","c7", "d7","e7", "f7", "g7", "h7",
      "a6","b6","c6", "d6","e6", "f6", "g6", "h6",
      "a5","b5","c5", "d5","e5", "f5", "g5", "h5",
      "a4","b4","c4", "d4","e4", "f4", "g4", "h4",
      "a3","b3","c3", "d3","e3", "f3", "g3", "h3",
      "a2","b2","c2", "d2","e2", "f2", "g2", "h2",
      "a1","b1","c1", "d1","e1", "f1", "g1", "h1" ]
    return lookup[integer_id]

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_matches_file_hint(square_id, file_hint):
    # for example, square 63 matches file hint "h"
    if file_hint == "a" and square_id % 8 == 0: return True
    elif file_hint == "b" and (square_id - 1) % 8 == 0: return True
    elif file_hint == "c" and (square_id - 2) % 8 == 0: return True
    elif file_hint == "d" and (square_id - 3) % 8 == 0: return True
    elif file_hint == "e" and (square_id - 4) % 8 == 0: return True
    elif file_hint == "f" and (square_id - 5) % 8 == 0: return True
    elif file_hint == "g" and (square_id - 6) % 8 == 0: return True
    elif file_hint == "h" and (square_id - 7) % 8 == 0: return True
    else: return False

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def square_matches_rank_hint(square_id, rank_hint):
    # for example, square 15 matches rank hint "7"
    if rank_hint == "8" and square_id >= 0 and square_id <= 7: return True
    elif rank_hint == "7" and square_id >= 8 and square_id <= 15: return True
    elif rank_hint == "6" and square_id >= 16 and square_id <= 23: return True
    elif rank_hint == "5" and square_id >= 24 and square_id <= 31: return True
    elif rank_hint == "4" and square_id >= 32 and square_id <= 39: return True
    elif rank_hint == "3" and square_id >= 40 and square_id <= 47: return True
    elif rank_hint == "2" and square_id >= 48 and square_id <= 55: return True
    elif rank_hint == "1" and square_id >= 56 and square_id <= 63: return True
    else: return False

  # -----------------------------------------------------------------------------------------------

  @staticmethod
  def copy_of(gs):
    # copy of a GameState object, by value
    result = GameState()
    for i in range(64):
      result.board_position[i] = gs.board_position[i]
    result.color_to_move = gs.color_to_move
    result.castling_info = gs.castling_info
    result.ep_square = gs.ep_square
    result.fifty_move_ctr = gs.fifty_move_ctr
    result.full_move_ctr = gs.full_move_ctr
    return result

  # ----------------------------------------------------------------------------------------------

  @staticmethod
  def board_position_to_fen(board_position):
    # position[] like ".."R","1","1","1",..", FEN like "../R3K2R/.."
    fen = ""
    consec_spaces = 0
    for i in range(len(board_position)):  # 64
      if i > 0 and i % 8 == 0:  # just finished a row
        if consec_spaces > 0: # flush
          fen += str(consec_spaces)
          consec_spaces = 0
        fen += "/"

      curr = str(board_position[i])
      if curr == "1":
        consec_spaces += 1
      else:  # curr is a piece token like "N" or "p"
        if consec_spaces > 0:
          fen += str(consec_spaces)  # flush
          fen += curr
          consec_spaces = 0
        else:
          fen += curr

    if consec_spaces > 0:  # flush blank spaces lower-right
      fen += str(consec_spaces)
      # consec_spaces = 0

    return fen
  # board_position_To_fen()

# -------------------------------------------------------------------------------------------------

  @ staticmethod
  def fen_string_to_board_position(fen_string):
    # helper for from_fen() method in GameState
    # fen_string like "rnb2rk/pp5p/. ./RN1Q3K" (no castling info, move counter, etc.)
    # board position like "r", "n", "b", "1", "1", "r", "k", "p", "p" . . "K"
    result = np.empty(64, dtype=object)  # Python-ish array of strings
    ptr = 0  # into result
    for i in range(len(fen_string)):
      token = fen_string[i]  # a single-character string
      if token == "/": continue
      elif token == "r" or token == "n" or token == "b" or token == "q" or token == "k" or \
        token == "p" or \
        token == "R" or token == "N" or token == "B" or token == "Q" or token == "K" or \
        token == "P":
        result[ptr] = token; ptr += 1
      elif token == "1":  # single space
        result[ptr] = token; ptr += 1
      elif token == "2" or token == "3" or token == "4" or token == "5" or token == "6" or \
        token == "7" or token == "8":
        ct = int(token)
        for j in range(ct):
          result[ptr] = "1"; ptr += 1
    return result

# -------------------------------------------------------------------------------------------------

def main():
  print("\nBegin chess PGN to FEN demo ")

  # 1. convert a PGN file to file of FEN strings
  source_pgn = ".\\Data\\euwe_colle_karlsbad_1929.pgn"
  dest_fen = ".\\Data\\euwe_colle_karlsbad_1929.fen"
  print("\nConverting file " + source_pgn + " to FEN strings ")
  ChessFunctions.file_pgn_to_file_fen(source_pgn, dest_fen)
  print("Done ")

  # 2. walk through moves
  curr = GameState()  # initial position
  print("\ninitial position: "); curr.display()

  move = "e4"; print("\nmove = " + move)
  next = ChessFunctions.update_game_state(curr, move)
  next.display()
  curr = ChessFunctions.copy_of(next)

  move = "e5"; print("\nmove = " + move)
  next = ChessFunctions.update_game_state(curr, move)
  next.display()
  curr = ChessFunctions.copy_of(next)

  move = "Nf3"; print("\nmove = " + move)
  next = ChessFunctions.update_game_state(curr, move)
  next.display()
  curr = ChessFunctions.copy_of(next)

  # 3. show analysis for possible move
  print("\nAnalysis for possible move d6 needed to update Game State: ")
  mar = ChessFunctions.move_analysis("d6", curr)
  mar.display()

  # 4. create a specified initial position
  # first few moves of Ruy Lopez opening
  # 1. e4 e5 2. Nf3 Nf6 3. Bb5 a6 4. Ba4 Nf6 5. O-O
  fen_string = "r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 3 5"
  print("\nFEN string first few moves of Ruy Lopez opening: ")
  print(fen_string)
  gs = GameState.from_fen(fen_string)
  print("Game State from FEN string = ")
  gs.display()

  print("\nEnd ")

if __name__ == "__main__":
  main()

    
