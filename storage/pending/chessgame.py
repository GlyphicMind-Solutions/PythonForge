#chessgame.py
#created with GlyphicMind Solutions: PythonForge

import pygame
import sys
import yaml
from pathlib import Path
from llama_cpp import Llama
import chess

# Basic chessboard settings
BOARD_SIZE = 8
SQUARE_SIZE = 80
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

# Piece representation: mapping board symbols to Unicode
PIECES = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛',
    'k': '♚', 'p': '♟', 'R': '♖', 'N': '♘',
    'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙', None: ''
}

# Load model manifest
MODEL_DIR = Path(__file__).parent / "models"
MANIFEST_FILE = MODEL_DIR / "manifest.yaml"

def load_manifest():
    if not MANIFEST_FILE.exists():
        raise FileNotFoundError(f"Manifest file not found: {MANIFEST_FILE}")
    with open(MANIFEST_FILE, "r") as f:
        data = yaml.safe_load(f)
    return data.get("models", {})

def choose_model(models):
    print("Available models:")
    for key in models:
        print(f" - {key}")
    choice = input("Select a model to play as (or press Enter for default): ").strip()
    if not choice:
        choice = "gpt_default"
    if choice not in models:
        print(f"Model {choice} not found. Falling back to gpt_default.")
        choice = "gpt_default"
    return choice, models[choice]

class ChessGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Python Chess')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, SQUARE_SIZE // 2)

        # Board as a python-chess object
        self.board = chess.Board()
        self.selected = None
        self.turn = 'white'  # 'white' or 'black'

        # LLM integration
        self.models = load_manifest()
        model_key, model_cfg = choose_model(self.models)
        self.model_path = Path(model_cfg["path"])
        if not self.model_path.is_absolute():
            self.model_path = MODEL_DIR / self.model_path
        self.llm = Llama(
            model_path=str(self.model_path),
            n_ctx=model_cfg.get("n_ctx", 2048),
            n_threads=4,
        )
        self.ai_color = None
        self.setup_ai_color()

    def setup_ai_color(self):
        while True:
            choice = input("Play as White or Black? (W/B): ").strip().lower()
            if choice in ("w", "white"):
                self.ai_color = "black"
                self.turn = "white"
                print("You are White, AI is Black.")
                break
            if choice in ("b", "black"):
                self.ai_color = "white"
                self.turn = "black"
                print("You are Black, AI is White.")
                break
            print("Invalid choice. Please enter 'W' or 'B'.")

    def draw_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = GRAY if (row + col) % 2 == 0 else WHITE
                pygame.draw.rect(self.screen, color,
                                 (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                square = chess.square(col, 7 - row)
                piece = self.board.piece_at(square)
                if piece:
                    sym = piece.symbol()
                    piece_color = BLACK if sym.isupper() else GREEN
                    text = self.font.render(PIECES[sym], True, piece_color)
                    rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2,
 row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    self.screen.blit(text, rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            if self.turn == self.ai_color:
                pygame.display.flip()
                self.ai_make_move()
                continue

            self.draw_board()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_click(self, pos):
        col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
        square = chess.square(col, 7 - row)
        if not self.selected:
            if self.board.piece_at(square):
                if (self.turn == 'white' and self.board.piece_at(square).color == chess.WHITE) or \
                   (self.turn == 'black' and self.board.piece_at(square).color == chess.BLACK):
                    self.selected = square
        else:
            if square != self.selected:
                move = chess.Move(self.selected, square)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.turn = 'black' if self.turn == 'white' else 'white'
                else:
                    print("Illegal move attempted.")
            self.selected = None

    def ai_make_move(self):
        # Convert board to FEN and ASCII board string
        ascii_board = str(self.board)
        prompt = (
            f"Current board (ASCII):\n{ascii_board}\n"
            f"It's {self.ai_color} turn. Provide a move in UCI format (e.g. e2e4)."
        )
        result = self.llm(prompt, max_tokens=32, temperature=0.7, top_k=40, top_p=0.9)
        move_text = result["choices"][0]["text"].strip()
        if len(move_text) >= 4:
            try:
                move = chess.Move.from_uci(move_text[:4])
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.turn = 'black' if self.turn == 'white' else 'white'
                    print(f"AI moved: {move_text[:4]}")
                else:
                    print(f"AI proposed illegal move: {move_text[:4]}")
            except Exception as e:
                print(f"Error parsing AI move: {move_text[:4]} ({e})")
        else:
            print(f"AI produced incomplete response: {move_text}")

if __name__ == "__main__":
    game = ChessGame()
    game.run()