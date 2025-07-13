"""
This module provides utility functions for interacting with repositories, such as fetching pull requests and custom instructions for AI reviewers.
It includes functions to retrieve pull requests with Copilot comments, parse them, and return a map of pull requests with their reviews.
It also includes a command-line interface for fetching pull requests from a specified repository.
It uses the GitHub CLI to fetch pull requests and their reviews, and it requires `gh` and `jq` to be installed on the system.
The module is designed to be used as a standalone script or imported into other Python scripts for further processing.

# Project: DAPKA
# File Created: Wednesday, 1st July 2025 11:00:00 EST
# Author: Roberts, Lucas
# Email: rlucas7@vt.edu
# example usage:
# python3 -i repo_utils.py  --owner rlucas7 --repo suggerere
"""
import argparse
import logging
import subprocess

from collections import defaultdict
from json import loads
from typing import Union

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Get map of pull requests with Copilot comments.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    "--owner",
    type=str,
    required=True,
    help="The owner of the repository.",
)
parser.add_argument(
    "--repo",
    type=str,
    required=True,
    help="The name of the repository.",
)
parser.add_argument(
    "--limit",
    type=int,
    default=50000,
    help="The maximum number of pull requests to fetch.",
)
parser.add_argument(
    "--AILogin",
    type=str,
    default="copilot-pull-request-reviewer",
    choices=["copilot-pull-request-reviewer", "github-copilot", "coderabbitai"],
    help="The maximum number of pull requests to fetch.",
)

def get_code_review_instructions(filepath_and_name:str = ".github/copilot-instructions.md") -> Union[str, None]:
    """Get instructions for the AI reviewer.

    Returns:
        str: Instructions for the AI reviewer.

    Note:
    This function provides fetches instructions for the AI reviewer from the repository's custom instructions.
    https://docs.github.com/en/copilot/how-tos/custom-instructions/adding-repository-custom-instructions-for-github-copilot#example

    We assume the instructions are locally stored in a file named `.github/copilot-instructions.md` which is a common practice for github repositories.
    If the file is not found, it returns None or a default message.
    If the file is found, it reads the content and returns it as a string.
    If the file is not found, it logs a warning and returns None.
    """
    try:
        with open(filepath_and_name, "r") as file:
            instructions = file.read()
        logger.info(f"Loaded custom instructions from {filepath_and_name}")
        return instructions
    except FileNotFoundError:
        logger.warning(f"Custom instructions file {filepath_and_name} not found. Using default instructions.")
        # Return None or a default message if the file is not found
        return None

def get_list_of_all_prs(owner: str, repo: str, limit:int = 50000) -> list[int]:
    """Get a list of all pull requests from the repository

    Args:
        repo_url (str): The URL of the repository to fetch PRs from.

    Returns:
        list[int]: A list of pull request URLs.

    Note:
    This function uses the GitHub CLI to fetch all pull requests from the specified repository.
    It runs a shell command to list all pull requests and then parses the output to extract the pull request numbers.
    It returns a list of integers representing the pull request numbers.
    If the command fails, it raises a subprocess.CalledProcessError.
    The command used is:
    ```bash
        gh pr list --repo owner/repo --state all -L limit --json number | jq '.[].number'
    ```
    We assume that the GitHub CLI (`gh`) and `jq` are installed and configured on the system where this function is executed.
    """
    cmd = f"gh pr list --repo {owner}/{repo} --state all -L {limit} --json number | jq '.[].number'"
    gh_cli_output = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    pr_numbers = [int(pr_num) for pr_num in gh_cli_output.stdout.split('\n') if len(pr_num) > 0]
    logger.info(f"Found {len(pr_numbers)} pull requests in {owner}/{repo}")
    return pr_numbers

def get_pr_comments(owner: str, repo: str, login:str, limit:int = 50000) -> list[dict]:
    """Get a list of pull requests with Copilot comments.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        login (str): The login of the AI reviewer (e.g., 'copilot-pull-request-reviewer') for which we want to fetch the comments.
        limit (int): The maximum number of pull requests to fetch. Defaults to 50000.

    Returns:
        list[dict]: a list of prs and the reviews
    """
    # TODO: make this function more robust and handle no reviews case...
    logger.info(f"Getting pull requests with comments in {owner}/{repo}")
    # now we need to get the PR numbers from the comments
    cmd = f"gh pr list --repo {owner}/{repo} --state all --json number,reviews --limit {limit}"
    gh_cli_output = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    # Parse the output to extract pull request numbers and review ids
    pr_nums_n_comments = loads(gh_cli_output.stdout)
    return pr_nums_n_comments


if __name__ == "__main__":
    # Example usage-will return JSONDecodeError if run with erroneous owner/repo/limit
    args = parser.parse_args()
    owner, repo, limit, login = args.owner, args.repo, args.limit, args.AILogin
    prs_with_reviews = get_pr_comments(owner, repo, login, limit)
    # now filter to only those with copilot comments
    pr_2_AI_reviews = dict()
    for entry in prs_with_reviews:
        pr_num, reviews = entry.get("number"), entry.get("reviews", [])
        pr_2_AI_reviews[pr_num] = [review for review in reviews if review.get("author", {}).get("login") == login]
    print(f"Pull requests with AILogin comments: {pr_2_AI_reviews}")