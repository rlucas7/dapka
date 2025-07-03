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

from github import Github

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

def get_prs_with_copilot_comments(owner: str, repo: str, limit:int = 50000, login:str = "copilot-pull-request-reviewer") -> tuple[list[dict], list[str]]:
    """Get a list of pull requests with Copilot comments.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        limit (int): The maximum number of pull requests to fetch.

    Returns:
        tuple[list[dict], list[int]]: First entry is a list of prs and the reviews, 
        the second is a list of pull requests comment ids from Copilot comments.
    """
    # TODO: make this function more robust and handle no reviews case...
    cmd1 =f"gh pr list --repo {owner}/{repo} --state all --json reviews | jq '.[].reviews | map(select(.author.login == \"{login}\"))'"
    gh_cli_output1 = subprocess.run(cmd1, shell=True, check=True, capture_output=True, text=True)
    # Parse the output to extract pull request numbers
    comments = loads(gh_cli_output1.stdout)
    logger.info(f"Found {None} pull requests with Copilot comments in {owner}/{repo}")
    ghcp_comment_ids = [comment.get("id") for comment in comments]
    # now we need to get the PR numbers from the comments
    cmd2 = f"gh pr list --repo {owner}/{repo} --state all --json number,reviews"
    gh_cli_output2 = subprocess.run(cmd2, shell=True, check=True, capture_output=True, text=True)
    # Parse the output to extract pull request numbers and review ids
    pr_nums_n_reviews = loads(gh_cli_output2.stdout)
    return pr_nums_n_reviews, ghcp_comment_ids

def ghcp_pr_numbers(prs_with_reviews: list[dict], ghcp_comment_ids: list[str]) -> dict[int, list[dict]]:
    """Make a map of pull requests and their reviews.

    Args:
        prs_with_reviews (list[dict]): A list of pull requests with their reviews.
        ghcp_comment_ids (list[str]): A list of comment IDs from Copilot comments.

    Returns:
        list[int]: Alist of pull request numbers that have copilot comments.
    """
    pr_map = defaultdict(list)
    for pr in prs_with_reviews:
        pr_number = pr.get("number")
        reviews = pr.get("reviews", [])
        for review in reviews:
            if review.get("id") in ghcp_comment_ids:
                pr_map[pr_number].append(review)
        logger.info(f"Found {len(pr_map[pr_number])} pull requests with Copilot")
    return pr_map



if __name__ == "__main__":
    # Example usage-will return JSONDecodeError if run with erroneous owner/repo/limit
    args = parser.parse_args()
    owner = args.owner
    repo = args.repo
    limit = args.limit
    prs_with_reviews, ghcp_comment_ids = get_prs_with_copilot_comments(owner, repo, limit)
    pr_map = ghcp_pr_numbers(prs_with_reviews, ghcp_comment_ids)
    print(f"Pull requests with Copilot comments: {pr_map}")