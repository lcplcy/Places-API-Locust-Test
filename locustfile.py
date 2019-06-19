
from locust import HttpLocust, TaskSet, task
import csv
import random
import requests
import urllib.parse
#requests.packages.urllib3.disable_warnings() 

AMAP_CLIENT_ID = "xxx"
AMAP_CLIENT_SECRET = "yyy"

FOURSQUARE_CLIENT_ID = "XXX"
FOURSQUARE_CLIENT_SECRET = "YYY"

fsq_url = "venues/search?client_id=%s&client_secret=%s&v=20190501&"

PARAMS = []
CATEGORIES = []
QUERIES = []
AMAPLOGS = []
class APICall(TaskSet):
    final_search_url = ""
    final_old_search_url = ""

    @task
    def gen_random_param(self):
        params = {}
        cat = {}
        query = []
        num_queries = 3
        search_url = fsq_url  % (AMAP_CLIENT_ID, AMAP_CLIENT_SECRET)
        old_search_url = fsq_url  % (FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET)
        
        if len(PARAMS) > 0:
            num_params = len(PARAMS)
            random_param_index = random.randint(0,num_params-1)
            params = PARAMS[random_param_index]
            random_radius = str(random.randint(50,100000))
            random_limit = str(50)
            if len(CATEGORIES) > 0:
                num_cat = len(CATEGORIES)
                random_cat_index = random.randint(0,num_cat-1)
                cat = CATEGORIES[random_cat_index]
            if len(QUERIES) > 0:
                num_queries = len(QUERIES)
                for i in range(num_queries):
                    random_qry_index = random.randint(0,num_queries-1)
                    query.append(QUERIES[random_qry_index])
        
        # Pull logs provided by aMaps to simulate user queries
        log = {}
        if len(AMAPLOGS) > 0:
            num_logs = len(AMAPLOGS)
            random_log_index = random.randint(0,num_logs-1)
            log = AMAPLOGS[random_log_index]

        # from amaps logs - with query params, using CY FSQ KEY
        old_search_url = old_search_url + log["request"]
        self.final_old_search_url = old_search_url

        # from random LL, random radius, limit=50, using AMAP FSQ key
        search_url = fsq_url  % (AMAP_CLIENT_ID, AMAP_CLIENT_SECRET)
        search_url = search_url + "&ll=" + params["ll"] + "&radius=" + random_radius + "&limit=" + random_limit

        self.final_search_url = search_url
        
        # Generate a random number, to decide if new infra/old infra to be called
        # Change the number in the "if" to tweak ratio of new infra vs old infra
        rand_pct_call = random.randint(1,100)
        if rand_pct_call <= 85:
            self.call_new_api()
        else:
            self.call_old_api()

    def call_old_api(self):
        self.client.get(self.final_old_search_url, name="OLD INFRA [from actual logs]")

    def call_new_api(self):
        self.client.get(self.final_search_url, name="NEW INFRA [random LL, random radius, limit=50]")

class EndUser(HttpLocust):
    host = "https://api.foursquare.com/v2/"
    task_set = APICall
    min_wait = 200
    max_wait = 200

    def __init__(self):
        super(EndUser, self).__init__()
        global PARAMS
        global CATEGORIES
        if len(PARAMS) == 0:
            with open('gps_country_city.csv','r') as f:
                reader = csv.reader(f)
                temp_list = list(reader)
                del temp_list[0]
                for row in temp_list:
                    PARAMS.append({'country':row[0],
                                     'city':row[1],
                                      'll':row[2] + ',' + row[3]})
        if len(CATEGORIES) == 0:
            with open('fsq_strict_commercial.csv','r') as fcat:
                reader = csv.reader(fcat)
                temp_list = list(reader)
                for row in temp_list:
                    CATEGORIES.append({'categoryId':row[0]})
        if len(QUERIES) == 0:
            with open('nounlist.txt','r') as fqr:
                word = fqr.readline()
                while word:
                    QUERIES.append({'query':word.rstrip()})
                    word = fqr.readline()
        if len(AMAPLOGS) == 0:
            to_replace = 'RAWREQ:https://api.foursquare.com/v2/venues/search?client_id=PB3FRIW31A2Z3F0Q5KNOYTONAGPFVGJT4YYZHWG1CAM2IFNN&client_secret=0G4NS2MITAKJO5BLYVIMGETL3AAZJUYF1YPIROBZFAIVZMIE'
            with open('4sq_case.txt','r') as fql:
                logline = fql.readline()
                while logline:
                    AMAPLOGS.append({'request':logline.strip().replace(to_replace,'')})
                    logline = fql.readline()

"""
Test Cases for Reference
# aMaps new Key with random LL, random radius, limit=50, random category    
#search_url = search_url + "&ll=" + params["ll"] + "&radius=" + random_radius + "&limit=" + random_limit + "&categoryId=" + cat["categoryId"]

# aMaps new Key with ramdom LL, random radius, limit=50, random category, 1 query word
#search_url = search_url + "&ll=" + params["ll"] + "&radius=" + random_radius + "&limit=" + random_limit + "&categoryId=" + cat["categoryId"] + "&query=" + query["query"]

# CY FSQ Key with random LL, random radius, limit=50, random category, 1 query word
#old_search_url = old_search_url + "&ll=" + params["ll"] + "&radius=" + random_radius + "&limit=" + random_limit + "&categoryId=" + cat["categoryId"] + "&query=" + query["query"]

# Query used by aMaps for test - 13.6.19
#search_url = "venues/search?client_id=PL5R5QCLX3FTCPOHDKKIQWV5HB4JTJP221O3W5SUGUIWHBWV&client_secret=2UNS5PQMYRFTKRLNV1PBGWBD0EF1SQUSL2ZK0BQTAPRGVMBY&query=%E7%8E%AF%E7%90%83%E5%BD%B1%E5%9F%8E&limit=50&ll=34.661483%2C135.430068&radius=50000&v=20190612"

# aMaps new Key with random LL, limit=50, random radius
#search_url = search_url + "limit=" + random_limit + "&radius=" + random_radius + "&ll=" + params["ll"]

# CY FSQ Key with random LL, limit=50, random radius
#old_search_url = old_search_url + "limit=" + random_limit + "&radius=" + random_radius + "&ll=" + params["ll"]

# aMaps new Key with fixed category, limit=20, fixed LL, fixed radius
#search_url = search_url + "&categoryId=4bf58dd8d48988d13b941735%2C4bf58dd8d48988d116941735&limit=20&ll=38.889931%2C-77.009003&radius=3000&v=20190422"

# aMaps new Key with variable query length, limit=50, random LL, random radius, random category
#search_url = search_url + "&limit=" + random_limit + "&radius=" + random_radius + "&ll=" + params["ll"] + "&categoryId=" + cat["categoryId"] + "&query="
#final_query = ""
#for i in range(num_queries):
#    final_query = final_query + query[i] + " "
#    final_query = urllib.parse.quote(final_query)
#search_url = search_url + final_query
"""
