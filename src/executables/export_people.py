import argparse
import time

import requests
from ryutils import log

from constants import CSV_TEMPLATE
from csv_writer import CsvWriter
from followupboss_api import FollowUpBossApi


def run_serial_export(args: argparse.Namespace, writer: CsvWriter) -> None:
    batch_size = args.batch_size
    api = FollowUpBossApi()
    fetch_count = 0
    failed_count = 0
    first_batch = True

    total_people = api.get_total_people()
    log.print_ok(f"Total people: {total_people}")

    offset = 0
    while True:
        log.print_ok_blue(f"Fetching people from Follow Up Boss: {fetch_count}")
        try:
            people_response = api.get_people(limit=batch_size, offset=offset)
        except requests.exceptions.RequestException as e:
            log.print_fail(f"Error fetching people: {e}")
            log.print_fail(f"Sleeping for {failed_count * 1.1} seconds")
            failed_count += 1
            time.sleep(1 + failed_count * 1.1)
            continue
        failed_count = 0
        people = people_response.get("people", [])
        if not people:
            break
        fetch_count += len(people)
        writer.write_people(people, args.output_csv, append=not first_batch)
        first_batch = False
        offset += batch_size
        if fetch_count >= total_people:
            break


def parse_args() -> argparse.Namespace:
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
    parser.add_argument(
        "--skip-duplicate-names",
        action="store_true",
        help="Skip duplicate names.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    writer = CsvWriter(skip_duplicate_names=args.skip_duplicate_names)

    if args.clean_csv:
        log.print_ok_blue("Cleaning CSV file")
        writer.erase_file(args.output_csv)

    start_time = time.time()
    run_serial_export(args, writer)

    end_time = time.time()
    log.print_ok_blue(f"Export completed in {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    main()
