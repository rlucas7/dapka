""" The purpose of this module is to provide utility functions for handling input and output
 operations related to repositories and pull requests in the Dapka project.
"""


import logging

from csv import DictReader, DictWriter


logger = logging.getLogger(__name__)

def read_csv(file_path: str) -> list[dict]:
    """Read a CSV file and return its content as a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list[dict]: A list of dictionaries representing the rows in the CSV file.
    """
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = DictReader(csvfile)
        return [row for row in reader]

def write_csv(file_path: str, data: list[dict]) -> None:
    """Write a list of dictionaries to a CSV file.

    Args:
        file_path (str): The path to the CSV file.
        data (list[dict]): A list of dictionaries to write to the CSV file.
    """
    if not data:
        logger.warning("No data provided to write to CSV.")
        return

    with open(file_path, mode='w', encoding='utf-8', newline='') as csvfile:
        writer = DictWriter(csvfile, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    logger.info(f"Data written to {file_path} successfully.")   
