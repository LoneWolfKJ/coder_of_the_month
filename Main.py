import csv
import json
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import Scrapper
from User import User
from utils import *

with open('./config.json') as config_file:
    config = json.load(config_file)
    initialize_logger(config["log_file_path"])
    scope = config["spreadsheet_scope"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(config["creds_file_path"], scope)
    gc = gspread.authorize(credentials)
    spreadsheet_key = config["spreadsheet_key"]
    data_sheet_name = config["data_sheet_name"]
    date_sheet_name = config["date_sheet_name"]
    result_sheet_name = config["result_sheet_name"]
    spreadsheet = gc.open_by_key(spreadsheet_key)
    logging.info("spreadsheet -> {}".format(spreadsheet))
    data_sheet = spreadsheet.worksheet(data_sheet_name)
    user_db = data_sheet.get_all_records()
    sheet_cols = config["sheet_columns"]
"""Can pass how many months after/before which you want to calculate results for"""
start_date, end_date = get_date_from_string(config["start_date"]), get_date_from_string(config["end_date"])
logging.info("Start {} End {}".format(start_date,end_date))
cf_scrapper = Scrapper.CF_Scrapper()
cc_scrapper = Scrapper.CC_Scrapper()
cf_scrapper.scrape_contests(start_date, end_date)
cc_scrapper.scrape_contests(start_date, end_date)

user_list = []
for entry in user_db:
    user = User(entry['Name'], entry['Email address'], entry["Batch"],
                entry['Profile Picture (To be Displayed on ACM Website)'],
                entry["Codeforces ID ( your username in codeforces)"], entry['Codechef ID (your username on codechef)'])
    if user.cf_id != "NA" and cf_scrapper.cf_contest != {}:
        cf_scrapper.scrape_user_submissions(user)
    if user.cc_id != "NA" and cc_scrapper.cc_contest != {}:
        cc_scrapper.scrape_user_submissions(user)
    user.get_total_sol()
    print_bold(f'{user.name} CF: {user.cf_sol} CC: {user.cc_sol} Total: {user.get_total_sol()}')
    user_list.insert(len(user_list), user)
sorted_list = sorted(user_list, key=lambda user: user.total_sol, reverse=True)
with open('result.csv', 'w') as r:
    label = ['name', 'email', 'Batch', 'CodeForces', 'CodeChef', 'Total', 'imageURL']
    csv_writer = csv.writer(r)
    csv_writer.writerow(label)
    for u in sorted_list:
        csv_writer.writerow([u.name, u.email, u.batch, u.cf_sol, u.cc_sol, u.total_sol, u.profile_url])

results_sheet = spreadsheet.worksheet(result_sheet_name)
print_info("Clearing current data from sheet")
results_sheet.clear()
print_info("Waiting for upload to complete")
spreadsheet.values_update(
    result_sheet_name,
    params={'valueInputOption': 'USER_ENTERED'},
    body={'values': list(csv.reader(open('./result.csv')))}
)

date_sheet = spreadsheet.worksheet(date_sheet_name)
date_sheet.update('A2', datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
date_sheet.update('B2', start_date.strftime('%Y-%m-%d %H:%M:%S.%f'))
date_sheet.update('C2', end_date.strftime('%Y-%m-%d %H:%M:%S.%f'))

# Wait 3 seconds to ensure the data upload is complete
time.sleep(3)
print_success("Uploaded data to the sheet")
