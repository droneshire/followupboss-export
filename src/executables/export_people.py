import argparse
import time

import requests
from ryutils import log

from constants import CSV_TEMPLATE
from csv_writer import CsvWriter
from followupboss_api import FollowUpBossApi


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-csv",
        type=str,
        default=CSV_TEMPLATE,
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of people to fetch per API call.",
    )
    parser.add_argument(
        "--clean-csv",
        action="store_true",
        help="Clean the CSV file before writing.",
    )
    args = parser.parse_args()

    api = FollowUpBossApi()
    writer = CsvWriter()

    batch_size = args.batch_size
    first_batch = True
    next_key = None

    log.print_ok_blue(f"Exporting people to {args.output_csv}")

    if args.clean_csv:
        log.print_ok_blue("Cleaning CSV file")
        writer.erase_file(args.output_csv)

    fetch_count = 0
    while True:
        log.print_ok_blue(f"Fetching people from Follow Up Boss: {fetch_count}")
        try:
            people_response = api.get_people(limit=batch_size, next_key=next_key)
        except requests.exceptions.RequestException as e:
            log.print_error(f"Error fetching people: {e}")
            time.sleep(1)
            break
        people = people_response.get("people", [])
        if not people:
            break
        fetch_count += len(people)
        writer.write_people(people, args.output_csv, append=not first_batch)
        first_batch = False
        next_key = people_response.get("_metadata", {}).get("next")
        if not next_key:
            break


if __name__ == "__main__":
    main()
