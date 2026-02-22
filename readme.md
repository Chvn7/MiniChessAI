# Gardner Chess (5x5)

Gardner Chess is a 5 by 5 board chess, containing all kinds of chess pieces on the 1st row and pawn on the 2nd row. The game has roughly 9 x 10^18 legal positions, comparable in complexity to Checkers.

> **Note:** This game is officially a **weakly solved game**, meaning perfect play results in a draw. This AI implementation focuses on a challenging experience not the solved approach.
> (AI look 3 moves ahead using Minimax search, Alpha-Beta pruning, and a heuristic evaluation system)

## Gameplay Rules:

- **Castling:** No
- **Pawn Mechanics:**
  - **Promotion:** Yes
  - **Double-Step:** No
  - **En Passant:** No

## Setup

1. **Clone the repository:**
   ```
   git clone https://github.com/Chvn7/MiniChessAI.git
   ```
2. **Install required libraries:**
   ```
   cd MiniChessAI
   pip install -r requirements.txt
   ```
3. **Run**
   ```
   python main.py
   ```

## Assets & Credits

- **Chess Piece Assets:** [en:User:Cburnett](https://commons.wikimedia.org/wiki/User:Cburnett), licensed under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) via Wikimedia Commons.
