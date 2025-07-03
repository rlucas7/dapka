# Project: DAPKA
# File Created: Wednesday, 1st July 2025 11:00:00 EST

import argparse
import logging

from dapka.cli import main

parser = argparse.ArgumentParser(description="The DAPKA cli tool.", HelpFormatter=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "--repo_url",
    type=str,
    required=True,
    help="The URL of the repository to scan.",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    args = parser.parse_args()
    if not args.repo_url:
        parser.error("The --repo_url argument is required.")
    # Here you would typically call a function to handle the repository URL,
    # such as adding it to a database or processing it in some way.
    logger.info(f"Processing repository URL: {args.repo_url}")
    main(args.repo_url)