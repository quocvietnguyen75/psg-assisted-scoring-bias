"""Run protocol 001 M1 for respiratory."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from event_m1 import main
if __name__ == '__main__':
    main('respiratory')
