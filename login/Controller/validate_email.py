import unirest
import tldextract
import datetime
import time, os, csv
import itertools
from login.models import Search_details
from multiprocessing import Lock, Process, Queue, current_process, Manager, Pool
# from helper import *
RUN_ID = "002"
DATE_PULLED = datetime.datetime.now()

WRITEOUT_ORDER = ['first_name', 'last_name', 'name', 'company', 'company_url', 'email_guess', 'email_score']
MAILBOX_API = "333e2a9a897eeba9ad3204f3c007ca10"
dir_path = os.path.dirname(os.path.realpath(__file__))


def emailGenerator(name, company_url):
    """Creates list of emails from person's name and company domain"""
    # guess email domain name
    ext = tldextract.extract(company_url)
    email_domain = "@" + ext.registered_domain

    # get first name, last name, etc
    first_name = name.split(" ")[0].lower()
    first_initial = first_name[0]
    last_name = name.split(" ")[1].lower()
    last_initial = last_name[0]

    # create priority list for guessing emails
    email_guess_list = [first_name + "." + last_name + email_domain,
                        last_name + "." + first_name + email_domain,
                        first_initial + last_name + email_domain,
                        first_name + last_name + email_domain,
                        first_name + "_" + last_name + email_domain,
                        last_name + "_" + first_name + email_domain,
                        first_initial + "." + last_name + email_domain,
                        last_initial + "." + first_name + email_domain,
                        last_name + first_name + email_domain,
                        first_name + last_initial + email_domain,
                        last_name + first_initial + email_domain,
                        last_initial + first_name + email_domain,
                        first_name + email_domain,
                        last_name + email_domain,
                        first_initial + email_domain]

    return email_guess_list


def emailVerifyMailbox(email):
    url = "https://apilayer.net/api/check?access_key=" + MAILBOX_API + "&email=" + email
    response = unirest.get(url,
                           headers={
                               "X-Mashape-Key": MAILBOX_API,
                               "Accept": "application/json"
                           })
    email_dict = {}
    email_dict["email"] = email
    email_dict["alternative_emails"] = response.body["did_you_mean"]
    email_dict["score"] = response.body["score"]

    return email_dict


def worker(person):
    print "inside workerrr"
    try:
        person_dict = {}
        person_dict["first_name"] = person[0]
        person_dict["last_name"] = person[1]
        person_dict["name"] = person_dict["first_name"] + " " + person_dict["last_name"]
        # person_dict["email_original"] = person[3]
        person_dict["company_url"] = person[3]
        print(person_dict["company_url"])

        # get ordered priority list of email permutations
        email_guess_list = emailGenerator(person_dict["name"], person_dict["company_url"])

        # verify all the emails using API
        email_ver_list = []
        for email_guess in email_guess_list:
            email_ver = emailVerifyMailbox(email_guess)
            email_ver_list.append(email_ver)
            if email_ver["score"] >= .95:
                print("break")
                print
                break

        # choose the most valid emails by finding max validity scores provided by API
        max_score = 0
        max_email_list = []
        for i in range(len(email_ver_list)):
            if email_ver_list[i]["score"] > max_score:
                max_score = email_ver_list[i]["score"]
                max_email_list = [email_ver_list[i]]
            elif email_ver_list[i]["score"] == max_score:
                max_email_list.append(email_ver_list[i])

        # when validity scores are the same, choose email that is highest on the priority list
        max_email = max_email_list[0]

        # add email with max validity scores to person dictionary
        person_dict["email_guess"] = max_email["email"]
        person_dict["email_score"] = max_email["score"] * 100

        # write out n/a for any column not scraped
        for i in range(len(WRITEOUT_ORDER)):
            if not person_dict.get(WRITEOUT_ORDER[i]):
                person_dict[WRITEOUT_ORDER[i]] = "N/A"

        # push to database
        # save_rows(person_dict, RUN_ID, DATE_PULLED)
        print(person_dict, RUN_ID, DATE_PULLED,"********************************************************")
        time.sleep(2)
        return [person_dict]
    except Exception, e:
        print e
        return [['Failed'] + person]


def run(file_name, process_count=1):
    # read in csv
    # file_name = "/input.csv"
    print file_name, "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
    queued_rows = read_csv(file_name)[0:5]
    print(queued_rows), "88888888888888888888888888888888888888888888888"

    # multithreading
    current_rows = queued_rows
    queued_rows = []
    pool = Pool(processes=process_count)
    # print queued_rows
    processed_rows = pool.map(worker, current_rows)
    pool.close()
    pool.join()
    processed_rows = list(itertools.chain.from_iterable(filter(None, processed_rows)))
    print(processed_rows),"////////////////////////////////////////////////////////////////////"
    print(len(processed_rows))
    return processed_rows
    # write out csv with sorted order
    file_name = "results.csv"
    # download_final_results(RUN_ID, file_name, WRITEOUT_ORDER)
    # print("Downloaded file")


def max_elements(seq):
    """Return list of max and position(s) of max element"""
    m = max(seq)
    elements = [i for i, j in enumerate(seq) if j == m]
    return [m].append(elements)


def read_csv(local_path):

    with open(local_path, 'rb') as f:
        reader = csv.reader(f)
        read_list = list(reader)
        return read_list[1:len(read_list)]


def write_dict(database, order, file_name):
    # write out each dictionary as a row
    with open(file_name, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, order, extrasaction='ignore')
        dict_writer.writeheader()
        dict_writer.writerows(database)


def dedupe_list_of_lists(list_of_lists):
    list_set = set(map(tuple, list_of_lists))
    list_of_lists = map(list, list_set)
    return list_of_lists


def download_final_results(run_id, file_name, order):
    # finished_rows = Emailvalidation.select().where(Emailvalidation.run == run_id)
    # finished_rows = [[person.run,
    #                   person.date_pulled,
    #                   person.first_name,
    #                   person.last_name,
    #                   person.name,
    #                   person.company,
    #                   person.company_url,
    #                   person.email_guess,
    #                   person.email_score] for person in finished_rows]
    finished_rows = dedupe_list_of_lists(order)

    with open(file_name, 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        headers = ["run", "date_pulled"] + order
        a.writerow(headers)
        a.writerows(finished_rows)


def select_type(data_dict):
    if len(data_dict) > 5:
        # run()
        print('csv')
    else:
        processed_rows = (worker(data_dict))
        print(processed_rows), "ppppppppppppppppppppppppppppppppppppppppppp"

        # processed_rows = list(itertools.chain.from_iterable(filter(None, processed_rows)))
        # print(processed_rows)
        return processed_rows

        # worker(data_dict)
        # if __name__ == "__main__":
        # run()
