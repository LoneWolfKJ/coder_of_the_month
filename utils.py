import calendar
import logging
import os
import pathlib
import sys
from datetime import datetime

from dateutil.relativedelta import relativedelta


def initialize_logger(log_file_path: str) -> None:
    pathlib.Path(os.path.dirname(log_file_path)).mkdir(parents=True, exist_ok=True)
    format_str = '%(asctime)s:%(threadName)-11s:%(levelname)-8s:%(filename)-15s:' '%(funcName)s:%(lineno)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    file_handler = logging.FileHandler(filename=log_file_path)
    handlers = [file_handler]
    logging.basicConfig(level=logging.INFO, format=format_str, datefmt=date_format, handlers=handlers)


def get_date_from_string(date_string: str):
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")


def get_start_and_end_date(number_of_months=0):
    """
    :param number_of_months: By Default 0 ( current month )
    :return start_date, end_date:
    """
    current_date = datetime.utcnow()
    logging.info("Current Date -> {}".format(current_date))
    if number_of_months >= 0:
        start_date = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_date += relativedelta(months=number_of_months)
        end_date = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1], hour=23,
                                        minute=59, second=59, microsecond=0)
    else:
        end_date = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1], hour=23,
                                        minute=59, second=59, microsecond=59)
        current_date += relativedelta(months=number_of_months)
        start_date = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    logging.info("Start date {}, End Date {}".format(start_date, end_date))
    return start_date, end_date


def print_fail(message: str, end='\n'):
    """Bold Red"""
    sys.stderr.write('\x1b[1;31m' + message.strip() + '\x1b[0m' + end)


def print_success(message: str, end='\n'):
    """Bold Green"""
    sys.stdout.write('\x1b[1;32m' + message.strip() + '\x1b[0m' + end)


def print_warning(message: str, end='\n'):
    """Bold Yellow"""
    sys.stderr.write('\x1b[1;33m' + message.strip() + '\x1b[0m' + end)


def print_info(message: str, end='\n'):
    """Bold Blue"""
    sys.stdout.write('\x1b[1;34m' + message.strip() + '\x1b[0m' + end)


def print_bold(message: str, end='\n'):
    """Bold White"""
    sys.stdout.write('\x1b[1;37m' + message.strip() + '\x1b[0m' + end)
