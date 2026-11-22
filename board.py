import copy
from settings import (
    BOARDWIDTH, BOARDHEIGHT,
    WHITE_TILE, BLACK_TILE, EMPTY_SPACE, HINT_TILE
)

def get_new_board():
    return [[EMPTY_SPACE] * BOARDHEIGHT for _ in range(BOARDWIDTH)]

def reset_board(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = EMPTY_SPACE
    board[3][3] = WHITE_TILE
    board[3][4] = BLACK_TILE
    board[4][3] = BLACK_TILE
    board[4][4] = WHITE_TILE

def get_score_of_board(board):
    w_score, b_score = 0, 0
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == WHITE_TILE: w_score += 1
            elif board[x][y] == BLACK_TILE: b_score += 1
    return {WHITE_TILE: w_score, BLACK_TILE: b_score}

def is_valid_move(board, tile, xstart, ystart):
    if board[xstart][ystart] != EMPTY_SPACE or not (0 <= xstart < BOARDWIDTH and 0 <= ystart < BOARDHEIGHT):
        return False
    
    board[xstart][ystart] = tile
    other_tile = BLACK_TILE if tile == WHITE_TILE else WHITE_TILE
    tiles_to_flip = []

    directions = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]
    for xdir, ydir in directions:
        x, y = xstart + xdir, ystart + ydir
        if 0 <= x < BOARDWIDTH and 0 <= y < BOARDHEIGHT and board[x][y] == other_tile:
            x += xdir
            y += ydir
            if not (0 <= x < BOARDWIDTH and 0 <= y < BOARDHEIGHT):
                continue
            while board[x][y] == other_tile:
                x += xdir
                y += ydir
                if not (0 <= x < BOARDWIDTH and 0 <= y < BOARDHEIGHT):
                    break
            if not (0 <= x < BOARDWIDTH and 0 <= y < BOARDHEIGHT):
                continue
            if board[x][y] == tile:
                while True:
                    x -= xdir
                    y -= ydir
                    if x == xstart and y == ystart:
                        break
                    tiles_to_flip.append([x, y])

    board[xstart][ystart] = EMPTY_SPACE
    return tiles_to_flip if len(tiles_to_flip) > 0 else False

def make_move(board, tile, xstart, ystart):
    tiles_to_flip = is_valid_move(board, tile, xstart, ystart)
    if not tiles_to_flip:
        return False
    board[xstart][ystart] = tile
    for x, y in tiles_to_flip:
        board[x][y] = tile
    return True

def get_valid_moves(board, tile):
    moves = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if is_valid_move(board, tile, x, y):
                moves.append((x, y))
    return moves

def get_board_with_valid_moves(board, tile):
    dupe = copy.deepcopy(board)
    for x, y in get_valid_moves(dupe, tile):
        dupe[x][y] = HINT_TILE
    return dupe
