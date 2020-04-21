import argparse
import re
import os
import sys
import datetime
import csv
import json


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--date", type=str, nargs="+",
        help="regex to match dates (YYYY-MM-DD)",
    )
    parser.add_argument(
        "-p", "--place-id", type=str, nargs="+",
        help="regex to match place_ids",
    )
    parser.add_argument(
        "-f", "--format", type=str, default="csv",
        help="""
        csv: export regular excel-style CSV table
        elasticsearch: export directly into ElasticSearch API
        """,
    )
    parser.add_argument(
        "-o", "--output", type=str, default="-",
        help="Export filename or - for stdout",
    )

    return parser.parse_args()


class RegexFilter:

    def __init__(self, *regex):
        self.expressions = []
        for r in regex:
            if isinstance(r, str):
                r = re.compile(r)
            self.expressions.append(r)

    def matches(self, text):
        for r in self.expressions:
            for i in r.finditer(text):
                return True
        return False


def export_rows(place_ids, rows, format, fp):
    if format == "csv":
        writer = csv.DictWriter(fp, ["timestamp"] + sorted(place_ids))
        writer.writeheader()
        writer.writerows(rows)

    elif format == "elasticsearch":
        from elastic.elastic import export_elastic
        export_elastic(load_meta(), place_ids, rows)

    else:
        print(f"Unsupported format '{format}'")


def export(date_filter, place_filter, output_filename, format, csv_path="./csv"):
    filenames = []
    for root, dirs, files in os.walk(csv_path):
        for fn in files:
            if fn.endswith(".csv"):
                try:
                    dt = datetime.datetime.strptime(fn[:10], "%Y-%m-%d").date()
                    if date_filter.matches(str(dt)):
                        filenames.append(os.path.join(root, fn))
                except ValueError:
                    pass

    all_rows = []
    all_places = set()
    for fn in sorted(filenames):
        with open(fn, "r") as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                filtered_row = {
                    key: value
                    for key, value in row.items()
                    if key == "timestamp" or place_filter.matches(key)
                }
                all_rows.append(filtered_row)
                for key in filtered_row:
                    if key != "timestamp":
                        all_places.add(key)

    if output_filename == "-":
        export_rows(all_places, all_rows, format, sys.stdout)
    else:
        with open(output_filename, "wt") as fp:
            export_rows(all_places, all_rows, format, fp)


def load_meta():
    place_map = dict()
    with open("./meta-data.csv") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            place_map[row["place_id"]] = row
    return place_map


if __name__ == "__main__":

    args = parse_args()

    if args.date:
        date_filter = RegexFilter(*args.date)
    else:
        date_filter = RegexFilter(r".*")

    if args.place_id:
        place_filter = RegexFilter(*args.place_id)
    else:
        place_filter = RegexFilter(r".*")

    export(date_filter, place_filter, args.output, args.format)
