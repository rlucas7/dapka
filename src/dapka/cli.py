""" CLI module for Dapka.
This module provides a command-line interface for Dapka, allowing users to
add repositories, list them, and perform other actions directly from the terminal.

To find all PRs w/copilot comments, use:
    dapka --repo_url <repository_url>
"""
import argparse
import logging

import pandas as pd

from repo_utils import get_pr_comments


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

def main(args) -> None:
    """Main function to handle the repository URL.

    Args:
        repo_url (str): The URL of the repository to process.
    """
    args = parser.parse_args()
    owner, repo, limit, login = args.owner, args.repo, args.limit, args.AILogin
    prs_with_reviews = get_pr_comments(owner, repo, login, limit)
    pr_2_AI_reviews = dict()
    for entry in prs_with_reviews:
        pr_num, reviews = entry.get("number"), entry.get("reviews", [])
        pr_2_AI_reviews[pr_num] = [review for review in reviews if review.get("author", {}).get("login") == login]
    records = []
    for key, val in pr_2_AI_reviews.items():
        for review in val:
            records.append({
                "pr_number": key,
                "review_id": review.get("id"),
                "author_login": review.get("author", {}).get("login"),
                "body": review.get("body"),
                "state": review.get("state"),
                "reviewed_at": review.get("submittedAt"),
                "owner": owner,
                "repo": repo,
            })
    df = pd.DataFrame(records).to_csv("pr_reviews.csv", index=False)
    logger.info(f"Pull requests with AILogin comments: {len(pr_2_AI_reviews.keys())}")
    logger.info(f"Repository {owner}/{repo} processed successfully.")
    return df

if __name__ == "__main__":
    # Example usage-will return JSONDecodeError if run with erroneous owner/repo/limit
    args = parser.parse_args()
    df = main(args)