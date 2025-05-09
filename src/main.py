import re
import json
import argparse


def parse_csv(fields: str) -> list[str]:
    res = []
    if fields:
        res.extend(fields.split(','))
        res[-1] = res[-1].rstrip()
    else:
        print('Line is empty.')
    return res


def populate_fields(fields: list[str], data: list[str]) -> dict:
    res = {}
    for field, val in zip(fields, data):
        res[field] = val
    return res


def read_csv(file_path: str) -> list[dict]:
    output = []
    try:
        with open(file_path) as file:
            fields = parse_csv(file.readline())
            for line in file:
                data = parse_csv(line)
                output.append(populate_fields(fields, data))    
    except Exception:
        print('No such file or directory.')

    return output


def calculate_payout(pattern: str, employe: dict) -> int:
    hours, rate = 0, 0
    try:
        field = search_for_field(pattern, employe)
        hours = int(employe['hours_worked'])
        rate = int(employe[field])
    except KeyError:
        print('Rate field is missing.')
    except ValueError:
        print('Invalid field type.')
    return hours * rate


def search_for_field(pattern: str, employe: dict) -> str:
    res = ''
    for field in employe.keys():
        match = re.search(pattern, field)
        if match:
            res += match.group(0)
    return res


def write_to_json(path: str, employees: list[dict]) -> None:
    with open(path, 'w') as file:
        json.dump(employees, file, indent=4)


def main():
    employees = []
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='+', help='path to a csv file')
    parser.add_argument('--report', help='report name')
    args = parser.parse_args()

    for file in args.filenames:
        employees.extend(read_csv(file))

    if args.report == 'payout':
        for employe in employees:
            payout = calculate_payout(r'hourly_rate|rate|salary', employe)
            employe[args.report] = payout
        
    if employees:
        write_to_json('output.json', employees)


if __name__ == '__main__':
    main()
