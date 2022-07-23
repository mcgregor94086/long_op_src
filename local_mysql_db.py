# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
function:  open_db_connection()

Purpose:

    opens the local MySQL database

Parameters: None

Returns:

   cnx (handle): The handle to the opened database

Description: opens the local MySQL database

Raises: None

Usage:

    cnx = open_db_connection()

Dependencies:

    os -- library for file path construction
    mysql.connector -- library mysql access functions
    datetime -- for datetime time stamps

Inheritance:    None

Testing: TODO: To be determined

    Test for wrong db login credentials, no database, no table, variable name mismatches, variable type mismatches

Warnings: None

Updates:

        Scott McGregor,  modified 22-Nov-2021, Added header documentation

Notes:  None

TO DO:

        None
"""

__author__ = 'Scott McGregor'

import logging
import os
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime


# define default values for new SonaData scan_job records:
email_attachments = ''  # TODO: integrate attachments
photoscene_id = 'undefined'
number_of_images = 18
obj_model_path = 'undefined'
stl_path = 'undefined'
order_form = 'no order form'  # TODO: integrate an order form
default_scan_price = 2.00
cad_price = 0.00
mfg_price = 0.00
shipping_price = 0.00
discounts_and_credits = 0.00
specials_and_adjustments = 0.00
amount_paid = 0.00


def open_db_connection():
    print(f'\n\tENTERING open_db_connection()')
    try:
        cnx = mysql.connector.connect(user='scanner_user', password='Use4Sonautics!',
                                      host='127.0.0.1',
                                      database='sonadata')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("\nSomething is wrong with your user name or password")
            print(f'\tEXITING open_db_connection()\n')
            return False
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("\tDatabase does not exist")
            print(f'\tEXITING open_db_connection()\n')
            return False
        else:
            print(err)
            return False
    else:  # database is open!
        return cnx


# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
function:  create_a_new_scan_record(scan_job_data_record)

Purpose:

    creates a new scan record in the local database.

Parameters: None

Returns:

   scan_job_data_record (dict): the variable keys and their values from the db record saved.

Description: opens the local MySQL database

Raises: None

Usage:

    scan_job_data_record  = create_a_new_scan_record(scan_job_data_record)

Dependencies:

    os -- library for file path construction
    mysql.connector -- library mysql access functions
    datetime -- for datetime time stamps

Inheritance:    None

Testing: Things to keep in mind while testing the program. Special cases to test for.

    Test for wrong db login credentials, no database, no table, variable name mismatches, variable type mismatches

Warnings: None

Updates: 

        Scott McGregor,  modified 22-Nov-2021, Added header documentation

Notes:  None

TO DO:   

        None
"""


def create_a_new_scan_record(scan_job_data_record):
    #                     long_scan_id, scanner_id, short_scan_id, when_created, when_last_updated, status,
    #                     scanner_owner, from_email, to_emails, email_subject, email_body, email_attachments,
    #                     photoscene_id, number_of_images, obj_model_path, stl_path, order_form,
    #                     scan_price, cad_price, mfg_price, shipping_price, discounts_and_credits,
    #                     specials_and_adjustments, total_price, amount_paid, remaining_balance,
    #                     mfg_order_info, cad_order_info, consumer_name, consumer_id):
    logging.debug(f'\nENTERING: create_a_new_scan_record({scan_job_data_record})')
    print(f'\n\tENTERING: create_a_new_scan_record({scan_job_data_record})')
    logging.debug("scan_job_data_record = ", scan_job_data_record)
    connection = False
    try:
        connection = mysql.connector.connect(user='scanner_user',
                                             password='Use4Sonautics!',
                                             host='localhost',
                                             database='sonadata')

        # scanner_id = scan_job_data_record['scanner_id']
        # short_scan_id = scan_job_data_record['short_scan_id']
        # long_scan_id = scan_job_data_record['long_scan_id']
        # when_created = scan_job_data_record['when_created']
        # when_last_updated = scan_job_data_record['when_last_updated']
        # status = scan_job_data_record['status']
        # scanner_owner = scan_job_data_record['scanner_owner']
        # from_email = scan_job_data_record['from_email']
        # to_emails = scan_job_data_record['to_emails']
        # email_subject = scan_job_data_record['email_subject']
        # email_body = scan_job_data_record['email_body']
        # email_attachments = scan_job_data_record['email_attachments']
        # photoscene_id = scan_job_data_record['photoscene_id']
        # number_of_images = scan_job_data_record['number_of_images']
        # obj_model_path = scan_job_data_record['obj_model_path']
        # stl_path = scan_job_data_record['stl_path']
        # order_form = scan_job_data_record['order_form']
        # scan_price = scan_job_data_record['scan_price']
        # cad_price = scan_job_data_record['cad_price']
        # mfg_price = scan_job_data_record['mfg_price']
        # shipping_price = scan_job_data_record['shipping_price']
        # discounts_and_credits = scan_job_data_record['discounts_and_credits']
        # specials_and_adjustments = scan_job_data_record['specials_and_adjustments']
        # total_price = scan_job_data_record['total_price']
        # amount_paid = scan_job_data_record['amount_paid']
        # remaining_balance = scan_job_data_record['remaining_balance']
        # mfg_order_info = scan_job_data_record['mfg_order_info']
        # cad_order_info = scan_job_data_record['cad_order_info']
        # consumer_name = scan_job_data_record['consumer_name']
        # consumer_id = scan_job_data_record['consumer_id']

        logging.debug("creating MySQL INSERT query")
        new_scan_job = ("INSERT INTO scan_history "
                        "(long_scan_id, scanner_id, short_scan_id, when_created, when_last_updated, status, \
                           scanner_owner, from_email, to_emails, email_subject, email_body, email_attachments, \
                           photoscene_id, number_of_images, obj_model_path, stl_path, order_form, \
                           scan_price, cad_price, mfg_price, shipping_price, discounts_and_credits, \
                           specials_and_adjustments, total_price, amount_paid, remaining_balance, \
                           mfg_order_info, cad_order_info, consumer_name, consumer_id) "
                        "VALUES (%(long_scan_id)s, \
                            %(scanner_id)s, \
                            %(short_scan_id)s, \
                            %(when_created)s, \
                            %(when_last_updated)s,\
                            %(status)s, \
                            %(scanner_owner)s, \
                            %(from_email)s, \
                            %(to_emails)s, \
                            %(email_subject)s,\
                            %(email_body)s, \
                            %(email_attachments)s,\
                            %(photoscene_id)s, \
                            %(number_of_images)s,\
                            %(obj_model_path)s, \
                            %(stl_path)s, \
                            %(order_form)s,\
                            %(scan_price)s, \
                            %(cad_price)s, \
                            %(mfg_price)s, \
                            %(shipping_price)s, \
                            %(discounts_and_credits)s, \
                            %(specials_and_adjustments)s,\
                            %(total_price)s, \
                            %(amount_paid)s, \
                            %(remaining_balance)s, \
                            %(mfg_order_info)s, \
                            %(cad_order_info)s, \
                            %(consumer_name)s, \
                            %(consumer_id)s \
                            )"
                        )
        logging.debug("MySQL INSERT query created")
        # Insert new scan job record
        cursor = connection.cursor()
        logging.debug("Executing MySQL INSERT query")
        cursor.execute(new_scan_job, scan_job_data_record)
        logging.debug("Executed MySQL INSERT query")
        connection.commit()
        logging.debug("Committed MySQL INSERT query")
        logging.debug(f"{cursor.rowcount}: A new scan_job record inserted successfully into scan_history table")
        cursor.close()

    except mysql.connector.Error as error:
        # logging.error("MYSQL error", error)
        if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            # logging.error("Something is wrong with the sonadata database username or password")
            # logging.error(f' EXITING 1: create_a_new_scan_record({scan_job_data_record}) RETURNS False\n')
            print(f'\tEXITING 1: create_a_new_scan_record({scan_job_data_record})\n')
            return False

        elif error.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error("\tThe sonadata database does not exist")
            logging.error(f'\tEXITING 2: create_a_new_scan_record({scan_job_data_record}) RETURNS False\n')
            print(f'\tEXITING 2: create_a_new_scan_record({scan_job_data_record}) RETURNS False\n')
            return False

        else:
            logging.error(error)
            logging.error(f"Failed to insert new scan_job record into scan_history table {error}")

            logging.error(f'EXITING 3: create_a_new_scan_record({scan_job_data_record}) RETURNS False\n')
            print(f'\tEXITING 3: create_a_new_scan_record({scan_job_data_record}) RETURNS False\n')
            return False

    finally:
        connection.close()
        logging.debug("MySQL connection (for creating a new scan record) is closed")
    logging.debug(f'EXITING 4: create_a_new_scan_record({scan_job_data_record}) RETURNS False\n')
    print(f'\tEXITING 4: create_a_new_scan_record({scan_job_data_record}) RETURNS False\n')
    return scan_job_data_record


# HEADER BLOCK: See naturaldocs examples and info: http://www.naturaldocs.org/features/output/
"""
function:  def update_scan_record(long_scan_id, key, value)

Purpose:

    UPDATES the value of the field "key" with value "value" WHERE scan_id = long_scan_id

Parameters: None

Returns:

   record (dict): the selected record updated.

Description: UPDATES the value of the field "key" with value "value" WHERE scan_id = long_scan_id

Raises: None

Usage:

    record  = update_scan_record(long_scan_id, key, value)

Dependencies:

    os -- library for file path construction
    mysql.connector -- library mysql access functions
    datetime -- for datetime time stamps

Inheritance:    None

Testing: Things to keep in mind while testing the program. Special cases to test for.

    Test for wrong db login credentials, no database, no table, variable name mismatches, variable type mismatches

Warnings: None

Updates: 

        Scott McGregor,  modified 22-Nov-2021, Added header documentation

Notes:  None

TO DO:   

        None
"""


def update_scan_record(long_scan_id, key, value):
    print(f'\n\tENTERING: update_scan_record("{long_scan_id}", "{key}", "{value}")')

    import mysql.connector
    record = ''
    connection = False
    print("\tBefore updating a db record.")
    try:
        connection = mysql.connector.connect(user='scanner_user', password='Use4Sonautics!',
                                             host='127.0.0.1', database='sonadata',
                                             auth_plugin='mysql_native_password')
        cursor = connection.cursor(buffered=True)

        sql_select_query = "select * from scan_history where long_scan_id = '" + long_scan_id + "'"
        print(f'\tquery = {sql_select_query}')
        cursor.execute(sql_select_query)
        record = cursor.fetchone()
        print(f'\tdb record = {record}')

        # Update single record now
        print("\tRecord Update a record.")
        str_value = str(value)
        sql_update_query = "Update scan_history set " \
                           + key + " = '" + str_value + "'" \
                           + " where long_scan_id = '" + long_scan_id + "'"
        print(f'\tquery = {sql_select_query}')
        cursor.execute(sql_update_query)
        connection.commit()
        print("\tRecord Updated successfully ")

        print("\tAfter updating record ")
        cursor.execute(sql_select_query)
        record = cursor.fetchone()
        print(f'\tdb record = {record}')

    except mysql.connector.Error as error:
        print(f"\tERROR: Failed to update table record: {error}")
    finally:
        connection.close()
        print("\tMySQL connection is closed")
    print("\tDONE updating a db record.")

    print(f'\tEXITING: update_scan_record() RETURNS "{record}"\n')
    return record


if __name__ == '__main__':
    now = datetime.now()

    scanner_id = 'test_scanner'
    short_scan_id = 'test_scan_id'
    long_scan_id_x = os.path.join(scanner_id, short_scan_id)
    when_created = now
    when_last_updated = now
    status = 'test'
    scanner_owner = 'test_owner'
    from_email = 'scott@sonautics.com'
    to_emails = 'scott@sonautics.com'
    email_subject = 'test subject'
    email_body = 'test body'
    # default values for new record

    # the following default values are defined globally above so that they can be included in other functions (in main)
    # from local_mysql_db import email_attachments, photoscene_id, number_of_images, \
    #                   obj_model_path,stl_path, order_form, \
    #                   scan_price, cad_price, mfg_price, shipping_price, discounts_and_credits, \
    #                   specials_and_adjustments, amount_paid

    total_price = default_scan_price + cad_price + mfg_price + shipping_price
    remaining_balance = total_price - amount_paid,
    mfg_order_info = ""
    cad_order_info = ""
    consumer_name = "no consumer name"
    consumer_id = "no consumer id"

    scan_job_data_record_x = {
        'scanner_id': scanner_id,
        'short_scan_id': short_scan_id,
        'long_scan_id': long_scan_id_x,
        'when_created': when_created,
        'when_last_updated': when_last_updated,
        'status': status,
        'scanner_owner': scanner_owner,
        'from_email': from_email,
        'to_emails': to_emails,
        'email_subject': email_subject,
        'email_body': email_body,
        'email_attachments': email_attachments,
        'photoscene_id': photoscene_id,
        'number_of_images': number_of_images,
        'obj_model_path': obj_model_path,
        'stl_path': stl_path,
        'order_form': order_form,
        'scan_price': default_scan_price,
        'cad_price': cad_price,
        'mfg_price': mfg_price,
        'shipping_price': shipping_price,
        'discounts_and_credits': discounts_and_credits,
        'specials_and_adjustments': specials_and_adjustments,
        'total_price': total_price,
        'amount_paid': amount_paid,
        'remaining_balance': remaining_balance,
        'mfg_order_info': mfg_order_info,
        'cad_order_info': cad_order_info,
        'consumer_name': consumer_name,
        'consumer_id': consumer_id,
    }

    create_a_new_scan_record(scan_job_data_record_x)

    key_x = "consumer_info"
    value_x = "updated consumer info"
    print(long_scan_id_x)
    update_scan_record(long_scan_id_x, key_x, value_x)
