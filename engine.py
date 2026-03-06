import pygame
import chess


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
