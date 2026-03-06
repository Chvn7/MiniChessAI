import pygame
import chess
import sys

from constants import WIDTH, HEIGHT, SQUARE_SIZE
from engine import get_mini_moves, minimax
from chess_game import MiniChessGame


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