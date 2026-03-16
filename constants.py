import pygame

# layout
width, height = 900, 900
square_size = width // 5
board_size = 5

# board colors
colors = [pygame.Color(235, 235, 208), pygame.Color(119, 148, 85)]
light_square = (235, 235, 208)
dark_square = (119, 148, 85)
selected_color = pygame.Color(186, 202, 68)
move_highlight_color = (255, 215, 0, 150)
coord_color = (0, 0, 0)

# UI colors
bg_color = (30, 30, 30)
game_bg_color = (0, 0, 0)
white_text = (255, 255, 255)
subtitle_text = (180, 180, 180)
hint_text = (140, 140, 140)
error_text = (255, 80, 80)
check_text = (255, 0, 0)
overlay_color = (0, 0, 0, 180)

# button colors
btn_default = (60, 60, 60)
btn_hover = (80, 160, 80)
btn_border = (200, 200, 200)
btn_dark = (50, 50, 50)
btn_clear = (100, 100, 100)
btn_play = (40, 140, 40)
btn_remove = (120, 20, 20)
btn_remove_active = (200, 30, 30)
btn_palette = (55, 55, 55)
btn_palette_sel = (80, 160, 80)
palette_border = (180, 180, 180)

# promotion popup
popup_bg = (240, 240, 240)
popup_text = (20, 20, 20)
popup_overlay = (0, 0, 0, 160)

# custom editor palette
palette_w = 80
palette_gap = 6
piece_symbols = ['K', 'Q', 'R', 'B', 'N', 'P',
                 'k', 'q', 'r', 'b', 'n', 'p']

# piece image mapping
piece_map = {
    'P': 'plt60', 'N': 'nlt60', 'B': 'blt60', 'R': 'rlt60', 'Q': 'qlt60', 'K': 'klt60',
    'p': 'pdt60', 'n': 'ndt60', 'b': 'bdt60', 'r': 'rdt60', 'q': 'qdt60', 'k': 'kdt60',
}

# AI
ai_delay_ms = 500
