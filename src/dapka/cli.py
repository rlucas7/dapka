""" CLI module for Dapka.
This module provides a command-line interface for Dapka, allowing users to
add repositories, list them, and perform other actions directly from the terminal.

To find all PRs w/copilot comments, use:
    dapka --repo_url <repository_url>
"""
import logging

from pyGitHub import GitHub

logger = logging.getLogger(__name__)

def main(repo_url: str) -> None:
    """Main function to handle the repository URL.

    Args:
        repo_url (str): The URL of the repository to process.
    """
    logger.info(f"Processing repository URL: {repo_url}")
    github = GitHub()
    github.add_repo(repo_url)
    logger.info(f"Repository {repo_url} added successfully.")



