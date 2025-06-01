import argparse

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
        help="Number of people to fetch per API call."
    )
    args = parser.parse_args()

    api = FollowUpBossApi()
    writer = CsvWriter()

    batch_size = args.batch_size
    first_batch = True
    next_key = None

    while True:
        people_response = api.get_people(limit=batch_size, next_key=next_key)
        people = people_response.get('people', [])
        if not people:
            break
        writer.write_people(people, args.output_csv, append=not first_batch)
        first_batch = False
        next_key = people_response.get('_metadata', {}).get('next')
        if not next_key:
            break




if __name__ == "__main__":
    main()
