from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from image_batch_enhance_rotate_crop.ui import main


if __name__ == "__main__":
    main()
