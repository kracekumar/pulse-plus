import click
import rich
from rich.console import Console
from pathlib import Path
from sqlite_utils import Database
import sqlite3
import datetime
from dateutil.relativedelta import relativedelta
import json


error_console = Console(stderr=True, style="bold red")
info_console = Console(style="black green")
print = info_console.print
error_print = error_console.print


TABLE_NAMES = {
    "aggregated_transaction": "aggregated_transaction",
    "aggregated_user": "aggregated_user",
    "aggregated_user_device": "aggregated_user_device",
    "top_transaction": "top_transaction",
    "top_user": "top_user",
}


# Tables


def create_tables(db):
    # TODO: Create common base dict fields
    aggregated_user_fields = {
        "id": int,
        "aggregated_by": str,
        "aggregate_name": str,
        "year": int,
        "users": int,
        "app_opens": int,
        "start_date": datetime.date,
        "end_date": datetime.date,
    }
    aggregated_user_device_fields = {
        "id": int,
        "aggregated_by": str,
        "aggregate_name": str,
        "year": int,
        "start_date": datetime.date,
        "end_date": datetime.date,
        "brand": str,
        "count": int,
        "percentage": float,
    }
    aggregated_transaction_fields = {
        "id": int,
        "aggregated_by": str,
        "aggregate_name": str,
        "year": int,
        "start_date": datetime.date,
        "end_date": datetime.date,
        "name": str,
        "type": str,
        "count": int,
        "amount": float,
    }
    top_user_fields = {
        "id": int,
        "aggregated_by": str,
        "aggregate_name": str,
        "year": int,
        "start_date": datetime.date,
        "end_date": datetime.date,
        "name": str,
        "type": str,
        "registered_users": int,
    }
    top_transaction_fields = {
        "id": int,
        "aggregated_by": str,
        "aggregate_name": str,
        "year": int,
        "start_date": datetime.date,
        "end_date": datetime.date,
        "entity_name": str,
        "entity_type": str,
        "type": str,
        "count": int,
        "amount": float,
    }
    for name, fields in (
        ("aggregated_user", aggregated_user_fields),
        ("aggregated_user_device", aggregated_user_device_fields),
        ("aggregated_transaction", aggregated_transaction_fields),
        ("top_user", top_user_fields),
        ("top_transaction", top_transaction_fields),
    ):
        table = TABLE_NAMES[name]
        try:
            if name == "top_transaction":
                non_null_fields = set(fields.keys())
                non_null_fields.remove("entity_name")
                db[table].create(
                    fields, pk="id", not_null=non_null_fields
                )
            else:
                db[table].create(fields, pk="id", not_null=set(fields.keys()))
            print(f"{table} table created")
        except sqlite3.OperationalError:
            error_print(f"{table} already exists. Skipping table creation")


def get_db(name):
    return Database(name)


def is_state(name):
    return "state" in str(name)


def get_date_range(name, year):
    """Get date range for the file."""
    if name == "1.json":
        start_date = datetime.date(year=year, month=1, day=1)
    elif name == "2.json":
        start_date = datetime.date(year=year, month=4, day=1)
    elif name == "3.json":
        start_date = datetime.date(year=year, month=7, day=1)
    elif name == "4.json":
        start_date = datetime.date(year=year, month=10, day=1)
    return {
        "start_date": start_date,
        "end_date": start_date + relativedelta(months=+3, days=-1),
    }


def get_aggregated_user_from_file(path):
    data = json.load(open(path))["data"]
    return {
        "users": data["aggregated"]["registeredUsers"],
        "app_opens": data["aggregated"]["appOpens"],
    }


def get_aggregated_user_device_from_file(path):
    data = json.load(open(path))["data"]["usersByDevice"]
    return [
        {
            "brand": datum["brand"],
            "count": datum["count"],
            "percentage": datum["percentage"],
        }
        for datum in data
    ]


def get_aggregated_transaction_from_file(path):
    data = json.load(open(path))["data"]
    data = data["transactionData"]
    return [
        {
            "name": datum["name"],
            "type": datum["paymentInstruments"][0]["type"],
            "count": datum["paymentInstruments"][0]["count"],
            "amount": datum["paymentInstruments"][0]["amount"],
        }
        for datum in data
    ]


def get_top_user_from_file(path):
    data = json.load(open(path))["data"]
    keys = ["states", "pincodes", "districts"]
    to_return = []
    for key in keys:
        if data[key] is None:
            continue
        for item in data[key]:
            to_return.append(
                {
                    "name": item["name"],
                    "registered_users": item["registeredUsers"],
                    "type": key,
                }
            )
    return to_return


def get_top_transaction_from_file(path):
    data = json.load(open(path))["data"]
    keys = ["states", "pincodes", "districts"]
    to_return = []
    for key in keys:
        if data[key] is None:
            continue
        for item in data[key]:
            to_return.append(
                {
                    "entity_name": item["entityName"],
                    "count": item["metric"]["count"],
                    "amount": item["metric"]["amount"],
                    "type": item["metric"]["type"],
                    "entity_type": key,
                }
            )
    return to_return


def extract_aggregated_user_rows(path):
    start_path = path / Path("aggregated/user/country/india/")
    all_data = []
    # TODO: Facepalm, use bloody recursion
    for directory in start_path.iterdir():
        if is_state(directory):
            for state in directory.iterdir():
                for year_dir in state.iterdir():
                    for data_file in year_dir.iterdir():
                        year = int(year_dir.name)
                        defaults = {
                            "year": year,
                            "aggregated_by": "state",
                            "aggregate_name": state.name,
                        }
                        defaults.update(get_date_range(name=data_file.name, year=year))
                        record = get_aggregated_user_from_file(data_file)
                        record.update(defaults)
                        all_data.append(record)
        else:
            year = int(directory.name)
            for data_file in directory.iterdir():
                defaults = {
                    "year": year,
                    "aggregated_by": "country",
                    "aggregate_name": "india",
                }
                defaults.update(get_date_range(name=data_file.name, year=year))
                record = get_aggregated_user_from_file(data_file)
                record.update(defaults)
                all_data.append(record)
    return all_data


def extract_aggregated_user_device_rows(path):
    start_path = path / Path("aggregated/user/country/india/")
    all_data = []
    # TODO: Facepalm, use bloody recursion
    for directory in start_path.iterdir():
        if is_state(directory):
            for state in directory.iterdir():
                for year_dir in state.iterdir():
                    for data_file in year_dir.iterdir():
                        year = int(year_dir.name)
                        defaults = {
                            "year": year,
                            "aggregated_by": "state",
                            "aggregate_name": state.name,
                        }
                        defaults.update(get_date_range(name=data_file.name, year=year))
                        records = get_aggregated_user_device_from_file(data_file)
                        [record.update(defaults) for record in records]
                        all_data.extend(records)
        else:
            year = int(directory.name)
            for data_file in directory.iterdir():
                defaults = {
                    "year": year,
                    "aggregated_by": "country",
                    "aggregate_name": "india",
                }
                defaults.update(get_date_range(name=data_file.name, year=year))
                records = get_aggregated_user_device_from_file(data_file)
                [record.update(defaults) for record in records]
                all_data.extend(records)
    return all_data


def extract_aggregated_transaction_rows(path):
    start_path = path / Path("aggregated/transaction/country/india/")
    all_data = []
    # TODO: Facepalm, use bloody recursion
    for directory in start_path.iterdir():
        if is_state(directory):
            for state in directory.iterdir():
                for year_dir in state.iterdir():
                    for data_file in year_dir.iterdir():
                        year = int(year_dir.name)
                        defaults = {
                            "year": year,
                            "aggregated_by": "state",
                            "aggregate_name": state.name,
                        }
                        defaults.update(get_date_range(name=data_file.name, year=year))
                        records = get_aggregated_transaction_from_file(data_file)
                        [record.update(defaults) for record in records]
                        all_data.extend(records)
        else:
            year = int(directory.name)
            for data_file in directory.iterdir():
                defaults = {
                    "year": year,
                    "aggregated_by": "country",
                    "aggregate_name": "india",
                }
                defaults.update(get_date_range(name=data_file.name, year=year))
                records = get_aggregated_transaction_from_file(data_file)
                [record.update(defaults) for record in records]
                all_data.extend(records)
    return all_data


def extract_top_user_rows(path):
    start_path = path / Path("top/user/country/india/")
    all_data = []
    # TODO: Facepalm, use bloody recursion
    for directory in start_path.iterdir():
        if is_state(directory):
            for state in directory.iterdir():
                for year_dir in state.iterdir():
                    for data_file in year_dir.iterdir():
                        year = int(year_dir.name)
                        defaults = {
                            "year": year,
                            "aggregated_by": "state",
                            "aggregate_name": state.name,
                        }
                        defaults.update(get_date_range(name=data_file.name, year=year))
                        records = get_top_user_from_file(data_file)
                        [record.update(defaults) for record in records]
                        all_data.extend(records)
        else:
            year = int(directory.name)
            for data_file in directory.iterdir():
                defaults = {
                    "year": year,
                    "aggregated_by": "country",
                    "aggregate_name": "india",
                }
                defaults.update(get_date_range(name=data_file.name, year=year))
                records = get_top_user_from_file(data_file)
                [record.update(defaults) for record in records]
                all_data.extend(records)
    return all_data


def extract_top_transaction_rows(path):
    start_path = path / Path("top/transaction/country/india/")
    all_data = []
    # TODO: Facepalm, use bloody recursion
    for directory in start_path.iterdir():
        if is_state(directory):
            for state in directory.iterdir():
                for year_dir in state.iterdir():
                    for data_file in year_dir.iterdir():
                        year = int(year_dir.name)
                        defaults = {
                            "year": year,
                            "aggregated_by": "state",
                            "aggregate_name": state.name,
                        }
                        defaults.update(get_date_range(name=data_file.name, year=year))
                        records = get_top_transaction_from_file(data_file)
                        [record.update(defaults) for record in records]
                        all_data.extend(records)
        else:
            year = int(directory.name)
            for data_file in directory.iterdir():
                defaults = {
                    "year": year,
                    "aggregated_by": "country",
                    "aggregate_name": "india",
                }
                defaults.update(get_date_range(name=data_file.name, year=year))
                records = get_top_transaction_from_file(data_file)
                [record.update(defaults) for record in records]
                all_data.extend(records)
    return all_data


def insert_data(directory: Path, db):
    for name, all_data in [
        ("aggregated_user_device", extract_aggregated_user_device_rows(directory)),
        ("aggregated_user", extract_aggregated_user_rows(directory)),
        ("aggregated_transaction", extract_aggregated_transaction_rows(directory)),
        ("top_user", extract_top_user_rows(directory)),
        ("top_transaction", extract_top_transaction_rows(directory)),
    ]:
        table = TABLE_NAMES[name]
        db[table].insert_all(all_data)
        print(f"Inserted {db[table].count} records in {table}")


# Commands


@click.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--output", default="pulse.db", type=click.Path())
def create_db(directory, output):
    db_path = Path(output)

    if db_path.exists():
        error_console.print(
            f"{output} location exists. Give a different location or delete the file"
        )
        exit(-1)

    db = get_db(output)
    create_tables(db)
    data_dir = Path(directory)
    insert_data(data_dir, db)
    print(f"{output} created")


if __name__ == "__main__":
    create_db()
