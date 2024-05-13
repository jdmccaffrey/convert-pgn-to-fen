# convert-pgn-to-fen
Python language function to convert a chess file in PGN notation to a file of FEN strings

Here's a basic PGN file (saved as euwe_colle_karlsbad_1929.pgn):

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

Example calling code:

<pre>
  source_pgn = ".\\Data\\euwe_colle_karlsbad_1929.pgn"
  dest_fen = ".\\Data\\euwe_colle_karlsbad_1929.fen"
  print("Converting file " + source_pgn + " to FEN strings ")
  ChessFunctions.file_pgn_to_file_fen(source_pgn, dest_fen)
  print("Done ")
</pre>

The resulting euwe_colle_karlsbad_1929.fen file contains:

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

<br>
<img src="https://github.com/jdmccaffrey/convert-pgn-to-fen/blob/main/Images/converting_euwe_colle_from_pgn_to_fen.jpg" width="600">
<i>A screenshot of my PGN to FEN conversion tool, under development.</i>

<hr>
  
The Wikipedia entries on PGN and FEN are quite good:
https://en.wikipedia.org/wiki/Portable_Game_Notation
https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation

The FEN format is so simple there is no specification document. The PGN specification is at:
http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm

<hr>
