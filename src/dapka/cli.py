""" CLI module for Dapka.
This module provides a command-line interface for Dapka, allowing users to
add repositories, list them, and perform other actions directly from the terminal.

To find all PRs w/copilot comments, use:
    dapka --repo_url <repository_url>
"""
import argparse
import logging
import sys
import pandas as pd
from math import log

from graphics import plot_histogram
from repo_utils import get_pr_comments, get_pr_open_closed_and_state, get_list_of_all_prs

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler("dapka.log")])

logger = logging.getLogger(__name__)

# TODO: group the args here in a way that helps humans
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
    "--status",
    type=str,
    default="merged",
    choices=["open", "closed", "all", "merged"],
    help="The state of the pull requests to fetch.",
)
parser.add_argument(
    "--csv_write",
    action="store_true",
    help="Setting this flag causes the data to be collected against gh api and"
    "stored in local filesystem @ `pr_reviews_with_and_wo_ai.csv`.",
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
parser.add_argument(
    "--use_stdout",
    action="store_true",
    help="Setting this flag causes the logs to be output to stdout",
)
parser.add_argument(
    "--log_level",
    type=str,
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="Set the logging level for the CLI.",
)

def main(args) -> pd.DataFrame:
    """Main function to handle the repository URL.

    Args:
        repo_url (str): The URL of the repository to process.
    """
    args = parser.parse_args()
    if args.use_stdout:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(args.log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    if args.log_level != "INFO":
        print(f"Setting log level to {args.log_level}")
        logger.setLevel(args.log_level)
    prs_with_reviews = get_pr_comments(owner=args.owner, repo=args.repo, login=args.AILogin, state=args.status, limit=args.limit)
    pr_2_AI_reviews = dict()
    for entry in prs_with_reviews:
        logger.debug(f"Processing AI reviewed entry: {entry!r}")
        pr_num, reviews = entry.get("number"), entry.get("reviews", [])
        pr_2_AI_reviews[pr_num] = [review for review in reviews if review.get("author", {}).get("login") == args.AILogin]
    records = []
    for key, val in pr_2_AI_reviews.items():
        for review in val:
            pr_state = get_pr_open_closed_and_state(args.owner, args.repo, key)
            records.append({
                "pr_number": key,
                "review_id": review.get("id"),
                "author_login": review.get("author", {}).get("login"),
                "body": review.get("body"),
                "state": review.get("state"),
                "reviewed_at": review.get("submittedAt"),
                "owner": args.owner,
                "repo": args.repo,
                "pr_state": pr_state,
                "additions": pr_state.get("additions"),
                "deletions": pr_state.get("deletions"),
            })
    df = pd.DataFrame(records)
    logger.info(f"Data for AI PRs processed")
    logger.info(f"# of PRs with AILogin comments: {len(pr_2_AI_reviews.keys())}")
    logger.info(f"Repository {args.owner}/{args.repo} processed successfully.")
    ## TODO: clean up the code beneath, it is a bit messy, put it into a function
    # now we can also get the non-AI reviews
    ai_review_pr_numbers = [int(value) for value in df['pr_number'].values]
    latest_prs = get_list_of_all_prs(owner=args.owner, repo=args.repo, state = args.status, limit=args.limit)
    non_ai_count = len(set(latest_prs) - set(ai_review_pr_numbers))
    non_ai_prs = list(set(latest_prs) - set(ai_review_pr_numbers))
    logger.info(f"Total PRs in {args.owner}/{args.repo} with non-AI reviews: {non_ai_count}")
    # spot checking a few non-AI PRs shows that they are indeed non-AI reviews but they might be bots
    # e.g. 32766 is a bot review
    records = []
    # for now take the first N, TODO: make this more better
    for pr_num in non_ai_prs[:2*len(ai_review_pr_numbers)]:
        pr_state = get_pr_open_closed_and_state(args.owner, args.repo, pr_number=pr_num)
        logger.debug(f"pr_state: {pr_state!r}")
        records.append({
                "pr_number": pr_num,
                "review_id": pr_state.get("id"),
                "author_login": "Non-AI Review",
                "body": "N/A",
                "state": "N/A",
                "reviewed_at": "N/A",
                "owner": args.owner,
                "repo": args.repo,
                "pr_state": pr_state,
                "additions": pr_state.get("additions"),
                "deletions": pr_state.get("deletions"),
            })
    non_ai_prs_df = pd.DataFrame(records)
    # now get the times of the two types of PRs
    df['time_to_merge_in_seconds'] = df['pr_state'].apply(lambda x: x['time_to_merge_in_seconds'])
    non_ai_prs_df['time_to_merge_in_seconds'] = non_ai_prs_df['pr_state'].apply(lambda x: x['time_to_merge_in_seconds'])
    logger.info(f"shape of nans for non-ai PRs data: {non_ai_prs_df['time_to_merge_in_seconds'].isna().shape!r}")
    # a bunch of these are Nan so we will filter them out, this seems to be primarily for PRs that are not merged, in draft state.
    non_ai_prs_df = non_ai_prs_df[~non_ai_prs_df['time_to_merge_in_seconds'].isna()]
    df = pd.concat([df, non_ai_prs_df], ignore_index=True)
    if args.csv_write:
        # TODO: make this a cli-arg
        df.to_csv("pr_reviews_with_and_wo_ai.csv", index=False)
        logger.info(f"saved data to local file `pr_reviews_with_and_wo_ai.csv`")
    return df

if __name__ == "__main__":
    # Example usage-will return JSONDecodeError if run with erroneous owner/repo/limit
    args = parser.parse_args()
    if not args.csv_write:
        df = pd.read_csv("pr_reviews_with_and_wo_ai.csv")
    else:
        df = main(args)
    plot_histogram(df, 'author_login', 'time_to_merge_in_seconds', funcs=[log])