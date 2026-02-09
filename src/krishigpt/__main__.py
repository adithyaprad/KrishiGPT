import logging
import os

from krishigpt.agent import test_pipeline


def main() -> None:
    level_name = os.getenv("KRISHIGPT_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, level_name, logging.INFO))
    test_pipeline()


if __name__ == "__main__":
    main()
