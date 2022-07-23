import os
from datetime import datetime
from pathlib import Path


def get_scan_id(scanner_id, scanner_dir):
    """
    This is the function that generates a new unique scan_id based on the current date time
    :param scanner_id:
    :param scanner_dir:
    :return: scan_id,long_scan_id, scan_dir
    """
    ################################################################################################################
    #  create a new scan_id
    ################################################################################################################
    short_scan_id = datetime.today().strftime('%Y%m%d%H%M%S')
    scan_dir = os.path.join(scanner_dir, short_scan_id)
    long_scan_id = os.path.join(scanner_id, short_scan_id)
    try:
        oldumask = os.umask(0)
        os.makedirs(scan_dir, mode=0o770, exist_ok=True)
    finally:
        os.umask(oldumask)
    return short_scan_id, long_scan_id, scan_dir


if __name__ == '__main__':  # Use this for Unit testing
    print("Testing get_serial_number()")
    serial_number = get_serial_number()
    print('serial_number=', serial_number)
