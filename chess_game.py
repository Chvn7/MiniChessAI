import pygame
import chess

from constants import (width, height, square_size, colors, board_size,
                       selected_color, move_highlight_color, coord_color,
                       popup_bg, popup_text, popup_overlay, piece_map)
from engine import get_mini_moves


GARDNER_FEN = "8/8/8/rnbqk3/ppppp3/8/PPPPP3/RNBQK3 w - - 0 1"


class MiniChessGame:
    def __init__(self, FEN=None):
        if FEN is None:
            self.board = chess.Board(GARDNER_FEN)
        else:
            self.board = chess.Board(FEN)
        self.selected_square = None
        self.promoting_move = None 
        
        self.images = {}
        for symbol, file_part in piece_map.items():
            path = f"assets/images/pieces/Chess_{file_part}.png"
            img = pygame.image.load(path)
            self.images[symbol] = pygame.transform.scale(img, (square_size, square_size))

        pygame.mixer.init()
        self.move_sound = pygame.mixer.Sound("assets/sound/bob_sound.wav")

    def draw(self, screen):
        for r in range(board_size):
            for c in range(board_size):
                sq = chess.square(c, 4-r)
                color = colors[(r + c) % 2]
                if self.selected_square == sq:
                    color = selected_color
                pygame.draw.rect(screen, color, (c * square_size, r * square_size, square_size, square_size))
                
                piece = self.board.piece_at(sq)
                if piece:
                    screen.blit(self.images[piece.symbol()], (c * square_size, r * square_size))

        # draw coordinates
        font = pygame.font.SysFont("Arial", 28, bold=True)
        for r in range(board_size):
            num = str(board_size - r)
            text = font.render(num, True, coord_color)
            screen.blit(text, (5, r * square_size + 5))
        for c in range(board_size):
            letter = chr(ord('a') + c)
            text = font.render(letter, True, coord_color)
            screen.blit(text, (c * square_size + square_size - 24, height - 30))

        if self.selected_square is not None:
            for move in get_mini_moves(self.board):
                if move.from_square == self.selected_square:
                    to_c = chess.square_file(move.to_square)
                    to_r = 4 - chess.square_rank(move.to_square)
                    center = (to_c * square_size + square_size // 2, to_r * square_size + square_size // 2)
                    pygame.draw.circle(screen, move_highlight_color, center, 12)

    def draw_promotion_popup(self, screen):
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(popup_overlay)
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont("Arial", 45, bold=True)
        q_rect = pygame.Rect(width//4 - 75, height//2 - 50, 200, 100)
        n_rect = pygame.Rect(width//2 + 25, height//2 - 50, 200, 100)
        
        pygame.draw.rect(screen, popup_bg, q_rect, border_radius=10)
        pygame.draw.rect(screen, popup_bg, n_rect, border_radius=10)
        
        screen.blit(font.render("QUEEN", True, popup_text), (q_rect.x + 30, q_rect.y + 25))
        screen.blit(font.render("KNIGHT", True, popup_text), (n_rect.x + 25, n_rect.y + 25))
        
        return q_rect, n_rect
