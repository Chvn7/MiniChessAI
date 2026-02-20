import pygame
import chess
import sys

WIDTH, HEIGHT = 900, 900
SQUARE_SIZE = WIDTH // 5 
COLORS = [pygame.Color(235, 235, 208), pygame.Color(119, 148, 85)]

def get_mini_moves(board):
    legal_moves = []
    for move in board.legal_moves:
        f_from, r_from = chess.square_file(move.from_square), chess.square_rank(move.from_square)
        f_to, r_to = chess.square_file(move.to_square), chess.square_rank(move.to_square)
        if f_from < 5 and r_from < 5 and f_to < 5 and r_to < 5:
            legal_moves.append(move)
    return legal_moves

def evaluate_board(board, depth):
    if board.is_checkmate():
        # Using depth here forces the AI to prefer faster mates
        return -9999 + depth if board.turn == chess.WHITE else 9999 - depth
    
    values = {chess.PAWN: 10, chess.KNIGHT: 30, chess.BISHOP: 30, chess.ROOK: 50, chess.QUEEN: 90}
    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            val = values.get(piece.piece_type, 0)
            score += val if piece.color == chess.WHITE else -val
    return score

def minimax(board, depth, alpha, beta, maximizing):
    pygame.event.pump() 
    if depth == 0 or board.is_game_over():
        return evaluate_board(board, depth)

    valid_moves = get_mini_moves(board)
    if not valid_moves: 
        return evaluate_board(board, depth)

    if maximizing:
        max_eval = -float('inf')
        for move in valid_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return max_eval
    else:
        min_eval = float('inf')
        for move in valid_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha: break
        return min_eval

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gardner Minichess AI")
    game = MiniChessGame()
    clock = pygame.time.Clock()

    ai_thinking_start = None  
    AI_DELAY_MS = 500        

    # state for end-of-game and check notifications
    game_over = False
    game_over_msg = ""
    check_msg = ""
    restart_timer = None  # track when game ended to auto restart

    # undo button rectangle (top-right corner)
    undo_rect = pygame.Rect(WIDTH - 120, 10, 110, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            # restart if game ended
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                game = MiniChessGame()
                game_over = False
                game_over_msg = ""
                check_msg = ""
                ai_thinking_start = None
                restart_timer = None
                continue

            # undo handling (click or key)
            if not game_over and not game.promoting_move:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if undo_rect.collidepoint(mx, my):
                        if len(game.board.move_stack) >= 2:
                            game.board.pop(); game.board.pop()
                        elif len(game.board.move_stack) == 1:
                            game.board.pop()
                        game.selected_square = None
                        check_msg = ""
                        ai_thinking_start = None
                        continue
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    if len(game.board.move_stack) >= 2:
                        game.board.pop(); game.board.pop()
                    elif len(game.board.move_stack) == 1:
                        game.board.pop()
                    game.selected_square = None
                    check_msg = ""
                    ai_thinking_start = None
                    continue

            if game.promoting_move:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    q_rect = pygame.Rect(WIDTH//4 - 75, HEIGHT//2 - 50, 200, 100)
                    n_rect = pygame.Rect(WIDTH//2 + 25, HEIGHT//2 - 50, 200, 100)
                    
                    if q_rect.collidepoint(mx, my):
                        game.promoting_move.promotion = chess.QUEEN
                    elif n_rect.collidepoint(mx, my):
                        game.promoting_move.promotion = chess.KNIGHT
                    
                    if game.promoting_move.promotion:
                        game.board.push(game.promoting_move)
                        game.move_sound.play()
                        game.promoting_move = None
                        ai_thinking_start = pygame.time.get_ticks()
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and game.board.turn == chess.WHITE:
                mx, my = pygame.mouse.get_pos()
                file, rank = mx // SQUARE_SIZE, 4 - (my // SQUARE_SIZE)
                
                if 0 <= file < 5 and 0 <= rank < 5:
                    clicked_sq = chess.square(file, rank)
                    
                    if game.selected_square is None:
                        piece = game.board.piece_at(clicked_sq)
                        if piece and piece.color == chess.WHITE:
                            game.selected_square = clicked_sq
                    else:
                        move = chess.Move(game.selected_square, clicked_sq)
                        piece = game.board.piece_at(game.selected_square)
                        
                        if piece and piece.piece_type == chess.PAWN and rank == 4:
                            game.promoting_move = move
                            game.selected_square = None
                        elif move in get_mini_moves(game.board):
                            game.board.push(move)
                            game.move_sound.play() 
                            game.selected_square = None
                            ai_thinking_start = pygame.time.get_ticks() 
                        elif move.to_square == game.selected_square:
                            game.selected_square = None 
                        else:
                            new_piece = game.board.piece_at(clicked_sq)
                            if new_piece and new_piece.color == chess.WHITE:
                                game.selected_square = clicked_sq
                            else:
                                game.selected_square = None

        # eval game status: check or checkmate
        if not game_over:
            if game.board.is_checkmate():
                winner = "Black" if game.board.turn == chess.WHITE else "White"
                game_over_msg = f"Checkmate! {winner} wins. Click to restart."
                game_over = True
                restart_timer = pygame.time.get_ticks()
            elif game.board.is_check():
                check_msg = "CHECK"
            else:
                check_msg = ""

        if game.board.turn == chess.BLACK and not game.board.is_game_over() and not game.promoting_move and not game_over:
            if ai_thinking_start is None:
                ai_thinking_start = pygame.time.get_ticks()
            
            current_time = pygame.time.get_ticks()
            if current_time - ai_thinking_start >= AI_DELAY_MS:
                best_move = None
                min_val = float('inf')
                
                for move in get_mini_moves(game.board):
                    game.board.push(move)
                    val = minimax(game.board, 3, -float('inf'), float('inf'), True)
                    game.board.pop()
                    if val < min_val:
                        min_val, best_move = val, move
                
                if best_move:
                    piece = game.board.piece_at(best_move.from_square)
                    if piece and piece.piece_type == chess.PAWN and chess.square_rank(best_move.to_square) == 0:
                        best_move.promotion = chess.QUEEN
                    
                    game.board.push(best_move)
                    game.move_sound.play()
                
                ai_thinking_start = None

        screen.fill((0, 0, 0))
        game.draw(screen)

        # draw undo button
        pygame.draw.rect(screen, (50, 50, 50), undo_rect)
        font = pygame.font.SysFont("Arial", 24, bold=True)
        txt = font.render("UNDO", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=undo_rect.center)
        screen.blit(txt, txt_rect)

        # draw check message
        if check_msg:
            font = pygame.font.SysFont("Arial", 32, bold=True)
            text = font.render(check_msg, True, (255, 0, 0))
            screen.blit(text, (10, 10))

        # draw game over overlay
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            font = pygame.font.SysFont("Arial", 50, bold=True)
            lines = game_over_msg.split("\n")
            for i, line in enumerate(lines):
                text = font.render(line, True, (255, 255, 255))
                rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + i*60))
                screen.blit(text, rect)

            # automatic restart after a few seconds
            if restart_timer and pygame.time.get_ticks() - restart_timer > 3000:
                game = MiniChessGame()
                game_over = False
                game_over_msg = ""
                check_msg = ""
                ai_thinking_start = None
                restart_timer = None

        if game.promoting_move:
            game.draw_promotion_popup(screen)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()