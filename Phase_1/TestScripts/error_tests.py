import requests
import re
import json


def result_append(input, expected_code, returned_code, expected_message, returned_message):
    status = "TEST PASSED"
    if (expected_code != returned_code) or (expected_message != returned_message):
        status = "TEST FAILED"
    result = {"input" : input, "expected_error_code":expected_code, "returned_error_code":returned_code, "expected_error_message":expected_message, "returned_error_message":returned_message, "test_status":status}
    with open('error_tests_data.json', 'a') as outfile:
        json.dump(result, outfile, indent=2)

def geturl(route):
    base = "https://flask-service.boulmkfsb234o.us-east-1.cs.amazonlightsail.com/find"
    return base+route

def test_valid_dateformat():
    input = "start_date=2010-03-04T00:00:00&end_date=2022-03-05T00:00:00"
    p = requests.get(geturl(input))
    result_append(input, "200", str(p.status_code), "Correct data returned", "Correct data returned")

def test_invalid_dateformat():
    input = "start_date=201-03-0T00:00:00&end_date=2022-03-05T00:00:0"
    p = requests.get(geturl(input))
    expected = {"error":"ERROR: Please enter dates in correct format: 'YYYY-MM-DDTHH:mm:ss'"}
    result_append(input, "400", str(p.status_code), p.json(), expected)

def test_future_date():
    input = "start_date=2011-03-01T00:00:00&end_date=2023-03-05T00:00:0"
    p = requests.get(geturl(input))
    expected = {"error":"ERROR: Please enter in valid start and end dates. Dates cannot be future dates."}
    result_append(input, "400", str(p.status_code), p.json(), expected)

def test_invalid_start_and_end_dates():
    input = "start_date=2022-03-05T00:00:0&end_date=2010-03-05T00:00:00"
    p = requests.get(geturl(input))
    expected = {"error":"ERROR: Please enter valid start and end dates. Start date must not be after end date"}
    result_append(input, "400", str(p.status_code), p.json(), expected)

def test_invalid_page():
    input = "/info"
    p = requests.get(geturl(input))
    expected = {"error":"404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."}
    result_append(input, "404", str(p.status_code), p.json(), expected)

if __name__ == "__main__":
    test_valid_dateformat()
    test_invalid_dateformat()
    test_future_date()
    test_invalid_start_and_end_dates()
    test_invalid_page()
