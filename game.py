import random
import sys
import pygame
from pygame.locals import *

from settings import (
    FPS, SPACESIZE, BOARDWIDTH, BOARDHEIGHT,
    WHITE_TILE, BLACK_TILE, EMPTY_SPACE,
    WHITE, BLACK, GREEN, resource_path
)
from board import (
    get_new_board, reset_board, get_score_of_board,
    is_valid_move, make_move, get_valid_moves, get_board_with_valid_moves
)
from ui import (
    draw_btn, render_board_tiles, draw_color_selection_overlay,
    draw_reset_confirmation_overlay, draw_game_over_overlay
)

class Othello:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        
        self.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        self.width, self.height = self.screen.get_size()
            
        self.font = pygame.font.Font('freesansbold.ttf', 24)
        self.large_font = pygame.font.Font('freesansbold.ttf', 36)
        
        self.load_assets()
        
        self.ui_buttons = {}
        
        # Game State Variables
        self.main_board = get_new_board()
        reset_board(self.main_board)
        self.show_hints = False
        self.player_tile = None
        self.computer_tile = None
        self.turn = None
        self.consecutive_passes = 0
        self.game_over = False
        self.awaiting_reset_confirmation = False
        
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

            elif event.type == MOUSEBUTTONUP:
                if getattr(event, 'touch', False):
                    continue
                self.process_interaction_at_pos(event.pos)

            elif event.type == FINGERUP:
                px_x = int(event.x * self.width)
                px_y = int(event.y * self.height)
                self.process_interaction_at_pos((px_x, px_y))

    def process_interaction_at_pos(self, pos):
        if self.check_ui_clicks(pos):
            return

        if self.selecting_color or self.game_over or getattr(self, 'awaiting_reset_confirmation', False):
            return

        if self.turn == 'player':
            board_coord = self.get_space_clicked(pos)
            if board_coord:
                x, y = board_coord
                if is_valid_move(self.main_board, self.player_tile, x, y):
                    print(f"[MOVE] Player placed tile at coordinates: ({x}, {y})")
                    make_move(self.main_board, self.player_tile, x, y)
                    self.turn = 'computer'
                else:
                    print(f"[REJECTED] Player tried to tap ({x}, {y}), but it flips 0 pieces!")

    def check_ui_clicks(self, pos):
        # Reset Confirmation Screen Interfaces
        if getattr(self, 'awaiting_reset_confirmation', False):
            for choice, rect in self.ui_buttons.items():
                if rect.collidepoint(pos):
                    if choice == 'CONFIRM_YES':
                        reset_board(self.main_board)
                        self.turn = random.choice(['computer', 'player'])
                        self.game_over = False
                        self.consecutive_passes = 0
                        self.awaiting_reset_confirmation = False
                    elif choice == 'CONFIRM_NO':
                        self.awaiting_reset_confirmation = False
                    return True
            return False

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
                    if choice == 'GAME_OVER_YES':
                        self.__init__() 
                    elif choice == 'GAME_OVER_NO':
                        self.terminate()
                    return True
            return False

        # Active In-Game Core HUD Interfaces
        for label, rect in self.ui_buttons.items():
            if rect.collidepoint(pos):
                if label == "RESET":
                    self.awaiting_reset_confirmation = True
                elif label == "HINTS":
                    self.show_hints = not self.show_hints
                return True
        return False

    def get_space_clicked(self, mouse_pos):
        is_portrait = self.height > self.width
        
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
        if self.selecting_color or self.game_over or getattr(self, 'awaiting_reset_confirmation', False):
            return

        player_moves = get_valid_moves(self.main_board, self.player_tile)
        comp_moves = get_valid_moves(self.main_board, self.computer_tile)

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
                make_move(self.main_board, self.computer_tile, x, y)
                self.turn = 'player'
            else:
                print(f"[PASS] Computer has NO legal moves at ({empty_squares} empty squares left). Forcing Pass to Player.")
                self.turn = 'player'
        elif self.turn == 'player' and not self.game_over:
            if not player_moves:
                print(f"[PASS] Player has NO legal moves at ({empty_squares} empty squares left). Forcing Pass to Computer.")
                pygame.time.wait(600)
                self.turn = 'computer'

    def draw(self):
        self.screen.fill(BLACK)
        is_portrait = self.height > self.width
        self.ui_buttons.clear()

        # Build Common Surface Board Base Environment
        board_surf = pygame.Surface((BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
        board_surf.blit(pygame.transform.scale(self.board_image, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE)), (0,0))
        
        if self.selecting_color:
            render_board_tiles(board_surf, self.main_board)
        else:
            board_to_render = self.main_board
            if self.turn == 'player' and self.show_hints:
                board_to_render = get_board_with_valid_moves(self.main_board, self.player_tile)
            render_board_tiles(board_surf, board_to_render)

        if is_portrait:
            avail_w = self.width - 20
            avail_h = int(self.height * 0.65)
            map_center = (self.width // 2, self.height // 2 - 40)
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

        if self.selecting_color:
            draw_color_selection_overlay(self.screen, map_center, self.ui_buttons, self.font, self.large_font)
        else:
            self.draw_ui(is_portrait, board_rect)
            if getattr(self, 'awaiting_reset_confirmation', False):
                draw_reset_confirmation_overlay(self.screen, map_center, self.ui_buttons, self.font, self.large_font)
            elif self.game_over:
                draw_game_over_overlay(
                    self.screen, map_center, self.main_board,
                    self.player_tile, self.computer_tile,
                    self.ui_buttons, self.font, self.large_font
                )

        pygame.display.update()

    def draw_ui(self, is_portrait, board_rect):
        scores = get_score_of_board(self.main_board)
        hud_str = f"Player: {scores.get(self.player_tile, 0)} | Computer: {scores.get(self.computer_tile, 0)} | Turn: {str(self.turn).capitalize()}"
        hud_surf = self.font.render(hud_str, True, WHITE)
        hud_rect = hud_surf.get_rect(midtop=(self.width // 2, 45))
        self.screen.blit(hud_surf, hud_rect)

        if is_portrait:
            btn_w, btn_h = 170, 95
            bottom_cy = board_rect.bottom + 100 + (btn_h // 2)
            
            if bottom_cy + (btn_h // 2) > self.height:
                bottom_cy = self.height - (btn_h // 2) - 15
            
            util_cx = self.width // 2
            draw_btn(self.screen, 'RESET', util_cx - 100, bottom_cy, btn_w, btn_h, self.ui_buttons, self.font)
            draw_btn(self.screen, 'HINTS', util_cx + 100, bottom_cy, btn_w, btn_h, self.ui_buttons, self.font)
        else:
            btn_w, btn_h = 140, 90
            util_cx = self.width * 0.12
            start_y = self.height // 2 - 60
            draw_btn(self.screen, 'RESET', util_cx, start_y, btn_w, btn_h, self.ui_buttons, self.font)
            draw_btn(self.screen, 'HINTS', util_cx, start_y + 120, btn_w, btn_h, self.ui_buttons, self.font)

    def terminate(self):
        pygame.quit()
        sys.exit()
