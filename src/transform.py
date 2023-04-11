import argparse
import csv
import os

from common import to_datetime, to_str, round_to_5min, write_header


def main():
    parser = argparse.ArgumentParser(description=
        "Transforms data from ZG App into this application's format")
    parser.add_argument('input', type=str, help='ZGApp directorey')
    parser.add_argument('output', type=str, help='output directorey (should be data/)')
    parser.add_argument(
        "-r",
        "--reduce-granularity",
        action="store_true",
        help='Reduce the granularity to 5minutes. Significantly reduces filesizes.',
    )
    args = parser.parse_args()

    transform(args.input, args.output, args.reduce_granularity)


def transform(input: str, output: str, reduce_granularity: bool) -> None:
    # iterate over csv files
    for root, dirs, files in os.walk(input):
        for name in files:
            if not name.lower().endswith(".csv"):
                continue
            full_path = os.path.join(root, name)
            print("Reading " + full_path)

            # get year, month, and day
            day = name.split(".")[0]
            root_1, month = os.path.split(root)
            _, year = os.path.split(root_1)

            # read zg file and do some transforming
            data = []
            with open(full_path, "r") as f:
                reader = csv.reader(f, delimiter=",")
                for count, row in enumerate(reader):
                    if count == 0:
                        continue
                    parsed_datetime = to_datetime(f"{year}-{month}-{day} {row[0]}")

                    # Reduce granularity. Round down to the nearest 5 minutes.
                    # Skip this row if there is already a datapoint for that time.
                    rounded_datetime = round_to_5min(parsed_datetime)
                    if to_str(rounded_datetime) in [d[0] for d in data]:
                        continue
                    
                    data.append((to_str(rounded_datetime), row[1], row[2]))

            # write new file
            new_filename = f"{year}-{month}-{day}.csv"
            new_full_path = os.path.join(output, new_filename)
            with open(new_full_path, "w") as f:
                write_header(f)
                csv_writer = csv.writer(f, delimiter=",")
                for row in data:
                    csv_writer.writerow(row)
                

if __name__ == "__main__":
    main()
