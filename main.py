import pygame
import chess
import sys

from constants import (
    width, height, square_size, board_size,
    light_square, dark_square, coord_color,
    bg_color, game_bg_color, white_text, subtitle_text,
    error_text, check_text, overlay_color,
    btn_default, btn_hover, btn_border, btn_dark, btn_clear,
    btn_play, btn_remove, btn_remove_active,
    btn_palette, btn_palette_sel, palette_border,
    palette_w, palette_gap, piece_symbols, piece_map,
    ai_delay_ms,
)
from engine import get_mini_moves, minimax
from chess_game import MiniChessGame, GARDNER_FEN


# menu gardner, custom --later add desc
def start_menu(screen, clock, piece_images):
    title_font = pygame.font.SysFont("Arial", 52, bold=True)
    sub_font   = pygame.font.SysFont("Arial", 28)
    btn_font   = pygame.font.SysFont("Arial", 34, bold=True)

    btn_w, btn_h = 340, 70
    gap = 30
    top_y = (height // 2) + 20

    gardner_rect = pygame.Rect((width - btn_w) // 2, top_y, btn_w, btn_h)
    custom_rect  = pygame.Rect((width - btn_w) // 2, top_y + btn_h + gap, btn_w, btn_h)

    hover = None

    while True:
        mx, my = pygame.mouse.get_pos()
        hover = None
        if gardner_rect.collidepoint(mx, my):
            hover = "gardner"
        elif custom_rect.collidepoint(mx, my):
            hover = "custom"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hover:
                    return hover

        screen.fill(bg_color)

        title = title_font.render("Mini Chess AI", True, white_text)
        screen.blit(title, title.get_rect(center=(width // 2, height // 4)))

        subtitle = sub_font.render("Choose game mode", True, subtitle_text)
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, height // 4 + 60)))

        # board preview
        preview_size = 24
        preview_x = width // 2 - (preview_size * 5) // 2
        preview_y = height // 4 + 95
        for r in range(board_size):
            for c in range(board_size):
                col = light_square if (r + c) % 2 == 0 else dark_square
                pygame.draw.rect(screen, col,
                                 (preview_x + c * preview_size,
                                  preview_y + r * preview_size,
                                  preview_size, preview_size))

        # buttons
        for rect, label, mode_key in [
            (gardner_rect, "Gardner  (5×5)", "gardner"),
            (custom_rect,  "Custom Position", "custom"),
        ]:
            color = btn_hover if hover == mode_key else btn_default
            pygame.draw.rect(screen, color, rect, border_radius=12)
            pygame.draw.rect(screen, btn_border, rect, width=2, border_radius=12)
            txt = btn_font.render(label, True, white_text)
            screen.blit(txt, txt.get_rect(center=rect.center))

        pygame.display.flip()
        clock.tick(30)

def custom_position_editor(screen, clock, piece_images):

    # place/remove pieces on a 5×5 board
    # return FEN str when click PLAY

    # widen the window for piece select on the right
    board_px = board_size * square_size
    panel_w = 2 * palette_w + palette_gap + 60
    editor_w = board_px + panel_w
    editor_h = height
    screen = pygame.display.set_mode((editor_w, editor_h))
    pygame.display.set_caption("Custom Position Editor")

    font      = pygame.font.SysFont("Arial", 24, bold=True)
    big_font  = pygame.font.SysFont("Arial", 32, bold=True)
    hint_font = pygame.font.SysFont("Arial", 18)

    # board state
    board_pieces = {}
    selected_piece_sym = None

    pal_x = board_px + 30
    full_w = 2 * palette_w + palette_gap  # full panel width

    # split pieces: black top, white bottom
    black_pieces = ['k', 'q', 'r', 'b', 'n', 'p']
    white_pieces = ['K', 'Q', 'R', 'B', 'N', 'P']

    # ── top section: black pieces ──
    black_label_y = 15
    black_top = black_label_y + 35

    def black_rect_for(i):
        col = i % 2
        row = i // 2
        x = pal_x + col * (palette_w + palette_gap)
        y = black_top + row * (palette_w + palette_gap)
        return pygame.Rect(x, y, palette_w, palette_w)

    # ── middle section: command buttons ──
    black_bottom = black_top + 3 * (palette_w + palette_gap)
    mid_y = black_bottom + 20
    btn_w = full_w
    btn_h = 44

    remove_rect = pygame.Rect(pal_x, mid_y, btn_w, btn_h)
    clear_rect  = pygame.Rect(pal_x, mid_y + btn_h + 10, btn_w, btn_h)
    play_rect   = pygame.Rect(pal_x, mid_y + 2 * (btn_h + 10), btn_w, btn_h)
    back_rect   = pygame.Rect(pal_x, mid_y + 3 * (btn_h + 10), btn_w, btn_h)

    # ── bottom section: white pieces ──
    white_label_y = back_rect.bottom + 20
    white_top = white_label_y + 35

    def white_rect_for(i):
        col = i % 2
        row = i // 2
        x = pal_x + col * (palette_w + palette_gap)
        y = white_top + row * (palette_w + palette_gap)
        return pygame.Rect(x, y, palette_w, palette_w)

    remove_mode = False
    error_msg = ""
    error_timer = 0

    def restore_window():
        nonlocal screen
        screen = pygame.display.set_mode((width, height))

    while True:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_palette = False

                # black piece click
                for i, sym in enumerate(black_pieces):
                    pr = black_rect_for(i)
                    if pr.collidepoint(mx, my):
                        selected_piece_sym = sym
                        remove_mode = False
                        clicked_palette = True
                        break

                # white piece click
                if not clicked_palette:
                    for i, sym in enumerate(white_pieces):
                        pr = white_rect_for(i)
                        if pr.collidepoint(mx, my):
                            selected_piece_sym = sym
                            remove_mode = False
                            clicked_palette = True
                            break

                if remove_rect.collidepoint(mx, my):
                    remove_mode = True
                    selected_piece_sym = None
                    clicked_palette = True

                # board click
                if not clicked_palette:
                    file = mx // square_size
                    rank = 4 - (my // square_size)
                    if 0 <= file < board_size and 0 <= rank < board_size:
                        sq = chess.square(file, rank)
                        if remove_mode:
                            board_pieces.pop(sq, None)
                        elif selected_piece_sym:
                            board_pieces[sq] = chess.Piece.from_symbol(selected_piece_sym)

                # PLAY button
                if play_rect.collidepoint(mx, my):
                    syms = [p.symbol() for p in board_pieces.values()]
                    if 'K' not in syms or 'k' not in syms:
                        error_msg = "Both kings required!"
                        error_timer = pygame.time.get_ticks()
                    else:
                        fen = board_dict_to_fen(board_pieces)
                        restore_window()
                        return fen

                # CLEAR button
                if clear_rect.collidepoint(mx, my):
                    board_pieces.clear()

                # BACK button
                if back_rect.collidepoint(mx, my):
                    restore_window()
                    return None

        # ── draw ──
        screen.fill(bg_color)

        # board
        for r in range(board_size):
            for c in range(board_size):
                sq = chess.square(c, 4 - r)
                color = light_square if (r + c) % 2 == 0 else dark_square
                pygame.draw.rect(screen, color,
                                 (c * square_size, r * square_size, square_size, square_size))
                if sq in board_pieces:
                    screen.blit(piece_images[board_pieces[sq].symbol()],
                                (c * square_size, r * square_size))

        # coordinates
        coord_font = pygame.font.SysFont("Arial", 28, bold=True)
        for r in range(board_size):
            num = str(5 - r)
            text = coord_font.render(num, True, coord_color)
            screen.blit(text, (5, r * square_size + 5))
        for c in range(board_size):
            letter = chr(ord('a') + c)
            text = coord_font.render(letter, True, coord_color)
            screen.blit(text, (c * square_size + square_size - 24, board_size * square_size - 30))

        # ── right panel ──

        # -- top: black pieces --
        lbl = big_font.render("Black", True, white_text)
        screen.blit(lbl, (pal_x, black_label_y))
        for i, sym in enumerate(black_pieces):
            pr = black_rect_for(i)
            is_sel = (selected_piece_sym == sym and not remove_mode)
            bg = btn_palette_sel if is_sel else btn_palette
            pygame.draw.rect(screen, bg, pr, border_radius=8)
            pygame.draw.rect(screen, palette_border, pr, width=2, border_radius=8)
            img = piece_images[sym]
            scaled = pygame.transform.scale(img, (palette_w - 12, palette_w - 12))
            screen.blit(scaled, (pr.x + 6, pr.y + 6))

        # -- middle: command buttons --
        rm_bg = btn_remove_active if remove_mode else btn_remove
        pygame.draw.rect(screen, rm_bg, remove_rect, border_radius=8)
        pygame.draw.rect(screen, palette_border, remove_rect, width=2, border_radius=8)
        rm_txt = font.render("REMOVE", True, white_text)
        screen.blit(rm_txt, rm_txt.get_rect(center=remove_rect.center))

        pygame.draw.rect(screen, btn_clear, clear_rect, border_radius=10)
        pygame.draw.rect(screen, btn_border, clear_rect, width=2, border_radius=10)
        cl_txt = font.render("CLEAR", True, white_text)
        screen.blit(cl_txt, cl_txt.get_rect(center=clear_rect.center))

        pygame.draw.rect(screen, btn_play, play_rect, border_radius=10)
        pygame.draw.rect(screen, btn_border, play_rect, width=2, border_radius=10)
        pl_txt = font.render("PLAY", True, white_text)
        screen.blit(pl_txt, pl_txt.get_rect(center=play_rect.center))

        pygame.draw.rect(screen, btn_default, back_rect, border_radius=10)
        pygame.draw.rect(screen, btn_border, back_rect, width=2, border_radius=10)
        bk_txt = font.render("← BACK", True, white_text)
        screen.blit(bk_txt, bk_txt.get_rect(center=back_rect.center))

        # -- bottom: white pieces --
        lbl2 = big_font.render("White", True, white_text)
        screen.blit(lbl2, (pal_x, white_label_y))
        for i, sym in enumerate(white_pieces):
            pr = white_rect_for(i)
            is_sel = (selected_piece_sym == sym and not remove_mode)
            bg = btn_palette_sel if is_sel else btn_palette
            pygame.draw.rect(screen, bg, pr, border_radius=8)
            pygame.draw.rect(screen, palette_border, pr, width=2, border_radius=8)
            img = piece_images[sym]
            scaled = pygame.transform.scale(img, (palette_w - 12, palette_w - 12))
            screen.blit(scaled, (pr.x + 6, pr.y + 6))

        # error message
        if error_msg and pygame.time.get_ticks() - error_timer < 2000:
            err = big_font.render(error_msg, True, error_text)
            screen.blit(err, err.get_rect(center=(board_px // 2, editor_h - 40)))
        else:
            error_msg = ""

        pygame.display.flip()
        clock.tick(30)


def board_dict_to_fen(board_pieces):
    """Convert a dict {square: chess.Piece} into a FEN (white to move)."""
    rows = []
    for rank in range(7, -1, -1):          # FEN goes from rank 8 → 1
        row = ""
        empty = 0
        for file in range(8):
            sq = chess.square(file, rank)
            if sq in board_pieces:
                if empty:
                    row += str(empty)
                    empty = 0
                row += board_pieces[sq].symbol()
            else:
                empty += 1
        if empty:
            row += str(empty)
        rows.append(row)
    return "/".join(rows) + " w - - 0 1"


# Main game (FEN)
def play_game(screen, clock, fen=None):
    """Run the actual chess game. Returns when the player should go back to menu."""
    pygame.display.set_caption("Gardner Minichess AI")
    game = MiniChessGame(fen)

    ai_thinking_start = None

    game_over = False
    game_over_msg = ""
    check_msg = ""
    restart_timer = None

    # undo & menu buttons
    undo_rect = pygame.Rect(width - 120, 10, 110, 40)
    menu_rect = pygame.Rect(width - 250, 10, 110, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # game over → click returns to menu
            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                return

            if not game_over and not game.promoting_move:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    emx, emy = pygame.mouse.get_pos()
                    if undo_rect.collidepoint(emx, emy):
                        if len(game.board.move_stack) >= 2:
                            game.board.pop(); game.board.pop()
                        elif len(game.board.move_stack) == 1:
                            game.board.pop()
                        game.selected_square = None
                        check_msg = ""
                        ai_thinking_start = None
                        continue
                    # menu
                    if menu_rect.collidepoint(emx, emy):
                        return  # back to menu

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
                    pmx, pmy = pygame.mouse.get_pos()
                    q_rect = pygame.Rect(width // 4 - 75, height // 2 - 50, 200, 100)
                    n_rect = pygame.Rect(width // 2 + 25, height // 2 - 50, 200, 100)

                    if q_rect.collidepoint(pmx, pmy):
                        game.promoting_move.promotion = chess.QUEEN
                    elif n_rect.collidepoint(pmx, pmy):
                        game.promoting_move.promotion = chess.KNIGHT

                    if game.promoting_move.promotion:
                        game.board.push(game.promoting_move)
                        game.move_sound.play()
                        game.promoting_move = None
                        ai_thinking_start = pygame.time.get_ticks()
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and game.board.turn == chess.WHITE:
                mx, my = pygame.mouse.get_pos()
                file, rank = mx // square_size, 4 - (my // square_size)

                if 0 <= file < board_size and 0 <= rank < board_size:
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

        # check / checkmate
        if not game_over:
            if game.board.is_checkmate():
                winner = "Black" if game.board.turn == chess.WHITE else "White"
                game_over_msg = f"Checkmate! {winner} wins.\nClick to return to menu."
                game_over = True
                restart_timer = pygame.time.get_ticks()
            elif game.board.is_check():
                check_msg = "CHECK"
            else:
                check_msg = ""

        # AI move
        if (game.board.turn == chess.BLACK
            and not game.board.is_game_over()
            and not game.promoting_move
            and not game_over):
            if ai_thinking_start is None:
                ai_thinking_start = pygame.time.get_ticks()
            if pygame.time.get_ticks() - ai_thinking_start >= ai_delay_ms:
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

        # draw
        screen.fill(game_bg_color)
        game.draw(screen)

        # undo button
        pygame.draw.rect(screen, btn_dark, undo_rect, border_radius=6)
        ufont = pygame.font.SysFont("Arial", 24, bold=True)
        utxt = ufont.render("UNDO", True, white_text)
        screen.blit(utxt, utxt.get_rect(center=undo_rect.center))

        # menu button
        pygame.draw.rect(screen, btn_dark, menu_rect, border_radius=6)
        mtxt = ufont.render("MENU", True, white_text)
        screen.blit(mtxt, mtxt.get_rect(center=menu_rect.center))

        # check msg
        if check_msg:
            cfont = pygame.font.SysFont("Arial", 32, bold=True)
            ctext = cfont.render(check_msg, True, check_text)
            screen.blit(ctext, (10, 10))

        # game over overlay
        if game_over:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill(overlay_color)
            screen.blit(overlay, (0, 0))
            go_font = pygame.font.SysFont("Arial", 50, bold=True)
            lines = game_over_msg.split("\n")
            for i, line in enumerate(lines):
                text = go_font.render(line, True, white_text)
                rect = text.get_rect(center=(width // 2, height // 2 + i * 60))
                screen.blit(text, rect)

        if game.promoting_move:
            game.draw_promotion_popup(screen)
        pygame.display.flip()
        clock.tick(30)


def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Mini Chess AI")
    clock = pygame.time.Clock()

    # pre-load piece images once (shared by menu, editor, game)
    piece_images = {}
    for sym, part in piece_map.items():
        img = pygame.image.load(f"assets/images/pieces/Chess_{part}.png")
        piece_images[sym] = pygame.transform.scale(img, (square_size, square_size))

    while True:
        screen = pygame.display.get_surface()
        mode = start_menu(screen, clock, piece_images)

        if mode == "gardner":
            play_game(screen, clock)

        elif mode == "custom":
            fen = custom_position_editor(screen, clock, piece_images)
            screen = pygame.display.get_surface()
            if fen:
                play_game(screen, clock, fen=fen)


if __name__ == "__main__":
    main()