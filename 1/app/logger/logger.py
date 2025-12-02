import sys
import logging
import os
from typing import List

def setup_logging(log_level = logging.DEBUG) -> None:
  log_dir = os.path.join(os.getcwd(), "logs")
  os.makedirs(log_dir, exist_ok=True)
  log_file_n = len(os.listdir(log_dir)) + 1
  log_file = os.path.join(log_dir, f"run-{log_file_n}.log")
  
  logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
      logging.StreamHandler(sys.stdout),
      logging.FileHandler(log_file, mode="a"),
    ]
)
