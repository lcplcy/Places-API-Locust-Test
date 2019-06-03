# Places API 
## Load Testing with Locust

Read more about Locust [here](https://docs.locust.io/en/stable/what-is-locust.html).

### Requirements
- Python (2 or 3)

### Setting Up
1. Download the locustfile.py and save it to any directory.
2. Follow the instructions [here](https://docs.locust.io/en/stable/installation.html) to install Locust and the relevant dependencies.
3. In the terminal, *cd* to the directory where your locustfile.py is and run the following command:

```shell
locust
```
4. In a web browser, browse to http://127.0.0.1:8089 to open up the Locust UI. Tell Locust how many users you'd wish to load for the test, along with the rate per second at which the users will be created.
  - eg. If you choose to simulate 300 users, at a hatch rate of 10, it will take Locust 30 seconds to create a total of 300 users running concurrently.


