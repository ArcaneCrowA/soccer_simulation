import argparse
import os

from src.load import run_simulation
from src.train import run_training

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train",
        type=int,
        metavar="N",
        help="Train the model for N episodes in headless mode.",
    )
    parser.add_argument(
        "--speed",
        type=int,
        default=10,
        help="Training speed multiplier (default: 10). Processes multiple ticks per iteration.",
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="Load pre-trained models for simulation.",
    )
    args = parser.parse_args()

    if args.train:
        # In training mode, we don't need the full pygame video setup
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        run_training(args.train, speed_multiplier=args.speed)
    else:
        run_simulation(load_models=args.load)
