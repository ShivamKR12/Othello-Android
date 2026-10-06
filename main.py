# main.py

"""
IMPROVEMENTS TO BE MADE: 

1. Add a confirmation dialog asking if the player is sure they want to reset the board, to prevent misclick resets. 
2. Run a simulation on this exact code to find in which scenarios exactly the game is getting stuck at the very last move of the game, where neither the player nor the computer can make the next move !?
3. Move the hud_str to the center at the top center of the screen, slightly below the very top of the screen, so it does not get's covered by the camera notches or top screen info tray.
"""

import random
import sys
import copy
import os
import pygame
from pygame.locals import *

# Constant Settings
FPS = 30
SPACESIZE = 50
BOARDWIDTH = 8
BOARDHEIGHT = 8

# Tile Constants
WHITE_TILE = 'WHITE_TILE'
BLACK_TILE = 'BLACK_TILE'
EMPTY_SPACE = 'EMPTY_SPACE'
HINT_TILE = 'HINT_TILE'

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
BRIGHTBLUE = (0, 50, 255)
BROWN = (174, 94, 0)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller/Buildozer packages."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, "assets", relative_path)


class Othello:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        
        # Enable Resizable Window (suitable for desktop testing and mobile orientations)
        self.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        self.width, self.height = self.screen.get_size()
            
        # Boosted base UI font size for mobile high-DPI clarity
        self.font = pygame.font.Font('freesansbold.ttf', 24)
        self.large_font = pygame.font.Font('freesansbold.ttf', 36)
        
        self.load_assets()
        
        # Virtual UI Buttons state map
        self.ui_buttons = {}
        
        # Game State Variables
        self.main_board = self.get_new_board()
        self.reset_board(self.main_board)
        self.show_hints = False
        self.player_tile = None
        self.computer_tile = None
        self.turn = None
        self.consecutive_passes = 0
        self.game_over = False
        
        # Start game setup flow
        self.selecting_color = True

    def load_assets(self):
        def safe_load(path, size, color):
            try:
                return pygame.image.load(resource_path(path)).convert_alpha()
            except Exception:
                surf = pygame.Surface(size)
                surf.fill(color)
                return surf

        self.board_image = safe_load('flippyboard.png', (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE), GREEN)

    def get_new_board(self):
        return [[EMPTY_SPACE] * BOARDHEIGHT for _ in range(BOARDWIDTH)]

    def reset_board(self, board):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                board[x][y] = EMPTY_SPACE
        board[3][3] = WHITE_TILE
        board[3][4] = BLACK_TILE
        board[4][3] = BLACK_TILE
        board[4][4] = WHITE_TILE

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_AC_BACK):
                self.terminate()
                
            elif event.type == VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

            # Handle mouse input releases
            elif event.type == MOUSEBUTTONUP:
                if getattr(event, 'touch', False):
                    continue
                self.process_interaction_at_pos(event.pos)

            # Handle explicit mobile touch finger inputs directly
            elif event.type == FINGERUP:
                px_x = int(event.x * self.width)
                px_y = int(event.y * self.height)
                self.process_interaction_at_pos((px_x, px_y))

    def process_interaction_at_pos(self, pos):
        if self.check_ui_clicks(pos):
            return

        if self.selecting_color or self.game_over:
            return

        if self.turn == 'player':
            board_coord = self.get_space_clicked(pos)
            if board_coord:
                x, y = board_coord
                if self.is_valid_move(self.main_board, self.player_tile, x, y):
                    print(f"[MOVE] Player placed tile at coordinates: ({x}, {y})")
                    self.make_move(self.main_board, self.player_tile, x, y)
                    self.turn = 'computer'
                else:
                    print(f"[REJECTED] Player tried to tap ({x}, {y}), but it flips 0 pieces!")

    def check_ui_clicks(self, pos):
        # Color Setup Screen Interfaces
        if self.selecting_color:
            for choice, rect in self.ui_buttons.items():
                if rect.collidepoint(pos):
                    if choice == 'WHITE':
                        self.player_tile, self.computer_tile = WHITE_TILE, BLACK_TILE
                    else:
                        self.player_tile, self.computer_tile = BLACK_TILE, WHITE_TILE
                    self.selecting_color = False
                    self.turn = random.choice(['computer', 'player'])
                    return True
            return False

        # End Game Play Again Overlays
        if self.game_over:
            for choice, rect in self.ui_buttons.items():
                if rect.collidepoint(pos):
                    if choice == 'YES':
                        self.__init__() 
                    elif choice == 'NO':
                        self.terminate()
                    return True
            return False

        # Active In-Game Core HUD Interfaces
        for label, rect in self.ui_buttons.items():
            if rect.collidepoint(pos):
                if label == "RESET":
                    self.reset_board(self.main_board)
                    self.turn = random.choice(['computer', 'player'])
                    self.game_over = False
                    self.consecutive_passes = 0
                elif label == "HINTS":
                    self.show_hints = not self.show_hints
                return True
        return False

    def get_space_clicked(self, mouse_pos):
        is_portrait = self.height > self.width
        
        # Unified tracking properties to match draw coordinates calculation transforms
        if is_portrait:
            avail_w = self.width - 20
            avail_h = int(self.height * 0.65)
            map_center = (self.width // 2, self.height // 2 - 40)
        else:
            avail_w = int(self.width * 0.55)
            avail_h = self.height - 40
            map_center = (self.width // 2, self.height // 2)

        map_w, map_h = BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE
        scale = min(avail_w / map_w, avail_h / map_h)
        
        new_w = int(map_w * scale)
        new_h = int(map_h * scale)
        
        topleft_x = map_center[0] - new_w // 2
        topleft_y = map_center[1] - new_h // 2

        mx, my = mouse_pos
        x = int((mx - topleft_x) // (SPACESIZE * scale))
        y = int((my - topleft_y) // (SPACESIZE * scale))

        if 0 <= x < BOARDWIDTH and 0 <= y < BOARDHEIGHT:
            return (x, y)
        return None

    def update(self):
        if self.selecting_color or self.game_over:
            return

        player_moves = self.get_valid_moves(self.main_board, self.player_tile)
        comp_moves = self.get_valid_moves(self.main_board, self.computer_tile)

        empty_squares = sum(row.count(EMPTY_SPACE) for row in self.main_board)

        if not player_moves and not comp_moves:
            print(f"[GAME OVER] No legal moves left for either entity. Empty spaces remaining: {empty_squares}")
            self.game_over = True
            return

        if self.turn == 'computer' and not self.game_over:
            if comp_moves:
                pygame.time.wait(600) 
                x, y = random.choice(comp_moves)
                print(f"[MOVE] Computer placed tile at coordinates: ({x}, {y}) | Options available: {len(comp_moves)}")
                self.make_move(self.main_board, self.computer_tile, x, y)
                self.turn = 'player'
            else:
                print(f"[PASS] Computer has NO legal moves at ({empty_squares} empty squares left). Forcing Pass to Player.")
                self.turn = 'player'

    def draw(self):
        self.screen.fill(BLACK)
        is_portrait = self.height > self.width
        self.ui_buttons.clear()

        # Build Common Surface Board Base Environment
        board_surf = pygame.Surface((BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
        board_surf.blit(pygame.transform.scale(self.board_image, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE)), (0,0))
        
        if self.selecting_color:
            self.render_board_tiles(board_surf, self.main_board)
        else:
            board_to_render = self.main_board
            if self.turn == 'player' and self.show_hints:
                board_to_render = self.get_board_with_valid_moves(self.main_board, self.player_tile)
            self.render_board_tiles(board_surf, board_to_render)

        # Scale and position board surface area centered onto screen dynamically
        if is_portrait:
            avail_w = self.width - 20
            avail_h = int(self.height * 0.65) # Takes more center room area allocation
            map_center = (self.width // 2, self.height // 2 - 40) # Absolute structural vertical/horizontal center offset
        else:
            avail_w = int(self.width * 0.55)
            avail_h = self.height - 40
            map_center = (self.width // 2, self.height // 2)

        map_w, map_h = board_surf.get_size()
        scale = min(avail_w / map_w, avail_h / map_h)
        new_w, new_h = int(map_w * scale), int(map_h * scale)
        
        scaled_board = pygame.transform.smoothscale(board_surf, (new_w, new_h))
        board_rect = scaled_board.get_rect(center=map_center)
        self.screen.blit(scaled_board, board_rect)

        # Draw Contextual Overlays or Main Interface HUD Elements
        if self.selecting_color:
            self.draw_color_selection_overlay(map_center)
        else:
            self.draw_ui(is_portrait, board_rect)
            if self.game_over:
                self.draw_game_over_overlay(map_center)

        pygame.display.update()

    def render_board_tiles(self, surf, board):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                cx = x * SPACESIZE + SPACESIZE // 2
                cy = y * SPACESIZE + SPACESIZE // 2
                if board[x][y] == WHITE_TILE:
                    pygame.draw.circle(surf, WHITE, (cx, cy), SPACESIZE // 2 - 4)
                elif board[x][y] == BLACK_TILE:
                    pygame.draw.circle(surf, BLACK, (cx, cy), SPACESIZE // 2 - 4)
                elif board[x][y] == HINT_TILE:
                    pygame.draw.rect(surf, BROWN, (cx - 4, cy - 4, 8, 8))
                
                pygame.draw.rect(surf, BLACK, (x*SPACESIZE, y*SPACESIZE, SPACESIZE, SPACESIZE), 1)

    def draw_btn(self, label, cx, cy, w, h, target_dict, font):
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (cx, cy)
        target_dict[label] = rect

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (30, 30, 30, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (100, 100, 100, 220), surf.get_rect().inflate(-4, -4), border_radius=10)

        lbl_surf = font.render(label, True, WHITE)
        lbl_rect = lbl_surf.get_rect(center=(w//2, h//2))
        surf.blit(lbl_surf, lbl_rect)
        self.screen.blit(surf, rect.topleft)

    def draw_ui(self, is_portrait, board_rect):
        scores = self.get_score_of_board(self.main_board)
        hud_str = f"Player: {scores[self.player_tile]} | Computer: {scores[self.computer_tile]} | Turn: {str(self.turn).capitalize()}"
        hud_surf = self.font.render(hud_str, True, WHITE)
        self.screen.blit(hud_surf, (20, 20))

        if is_portrait:
            # Massive oversized button configurations optimized for clear thumb targets
            btn_w, btn_h = 170, 95
            
            # Position the buttons safely below the bottom edge of the board with a 25px gap
            bottom_cy = board_rect.bottom + 100 + (btn_h // 2)
            
            # Fallback check: If it still runs off the screen, clamp it to the safe bottom window zone
            if bottom_cy + (btn_h // 2) > self.height:
                bottom_cy = self.height - (btn_h // 2) - 15
            
            util_cx = self.width // 2
            self.draw_btn('RESET', util_cx - 100, bottom_cy, btn_w, btn_h, self.ui_buttons, self.font)
            self.draw_btn('HINTS', util_cx + 100, bottom_cy, btn_w, btn_h, self.ui_buttons, self.font)
        else:
            btn_w, btn_h = 140, 90
            util_cx = self.width * 0.12
            start_y = self.height // 2 - 60
            self.draw_btn('RESET', util_cx, start_y, btn_w, btn_h, self.ui_buttons, self.font)
            self.draw_btn('HINTS', util_cx, start_y + 120, btn_w, btn_h, self.ui_buttons, self.font)

    def draw_color_selection_overlay(self, map_center):
        card_w, card_h = 550, 320
        overlay = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        
        pygame.draw.rect(overlay, (15, 15, 15, 230), overlay.get_rect(), border_radius=20)
        
        title_surf = self.large_font.render('Choose Your Color', True, WHITE)
        title_rect = title_surf.get_rect(center=(card_w // 2, 60)) # Centered inside the card
        overlay.blit(title_surf, title_rect)
        
        self.screen.blit(overlay, overlay.get_rect(center=map_center))
        
        btn_w, btn_h = 180, 95
        side_offset = 120
        vertical_offset = 50
        
        self.draw_btn('WHITE', map_center[0] - side_offset, map_center[1] + vertical_offset, btn_w, btn_h, self.ui_buttons, self.font)
        self.draw_btn('BLACK', map_center[0] + side_offset, map_center[1] + vertical_offset, btn_w, btn_h, self.ui_buttons, self.font)


    def draw_game_over_overlay(self, map_center):
        scores = self.get_score_of_board(self.main_board)
        p_score = scores[self.player_tile]
        c_score = scores[self.computer_tile]
        
        if p_score > c_score:
            msg = f"You won by {p_score - c_score} points!"
        elif c_score > p_score:
            msg = f"Computer won by {c_score - p_score} points."
        else:
            msg = "Tie game matching outcome!"

        overlay = pygame.Surface((440, 280), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (20, 20, 20, 230), overlay.get_rect(), border_radius=15)
        
        m_surf = self.font.render(msg, True, WHITE)
        m_rect = m_surf.get_rect(center=(220, 40))
        overlay.blit(m_surf, m_rect)

        prompt_surf = self.large_font.render("Play Again?", True, WHITE)
        prompt_rect = prompt_surf.get_rect(center=(220, 110))
        overlay.blit(prompt_surf, prompt_rect)
        
        self.screen.blit(overlay, overlay.get_rect(center=map_center))
        
        # Scaled up confirmation interfaces
        self.draw_btn('YES', map_center[0] - 90, map_center[1] + 70, 130, 65, self.ui_buttons, self.font)
        self.draw_btn('NO', map_center[0] + 90, map_center[1] + 70, 130, 65, self.ui_buttons, self.font)

    # Core Ruleset Logic
    def get_score_of_board(self, board):
        w_score, b_score = 0, 0
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if board[x][y] == WHITE_TILE: w_score += 1
                elif board[x][y] == BLACK_TILE: b_score += 1
        return {WHITE_TILE: w_score, BLACK_TILE: b_score}

    def make_move(self, board, tile, xstart, ystart):
        tiles_to_flip = self.is_valid_move(board, tile, xstart, ystart)
        if not tiles_to_flip:
            return False
        board[xstart][ystart] = tile
        for x, y in tiles_to_flip:
            board[x][y] = tile
        return True

    def is_valid_move(self, board, tile, xstart, ystart):
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

    def get_valid_moves(self, board, tile):
        moves = []
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if self.is_valid_move(board, tile, x, y):
                    moves.append((x, y))
        return moves

    def get_board_with_valid_moves(self, board, tile):
        dupe = copy.deepcopy(board)
        for x, y in self.get_valid_moves(dupe, tile):
            dupe[x][y] = HINT_TILE
        return dupe

    def terminate(self):
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Othello()
    game.run()
