from locust import HttpLocust, TaskSet, task
import csv
import random

AMAP_CLIENT_ID = "xxx"
AMAP_CLIENT_SECRET = "yyy"

FOURSQUARE_CLIENT_ID = "XXX"
FOURSQUARE_CLIENT_SECRET = "YYY"

fsq_url = "venues/search?client_id=%s&client_secret=%s&v=20190501&"

PARAMS = []

class APICall(TaskSet):
    final_search_url = ""
    final_old_search_url = ""

    @task
    def gen_random_param(self):
        params = {}
        search_url = fsq_url  % (AMAP_CLIENT_ID, AMAP_CLIENT_SECRET)
        old_search_url = fsq_url  % (FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET)
        if len(PARAMS) > 0:
            num_params = len(PARAMS)
            random_param_index = random.randint(0,num_params-1)
            params = PARAMS[random_param_index]
            random_radius = str(random.randint(50,100000))
            random_limit = str(50)
            search_url = search_url + "limit=" + random_limit + "&radius=" + random_radius + "&ll=" + params["ll"]
            old_search_url = old_search_url + "limit=" + random_limit + "&radius=" + random_radius + "&ll=" + params["ll"]
        self.final_search_url = search_url
        self.final_old_search_url = old_search_url
        self.call_api()
        #self.call_old_api()

    def call_api(self):
        self.client.get(self.final_search_url, name="NEW INFRA")

    def call_old_api(self):
        self.client.get(self.final_old_search_url, name="OLD INFRA")

class EndUser(HttpLocust):
    host = "https://api.foursquare.com/v2/"
    task_set = APICall
    min_wait = 0
    max_wait = 0

    def __init__(self):
        super(EndUser, self).__init__()
        global PARAMS
        if len(PARAMS) == 0:
            with open('gps_country_city.csv','r') as f:
                reader = csv.reader(f)
                temp_list = list(reader)
                del temp_list[0]
                for row in temp_list:
                    PARAMS.append({'country':row[0],
                                     'city':row[1],
                                      'll':row[2] + ',' + row[3]})