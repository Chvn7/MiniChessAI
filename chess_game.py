import pygame
import chess

from constants import WIDTH, HEIGHT, SQUARE_SIZE, COLORS
from engine import get_mini_moves


class MiniChessGame:
    def __init__(self):
        self.board = chess.Board("8/8/8/rnbqk3/ppppp3/8/PPPPP3/RNBQK3 w - - 0 1")
        self.selected_square = None
        self.promoting_move = None 
        
        piece_map = {
            'P': 'plt60', 'N': 'nlt60', 'B': 'blt60', 'R': 'rlt60', 'Q': 'qlt60', 'K': 'klt60',
            'p': 'pdt60', 'n': 'ndt60', 'b': 'bdt60', 'r': 'rdt60', 'q': 'qdt60', 'k': 'kdt60'
        }
        
        self.images = {}
        for symbol, file_part in piece_map.items():
            path = f"assets/images/pieces/Chess_{file_part}.png"
            img = pygame.image.load(path)
            self.images[symbol] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))

        pygame.mixer.init()
        self.move_sound = pygame.mixer.Sound("assets/sound/bob_sound.wav")

    def draw(self, screen):
        for r in range(5):
            for c in range(5):
                sq = chess.square(c, 4-r)
                color = COLORS[(r + c) % 2]
                if self.selected_square == sq:
                    color = pygame.Color(186, 202, 68) 
                pygame.draw.rect(screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
                piece = self.board.piece_at(sq)
                if piece:
                    screen.blit(self.images[piece.symbol()], (c * SQUARE_SIZE, r * SQUARE_SIZE))

        # draw coordinates
        font = pygame.font.SysFont("Arial", 28, bold=True)
        for r in range(5):
            num = str(5 - r)
            text = font.render(num, True, (0, 0, 0))
            screen.blit(text, (5, r * SQUARE_SIZE + 5))
        for c in range(5):
            letter = chr(ord('a') + c)
            text = font.render(letter, True, (0, 0, 0))
            screen.blit(text, (c * SQUARE_SIZE + SQUARE_SIZE - 24, HEIGHT - 30))

        if self.selected_square is not None:
            for move in get_mini_moves(self.board):
                if move.from_square == self.selected_square:
                    to_c = chess.square_file(move.to_square)
                    to_r = 4 - chess.square_rank(move.to_square)
                    center = (to_c * SQUARE_SIZE + SQUARE_SIZE // 2, to_r * SQUARE_SIZE + SQUARE_SIZE // 2)
                    # highlight possible moves with a golden circle
                    pygame.draw.circle(screen, (255, 215, 0, 150), center, 12)

    def draw_promotion_popup(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont("Arial", 45, bold=True)
        q_rect = pygame.Rect(WIDTH//4 - 75, HEIGHT//2 - 50, 200, 100)
        n_rect = pygame.Rect(WIDTH//2 + 25, HEIGHT//2 - 50, 200, 100)
        
        pygame.draw.rect(screen, (240, 240, 240), q_rect, border_radius=10)
        pygame.draw.rect(screen, (240, 240, 240), n_rect, border_radius=10)
        
        screen.blit(font.render("QUEEN", True, (20, 20, 20)), (q_rect.x + 30, q_rect.y + 25))
        screen.blit(font.render("KNIGHT", True, (20, 20, 20)), (n_rect.x + 25, n_rect.y + 25))
        
        return q_rect, n_rect
