<b>Parsing a PGN Move</b>

A PGN file looks like:

<pre>
[Event "F/S Return Match"]
[Site "Belgrade, Serbia JUG"]
[Date "1992.11.04"]
[Round "29"]
[White "Fischer, Robert J."]
[Black "Spassky, Boris V."]
[Result "1/2-1/2"]

[Optional tag #1 xxx]
[Optional tag #2 yyy]

1. e4 e5 2. Nf3 Nc6 3. Bb5 {This opening is called the Ruy Lopez.} 3... a6
4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7
11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 16. Bh4 c5 17. dxe5
Nxe4 18. Bxe7 Qxe7 19. exd6 Qf6 20. Nbd2 Nxd6 21. Nc4 Nxc4 22. Bxc4 Nb6
23. Ne5 Rae8 24. Bxf7+ Rxf7 25. Nxf7 Rxe1+ 26. Qxe1 Kxf7 27. Qe3 Qg5 28. Qxg5
hxg5 29. b3 Ke6 30. a3 Kd6 31. axb4 cxb4 32. Ra5 Nd5 33. f3 Bc8 34. Kf2 Bf5
35. Ra7 g6 36. Ra6+ Kc5 37. Ke1 Nf4 38. g3 Nxh3 39. Kd2 Kb5 40. Rd6 Kc5 41. Ra6
Nf2 42. g4 Bd3 43. Re6 1/2-1/2
</pre>  

The tool API defines a single function file_pgn_to_file_fen(source_pgn_file, dest_fen_file) interface. The function begins by extracting the moves part of the file as one large string, which involves getting rid of embedded comments, to-end-of-line comments, and black move triple-dot syntax following a comment:

<pre>
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
</pre>

The moves part string of a PGN file now look likes "1. e4 e5 2. Nf3 Nf5 3. Bg5 a6" and so on. A single move can take a surprising number of forms. For piece (R, N, B, K, Q) moves:

<pre>
Nf3      basic piece move
N2f3     with rank hint
Nhf3     with file hint
Ng1f3    with full hint

Nxf3     basic capture move
N2xf3    capture with rank hint  
Nhxf3    capture with file hint
Ng1xf3   capture with full hint
</pre>

Now for each of these eight possibilities, there can be a "+" or "#" appended, such as Nf3+, giving a total of 24 possible patterns. To parse a piece move, I first strip away any trailing "+" or "#" if one is there. Somewhat surprisingly, this information is not needed to convert PGN to FEN.

Next, I check to see if the move contains an "x" character. If so, it is stripped away and the information is saved in a results.capture = true field.

Next, I check if the length of the move is 5. If so, the move must contain a full hint at indices [1] and [2]. The full hint information, like "g1" is stripped away and saved.

At this point the length of the move is either 3 or 4. If the length is 4, there must be a rank hint like "h" or a file hint like "2" at index [1]. If the hint is "a" through "h" it's a rank hint, if the hint is "1" through "8" it's a file hint. The hint is stripped away and saved.

At this point, the move has been reduced to length 3, like Nf3, with information like has_rank_hint = True and rank_hint = "h" saved. The reduced move has the piece that moved (in upper case form) at index [0] and the landing square in algebraic form at indexes [1] and [2]. Now the challenge is to determine where the piece came from. If the move has a full hint, then you know exactly where it came from, but otherwise, the logic is quite tricky.

Parsing a pawn move instead of a piece move uses different logic. Possible patterns are:

<pre>
e4       basic pawn move
exd5     regular or en passant capture
e8=Q     regular promotion
exf8=R   capture and promotion
</pre>

Each of these four patterns can have "+" or "#" appended, giving a total of 12 possible patterns. Note that in PGN, en passant captures are not explicitly indicated by "e.p." or something similar.

First, "+" or "#" are stripped away if there. Again, surprisingly, this information is not needed to convert PGN to FEN. After parsing a pawn move, the next step is to determine where the pawn came from. The tool considers eight cases:

<pre>
# 1. if color = w and results.capture = False and pawn promo = False
# 2. else if color = w and results.capture = False and pawn promo = True
# 3. else if color = w and results.capture = True and pawn promo = False
# 4. else if color = w and results.capture = True and pawn promo = True

# 5. else if color = b and results.capture = False and pawn promo = False
# 6. else if color = b and results.capture = False and pawn promo = True
# 7. else if color = b and results.capture = True and pawn promo = False
# 8. else if color = b and results.capture = True and pawn promo = True
</pre>
