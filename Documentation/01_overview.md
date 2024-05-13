<b>Programmatically Converting Chess PGN to FEN - Overview</b>

I recently explored the idea of programmatically analyzing individual chess positions and full chess games. See https://jamesmccaffrey.wordpress.com/2024/05/02/programmatically-analyzing-chess-games-using-stockfish-with-python/. The technique I used requires all chess positions to be in FEN (Forsyth–Edwards Notation) format. But chess games are almost always stored in PGN (Portable Game Notation) format.

In order to do any serious programmatic chess analysis, I need the ability to programmatically convert PGN to FEN. For example, here's a basic PGN file:

<pre>
[Event "Karlsbad"]
[Site "Karlsbad CSR"]
[Date "1929.08.18"]
[Round "15"]
[White "Max Euwe"]
[Black "Edgar Colle"]
[Result "1-0"]

1.Nf3 Nf6 2.d4 e6 3.c4 b6 4.g3 Bb7 5.Bg2 Bb4+ 6.Bd2 Bxd2+
7.Nbxd2 d6 8.O-O O-O 9.Re1 Nbd7 10.Qc2 e5 11.Nxe5 Bxg2 12.Nxd7
Bh3 13.Nxf8 1-0
</pre>

The first seven tags are supposed to be mandatory, and listed in the order shown. If a value is not applicable or not known, it's given a "?" value. Unfortunately, the PGN specification is very long and difficult to interpret, and so many PGN files have different formats. For example, the PGN specification is not clear whether move numbers should have a space after the dot, or no space. The example above has no space after the move dot.

This game, converted to FEN strings, is:

<pre>
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1
rnbqkb1r/pppppppp/5n2/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 2 2
rnbqkb1r/pppppppp/5n2/8/3P4/5N2/PPP1PPPP/RNBQKB1R b KQkq d3 0 2
rnbqkb1r/pppp1ppp/4pn2/8/3P4/5N2/PPP1PPPP/RNBQKB1R w KQkq - 0 3
rnbqkb1r/pppp1ppp/4pn2/8/2PP4/5N2/PP2PPPP/RNBQKB1R b KQkq c3 0 3
rnbqkb1r/p1pp1ppp/1p2pn2/8/2PP4/5N2/PP2PPPP/RNBQKB1R w KQkq - 0 4
rnbqkb1r/p1pp1ppp/1p2pn2/8/2PP4/5NP1/PP2PP1P/RNBQKB1R b KQkq - 0 4
rn1qkb1r/pbpp1ppp/1p2pn2/8/2PP4/5NP1/PP2PP1P/RNBQKB1R w KQkq - 1 5
rn1qkb1r/pbpp1ppp/1p2pn2/8/2PP4/5NP1/PP2PPBP/RNBQK2R b KQkq - 2 5
rn1qk2r/pbpp1ppp/1p2pn2/8/1bPP4/5NP1/PP2PPBP/RNBQK2R w KQkq - 3 6
rn1qk2r/pbpp1ppp/1p2pn2/8/1bPP4/5NP1/PP1BPPBP/RN1QK2R b KQkq - 4 6
rn1qk2r/pbpp1ppp/1p2pn2/8/2PP4/5NP1/PP1bPPBP/RN1QK2R w KQkq - 0 7
rn1qk2r/pbpp1ppp/1p2pn2/8/2PP4/5NP1/PP1NPPBP/R2QK2R b KQkq - 0 7
rn1qk2r/pbp2ppp/1p1ppn2/8/2PP4/5NP1/PP1NPPBP/R2QK2R w KQkq - 0 8
rn1qk2r/pbp2ppp/1p1ppn2/8/2PP4/5NP1/PP1NPPBP/R2Q1RK1 b kq - 1 8
rn1q1rk1/pbp2ppp/1p1ppn2/8/2PP4/5NP1/PP1NPPBP/R2Q1RK1 w - - 2 9
rn1q1rk1/pbp2ppp/1p1ppn2/8/2PP4/5NP1/PP1NPPBP/R2QR1K1 b - - 3 9
r2q1rk1/pbpn1ppp/1p1ppn2/8/2PP4/5NP1/PP1NPPBP/R2QR1K1 w - - 4 10
r2q1rk1/pbpn1ppp/1p1ppn2/8/2PP4/5NP1/PPQNPPBP/R3R1K1 b - - 5 10
r2q1rk1/pbpn1ppp/1p1p1n2/4p3/2PP4/5NP1/PPQNPPBP/R3R1K1 w - - 0 11
r2q1rk1/pbpn1ppp/1p1p1n2/4N3/2PP4/6P1/PPQNPPBP/R3R1K1 b - - 0 11
r2q1rk1/p1pn1ppp/1p1p1n2/4N3/2PP4/6P1/PPQNPPbP/R3R1K1 w - - 0 12
r2q1rk1/p1pN1ppp/1p1p1n2/8/2PP4/6P1/PPQNPPbP/R3R1K1 b - - 0 12
r2q1rk1/p1pN1ppp/1p1p1n2/8/2PP4/6Pb/PPQNPP1P/R3R1K1 w - - 1 13
r2q1Nk1/p1p2ppp/1p1p1n2/8/2PP4/6Pb/PPQNPP1P/R3R1K1 b - - 0 13
</pre>

Each line of the FEN corresponds to one position/state of the chess game. The first line is the initial position. Lower case letters are black pieces, upper case letters are white pieces. An integer indicates consecutive empty squares on the board. Each board rank is separated by the "/" character.

Each FEN  line has exactly 6 comma-separated fields. The first is the board position. The second is the color of the player ('w" or "b") to move next. The third field, like "KQkq" is a code for castling privileges. A "K" means white has not lost the privilege to castle kingside (for example, if the white king has moved, or already castled to either side). The letter code does not mean that white can castle in the position, it just means that white has not lost kingside castling privileges. The other letters are for white queenside, black kingside, and black queenside privileges.

The fourth field, usually a "-", is a potential en passant capture square. This occurs only when the last move was a two-square pawn move to the fourth rank by white, or a two-square pawn move by black to the fifth rank. For example, if the last move was e4 (from e2) by white then the e3 square is a potential en passant capture square. If the last move was b5 (from b7) by black, the b6 square is a possible e.p. capture square. The code does not check if an e.p. capture is possible. Notice that all possible re.p. capture squares will end with "3" or "6".

The fifth field is "halfmove clock", or the fifty-move-rule counter. It is the number of half-moves since a pawn was moved or a piece captures, by either color. In chess, if 50 such moves have been made consecutively, either color may claim a draw.

The sixth field is the "fullmove number". It starts at 1 and is incremented after a black move.

If you think about it, an FEN string gives players all the information they need to restart a game. In the old days, when chess games were crazy long, it was common to adjourn a game and then resume the game the next day. A simple FEN string has all the information to restart.

I found a nice JavaScript implementation of PGN to FEN at https://www.chess-poster.com/english/lt_pgn_to_fen/lt_pgn_fen.htm but it didn't meet my needs because 1.) you need to manually paste PGN text into a Web browser window, 2.) it's written in JavaScript, not Python, and 3.) the tool is on a personal Web site rather than someplace like GitHub and so it might/probably go away in the future.

So I set out to write my own PGN to FEN conversion tool. I have a preliminary version running. The calling code looks like:

<pre>
  source_pgn = ".\\Data\\euwe_colle_karlsbad_1929.pgn"
  dest_fen = ".\\Data\\euwe_colle_karlsbad_1929.fen"
  print("Converting file " + source_pgn + " to FEN strings ")
  ChessFunctions.file_pgn_to_file_fen(source_pgn, dest_fen)
  print("Done ")
</pre>

One of the side effects of years of experience of writing software is that it's usually possible to make a reasonable estimate of how much time and effort is going to be required for a project. I knew going in this was not going to be a simple project. I mentally estimated that writing a PGN to FEN conversion tool would take approximately 80 hours of effort, and as I write this blog post, my estimate is right on track so far.

The Wikipedia entries on PGN and FEN are quite good:
https://en.wikipedia.org/wiki/Portable_Game_Notation
https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation

The FEN format is so simple there is no specification document. The PGN specification is at:
http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm
