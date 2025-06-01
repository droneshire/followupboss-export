import argparse
import time
from multiprocessing import Process, Queue, cpu_count
from typing import Generator

import requests
from ryutils import log

from constants import CSV_TEMPLATE
from csv_writer import CsvWriter
from followupboss_api import FollowUpBossApi


def worker_task(task_queue: Queue, result_queue: Queue, batch_size: int) -> None:
    api = FollowUpBossApi()
    while True:
        next_key = task_queue.get()
        if next_key is None:
            break
        retry = 0
        while True:
            try:
                people_response = api.get_people(limit=batch_size, next_key=next_key)
                result_queue.put(
                    (
                        people_response.get("people", []),
                        people_response.get("_metadata", {}).get("next"),
                    )
                )
                break
            except requests.exceptions.RequestException:
                sleep_time = min(60, 2**retry)
                time.sleep(sleep_time)
                retry += 1


def enqueue_initial_tasks(task_queue: Queue, initial_next_key: str | None) -> None:
    # Seed the queue with the first N next_keys (None for the first page)
    task_queue.put(initial_next_key)


def write_batches_from_queue(
    result_queue: Queue, writer: CsvWriter, output_csv: str, first_batch_flag: bool
) -> Generator[str, None, None]:
    fetch_count = 0
    first_batch = first_batch_flag
    while True:
        people, next_key = result_queue.get()
        if people is None:
            break
        writer.write_people(people, output_csv, append=not first_batch)
        fetch_count += len(people)
        first_batch = False
        if next_key:
            yield next_key
        else:
            break


def run_parallel_export(args: argparse.Namespace, writer: CsvWriter) -> None:
    batch_size = args.batch_size
    num_workers = max(2, cpu_count() - 1)
    task_queue: Queue = Queue(maxsize=num_workers * 2)
    result_queue: Queue = Queue(maxsize=num_workers * 2)
    log.print_ok_blue(f"Exporting people to {args.output_csv}")

    # Start worker processes
    workers = [
        Process(target=worker_task, args=(task_queue, result_queue, batch_size))
        for _ in range(num_workers)
    ]
    for w in workers:
        w.start()

    # Seed the first task
    enqueue_initial_tasks(task_queue, None)

    first_batch = True
    next_keys = set()
    start_time = time.time()

    while True:
        # Get results and write to CSV
        for next_key in write_batches_from_queue(
            result_queue, writer, args.output_csv, first_batch
        ):
            if next_key and next_key not in next_keys:
                task_queue.put(next_key)
                next_keys.add(next_key)
        break

    # Stop workers
    for _ in workers:
        task_queue.put(None)
    for w in workers:
        w.join()

    end_time = time.time()
    log.print_ok_blue(f"Export completed in {end_time - start_time:.2f} seconds.")


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
        "--parallel",
        action="store_true",
        help="Run the export in parallel.",
    )
    return parser.parse_args()


def run_serial_export(args: argparse.Namespace, writer: CsvWriter) -> None:
    batch_size = args.batch_size
    api = FollowUpBossApi()
    fetch_count = 0
    failed_count = 0
    first_batch = True
    next_key = None
    while True:
        log.print_ok_blue(f"Fetching people from Follow Up Boss: {fetch_count}")
        try:
            people_response = api.get_people(limit=batch_size, next_key=next_key)
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
        next_key = people_response.get("_metadata", {}).get("next")
        if not next_key:
            break


def main() -> None:
    args = parse_args()

    writer = CsvWriter()

    if args.clean_csv:
        log.print_ok_blue("Cleaning CSV file")
        writer.erase_file(args.output_csv)

    start_time = time.time()
    if args.parallel:
        run_parallel_export(args, writer)
    else:
        run_serial_export(args, writer)

    end_time = time.time()
    log.print_ok_blue(f"Export completed in {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    main()
