<b>Program Organization</b>

The code to convert PGN to FEN is contained in a single file named convert_pgn_to_fen.py. The file has three classes plus a main() function:

<pre>
# convert_pgn_to_fen.py
import numpy as np

class GameState:
  def __init__()
  def from_fen()
  def display()
  def get_fen()
  def show_board()

class MoveAnalysisResults:
  def __init__()
  def display()
  
class ChessFunctions:
  def __init__()

  # primary functions
  def file_pgn_to_file_fen(
  def pgn_to_fen(

  # secondary
  def update_game_state(
  def move_analysis(
  def can_reach(

  # helpers
  def square_algebraic_to_int()
  def square_int_to_algebraic()
  def square_matches_file_hint()
  def square_matches_rank_hint()
  def square_color()
  def square_file()
  def square_rank()
  def copy_of()
  def board_position_to_fen_string()
  def fen_string_to_board_position()  
  
def main()
  print("Begin ")
  . . .
  ChessFunctions.file_pgn_to_file_fen(source_pgn, dest_fen)
  . . .
  print("End ")

if __name__ == "__main__":
  main()
</pre>

The primary function is ChessFunctions.file_pgn_to_file_fen(). For example:

<pre>
  source_pgn = ".\\Data\\euwe_colle_karlsbad_1929.pgn"
  dest_fen = ".\\Data\\euwe_colle_karlsbad_1929.fen"
  print("Converting file " + source_pgn + " to FEN strings ")
  ChessFunctions.file_pgn_to_file_fen(source_pgn, dest_fen)
  print("Done ")
</pre>

All the functions in class ChessFunctions are static so they're all called by prepending "ChessFunctions." before the function name. The ChessFunctions.file_pgn_to_file_fen() function calls the ChessFunctions.pgn_to_fen() function.

The GameState class holds information that mirrors a FEN string state -- all the information needed to set up a position and start (or resume) playing. A GameState object is used to set up an initial game state and to hold the results of a call to ChessFunctions.update_state(). Each game state has an associated FEN string and the collection of all FEN strings is the goal of the file_pgn_to_file_fen() function.

The MoveAnalysisResults class holds all the information needed to update a GameState object. A MoveAnalysisResults object is returned by a call to the move_analysis() function. The move_analysis() function calls a can_reach() function that does a lot of work to compute where a piece came from.

To recap, the file_pgn_to_file_fen() function calls the pgn_to_fen() function which calls the update_state() function which calls the move_analysis() function which calls the can_reach() function. The update_state() function returns a GameState object. The move_analysis() function returns a MoveAnalysisResults object.

The 10 helper functions, such as square_color() to determine what color (black or white) square a piece is on, are used by the other funcctions.

The program organization might seem a bit overly-complicated, but the problem of converting PGN to FEN strings is much more difficult than you might expect.

Notice that the program file has only a dependency on the NumPy library -- just a single import. One of my design philosophies is to have as few external dependencies as possible.

All the functions and the two container classes have dependencies on each other. Therefore if you intend to use this code as part of some larger system, you might consider putting everything inside a single parent class with a name like Converter. Then you could drop the Converter class into your system and call functions along the lines of:

<pre><span class="inner-pre" style="font-size:12px">Converter.ChessFunctions.file_pgn_to_file_fen(source_pgn, dest_fen)
</span></pre>

I didn't wrap the converter code up into a single parent class because separated classes were easier to work with during development. Managing different versions of the code during development, even for a system as relatively simple as the PGN to FEN code, is a bit tricky at times.
