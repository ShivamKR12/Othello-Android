import pygame
from settings import WHITE, BOARDWIDTH, BOARDHEIGHT, SPACESIZE, WHITE_TILE, BLACK_TILE, HINT_TILE, BROWN, BLACK
from board import get_score_of_board

def draw_btn(surface, label, cx, cy, w, h, target_dict, font, display_text=None):
    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)
    target_dict[label] = rect

    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (30, 30, 30, 220), surf.get_rect(), border_radius=12)
    pygame.draw.rect(surf, (100, 100, 100, 220), surf.get_rect().inflate(-4, -4), border_radius=10)

    text_to_show = display_text if display_text is not None else label
    lbl_surf = font.render(text_to_show, True, WHITE)
    lbl_rect = lbl_surf.get_rect(center=(w // 2, h // 2))
    surf.blit(lbl_surf, lbl_rect)
    surface.blit(surf, rect.topleft)

def render_board_tiles(surf, board):
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
            pygame.draw.rect(surf, BLACK, (x * SPACESIZE, y * SPACESIZE, SPACESIZE, SPACESIZE), 1)

def draw_color_selection_overlay(screen, map_center, ui_buttons, font, large_font):
    card_w, card_h = 550, 320
    overlay = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (15, 15, 15, 230), overlay.get_rect(), border_radius=20)
    
    title_surf = large_font.render('Choose Your Color', True, WHITE)
    title_rect = title_surf.get_rect(center=(card_w // 2, 60))
    overlay.blit(title_surf, title_rect)
    
    screen.blit(overlay, overlay.get_rect(center=map_center))
    
    btn_w, btn_h = 180, 95
    side_offset = 120
    vertical_offset = 50
    
    draw_btn(screen, 'WHITE', map_center[0] - side_offset, map_center[1] + vertical_offset, btn_w, btn_h, ui_buttons, font)
    draw_btn(screen, 'BLACK', map_center[0] + side_offset, map_center[1] + vertical_offset, btn_w, btn_h, ui_buttons, font)

def draw_reset_confirmation_overlay(screen, map_center, ui_buttons, font, large_font):
    card_w, card_h = 550, 320
    overlay = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (15, 15, 15, 230), overlay.get_rect(), border_radius=20)
    
    title_surf = large_font.render('Reset Board?', True, WHITE)
    title_rect = title_surf.get_rect(center=(card_w // 2, 60))
    overlay.blit(title_surf, title_rect)
    
    screen.blit(overlay, overlay.get_rect(center=map_center))
    
    btn_w, btn_h = 180, 95
    side_offset = 120
    vertical_offset = 50
    draw_btn(screen, 'CONFIRM_YES', map_center[0] - side_offset, map_center[1] + vertical_offset, btn_w, btn_h, ui_buttons, font, display_text='YES')
    draw_btn(screen, 'CONFIRM_NO', map_center[0] + side_offset, map_center[1] + vertical_offset, btn_w, btn_h, ui_buttons, font, display_text='NO')

def draw_game_over_overlay(screen, map_center, main_board, player_tile, computer_tile, ui_buttons, font, large_font):
    scores = get_score_of_board(main_board)
    p_score = scores.get(player_tile, 0)
    c_score = scores.get(computer_tile, 0)
    
    if p_score > c_score:
        msg = f"You won by {p_score - c_score} points!"
    elif c_score > p_score:
        msg = f"Computer won by {c_score - p_score} points."
    else:
        msg = "Tie game matching outcome!"

    overlay = pygame.Surface((440, 280), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (20, 20, 20, 230), overlay.get_rect(), border_radius=15)
    
    m_surf = font.render(msg, True, WHITE)
    m_rect = m_surf.get_rect(center=(220, 40))
    overlay.blit(m_surf, m_rect)

    prompt_surf = large_font.render("Play Again?", True, WHITE)
    prompt_rect = prompt_surf.get_rect(center=(220, 110))
    overlay.blit(prompt_surf, prompt_rect)
    
    screen.blit(overlay, overlay.get_rect(center=map_center))
    
    draw_btn(screen, 'GAME_OVER_YES', map_center[0] - 90, map_center[1] + 70, 130, 65, ui_buttons, font, display_text='YES')
    draw_btn(screen, 'GAME_OVER_NO', map_center[0] + 90, map_center[1] + 70, 130, 65, ui_buttons, font, display_text='NO')
