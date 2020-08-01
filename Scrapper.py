import datetime
import json
import logging
import time
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse

from utils import print_info, print_fail


class CF_Scrapper:

    def __init__(self):
        self.cf_contest = {}

    def scrape_contests(self, start_date, end_date):
        try:
            with urlopen("http://codeforces.com/api/contest.list?gym=false&format=json") as response:
                source = response.read()
                source = source.decode('utf-8').encode('cp850', 'replace').decode('cp850')
                data = json.loads(source)  # json.loads() creates dictionary from json data
                # js = json.dumps(data, indent=2) #json.dumps() creates a string from dict i.e dict to json
                # converdion in python
                for contest in data['result']:
                    if contest['phase'] == 'FINISHED':
                        # print(contest)
                        date = datetime.datetime.fromtimestamp(contest['startTimeSeconds'])
                        if start_date <= date <= end_date:
                            self.cf_contest[contest['id']] = date
                print_info(f'{self.cf_contest}')
        except Exception as e:
            logging.exception("Exception raised {}".format(e))

    def scrape_user_submissions(self, user):
        cfLink = user.cf_url
        cfid = user.cf_id
        # print(cfLink, cfid)
        try:
            response = requests.get(f'https://codeforces.com/contests/with/{cfid}')
            if response.status_code != 200:
                logging.error("Failed scrapping cf for user {} with id {}".format(user, user.cf_id))
            source = response.text
            soup = BeautifulSoup(source, 'lxml')
            soup = soup.decode('utf-8').encode('cp850', 'replace').decode('cp850')
            soup = BeautifulSoup(soup, 'lxml')
            # Looping over all contests participated by user in cf
            for tr in soup.find('div', class_='datatable').tbody.find_all('tr'):
                # cflist contain details related to user-contest in cf
                cflist = []
                # Extracting codeforces contestid
                str = tr.a.attrs['href'].split('/')
                cflist.insert(len(cflist), str[2])
                for td in tr.find_all('td'):
                    cflist.insert(len(cflist), td.text.strip())
                if int(cflist[0]) in self.cf_contest:
                    user.cf_sol += int(cflist[4])
        except Exception as e:
            logging.exception("Exception {} for user {} with id {}".format(e, user, user.cf_id))


class CC_Scrapper:

    def __init__(self):
        self.cc_contest = {}

    def scrape_contests(self, start_date, end_date):
        try:
            response = requests.get('https://www.codechef.com/contests')
            if response.status_code != 200:
                logging.error("Failed Scrapping cc for contests")
                logging.info("Response {}".format(response))
                logging.info("Retrying in 5 seconds")
                time.sleep(5)
                response = requests.get('https://www.codechef.com/contests')
                logging.info("2nd attempt Response {}".format(response))
                if response.status_code != 200:
                    print_fail("Failed to get cc contests")
                    logging.info("2nd attempt FAILED")
            source = response.text
            soup = BeautifulSoup(source, 'lxml')
            soup = soup.find('div', class_='content-wrapper')
            soup = soup.find_all('div')[4]
            for i in soup.tbody.find_all('tr'):
                clist = []
                for j in i.find_all('td'):
                    clist.insert(len(clist), j.text)
                try:
                    contest_type = clist[1].split(' ')[1]
                    contest_end_time = parse(clist[2])
                    if (start_date <= contest_end_time <= end_date) and (
                            contest_type == "Challenge" or contest_type == "Cook-Off" or contest_type == "Lunchtime"):  # considering the required contests to be of the format <month name> <contest type> <year>
                        print_info(f'{clist}')
                        self.cc_contest[clist[0]] = clist[1]
                except Exception as e:
                    pass
        except Exception as e:
            logging.exception("Exception raised {}".format(e))

    def scrape_user_submissions(self, user):
        ccLink = user.cc_url
        ccid = user.cc_id
        # print(ccLink, ccid)
        try:
            response = requests.get(f'https://www.codechef.com/users/{ccid}')
            if response.status_code != 200:
                logging.error("Failed Scrapping cc for user {} with id {}".format(user, user.cc_id))
                logging.info("Response {}".format(response))
                logging.info("Retrying in 5 seconds")
                time.sleep(5)
                response = requests.get(f'https://www.codechef.com/users/{ccid}')
                logging.info("2nd attempt for user {} response {}".format(ccid, response))
                if response.status_code != 200:
                    print_fail("Failed for user {} with id {}".format(user.name, ccid))
                    logging.info("2nd attempt FAILED")
            source = response.text
            soup = BeautifulSoup(source, 'lxml')
            soup = soup.decode('utf-8').encode('cp850', 'replace').decode('cp850')
            soup = BeautifulSoup(soup, 'lxml')
            soup = soup.find('section', class_='rating-data-section problems-solved').article
            for p in soup.find_all('p'):
                cclist = [p.text.strip().split(":")]
                for c in cclist:
                    if self.cc_contest.get(c[0]) is not None or self.cc_contest.get(c[0][:-1]) is not None:
                        # print(c[0] + " = ", end='')
                        # print(len(c[1].split(',')))
                        user.cc_sol += len(c[1].split(','))
        except Exception as e:
            logging.exception("Exception {} for user {} with id {}".format(e, user, user.cc_id))
