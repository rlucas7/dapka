"""
This module provides utility functions for interacting with repositories, such as fetching pull requests and custom instructions for AI reviewers.
"""
import logging

from pyGitHub import GitHub

def get_code_review_instructions(filepath_and_name=".github/copilot-instructions.md") -> str | None:
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
    logger.info(f"Found {len(pr_numbers)} pull requests in {repo_url}")
    return pr_numbers

def get_prs_with_copilot_comments(owner: str, repo: str, limit:int = 50000, login:str = "copilot-pull-request-reviewer") -> list[int]:
    """Get a list of pull requests with Copilot comments.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        limit (int): The maximum number of pull requests to fetch.

    Returns:
        list[int]: A list of pull request numbers that have Copilot comments.
    """
    cmd = f"gh pr list --repo {owner}/{repo} --state all --json reviews | jq '.[].reviews | map(select(.author.login == \"{login}\"))'"
    gh_cli_output = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
    logger.info(f"Found {len(prs)} pull requests with Copilot comments in {owner}/{repo}")
    return prs