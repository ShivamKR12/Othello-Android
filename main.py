# main.py
"""
IMPROVEMENTS TO BE MADE: 

1. [FIXED] Add a confirmation dialog asking if the player is sure they want to reset the board, to prevent misclick resets. 
2. [FIXED] Run a simulation on this exact code to find in which scenarios exactly the game is getting stuck at the very last move of the game, where neither the player nor the computer can make the next move !?
3. [FIXED] Move the hud_str to the center at the top center of the screen, slightly below the very top of the screen, so it does not get's covered by the camera notches or top screen info tray.
"""

from game import Othello

def main():
    game = Othello()
    game.run()

if __name__ == '__main__':
    main()
