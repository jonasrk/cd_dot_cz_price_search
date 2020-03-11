"""cd-dot-cz-price-search

Queries cd.cz for train ticket prices and emails a summary.
AWS Lambda optimized.

Example usage:
        $ python lambda_function.py
"""

import argparse
import ast
import csv
import datetime
import io
import json
import pickle
import re

import boto3
import requests

AWS_REGION = None
EMAIL_FROM = None
EMAIL_TO = None
JOURNEY_ORIGIN = None
VIA = None
JOURNEY_DESTINATION = None
DATES_TO_QUERY = None

EMAIL_SUBJECT = "cd-dot-cz-price-search results"

CSV_COLUMNS = ["date", "origin", "destination", "price"]

EUR_CZK = 25.59
H_IN_CZK = 100

REQUEST_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}
FIRST_REQUEST_URL = "https://www.cd.cz/de/spojeni-a-jizdenka/"
SECOND_REQUEST_URL = f"{FIRST_REQUEST_URL}spojeni-tam/"


def lambda_handler(
    event, context, make_network_requests=True
):  # pylint: disable=unused-argument
    """The main entrypoint for AWS Lambda."""

    global AWS_REGION, EMAIL_FROM  # pylint: disable=global-statement
    global EMAIL_TO, JOURNEY_ORIGIN, VIA  # pylint: disable=global-statement
    global JOURNEY_DESTINATION  # pylint: disable=global-statement
    global DATES_TO_QUERY  # pylint: disable=global-statement

    AWS_REGION = event["AWS_REGION"]
    EMAIL_FROM = event["EMAIL_FROM"]
    EMAIL_TO = event["EMAIL_TO"]
    JOURNEY_ORIGIN = event["JOURNEY_ORIGIN"]
    VIA = event["VIA"]
    JOURNEY_DESTINATION = event["JOURNEY_DESTINATION"]
    DATES_TO_QUERY = event["DATES_TO_QUERY"]

    csv_dict = []

    dates = get_dates(DATES_TO_QUERY)

    for date in dates:

        query_data_object = {
            "date": date,
            "csv_dict": csv_dict,
            "make_network_requests": make_network_requests,
        }

        csv_dict = run_query(
            query_data_object,
            origin=JOURNEY_ORIGIN,
            destination=JOURNEY_DESTINATION,
        )

        csv_dict = run_query(
            query_data_object,
            origin=JOURNEY_DESTINATION,
            destination=JOURNEY_ORIGIN,
        )

    csv_email_content = get_csv_email_content(csv_dict)

    send_email(csv_email_content, make_network_requests)

    return {"statusCode": 200, "body": json.dumps(csv_email_content)}


def send_email(email_body, make_network_requests):
    """Sends email using AWS SES."""

    if make_network_requests:
        ses = boto3.client("ses", region_name=AWS_REGION)
        ses.send_email(
            Source=EMAIL_FROM,
            Destination={"ToAddresses": [EMAIL_TO]},
            Message={
                "Subject": {"Data": EMAIL_SUBJECT},
                "Body": {"Text": {"Data": email_body}},
            },
        )
    else:
        print(email_body)


def get_dates(amount):
    """Returns a list of dates starting today"""

    day = datetime.date.today()

    dates = []

    for _ in range(amount):
        dates.append(day.strftime("%d.%m.%Y"))
        day += datetime.timedelta(days=1)

    return dates


def get_api_response_string(payload, make_network_requests):
    """Chaining two POST requests to receive HTML with prices."""

    with requests.session() as session:
        if make_network_requests:
            first_response = session.post(
                FIRST_REQUEST_URL, data=payload, headers=REQUEST_HEADERS
            )
            # pickle.dump(first_response, open("first_response.pickle", "wb"))

            first_response_string = first_response.content.decode("UTF-8")
            first_response_dict = ast.literal_eval(first_response_string)

            guid = first_response_dict["guid"]

            second_response = session.post(f"{SECOND_REQUEST_URL}{guid}")

            # pickle.dump(second_response,
            # open("second_response.pickle", "wb"))
        else:
            first_response = pickle.load(open("first_response.pickle", "rb"))
            second_response = pickle.load(open("second_response.pickle", "rb"))

    second_response_string = second_response.content.decode("UTF-8")

    return second_response_string


def run_query(query_data_object, origin, destination):
    """Generating payload, querying API, extracting lowest price
    and adding an entry to the results list."""

    csv_dict = query_data_object["csv_dict"]

    payload = get_payload(query_data_object["date"], origin, destination, VIA)

    second_response_string = get_api_response_string(
        payload, query_data_object["make_network_requests"]
    )

    lowest_price = get_lowest_price(second_response_string)

    csv_dict.append(
        {
            CSV_COLUMNS[0]: query_data_object["date"],
            CSV_COLUMNS[1]: origin,
            CSV_COLUMNS[2]: destination,
            CSV_COLUMNS[3]: lowest_price,
        }
    )

    return csv_dict


def get_lowest_price(second_response_string):
    """Get the lowest price from the HTML response"""

    pattern = '(?<="price":)(.*?)(?=,)'

    price_regex_matches = re.findall(pattern, second_response_string)

    price_integers = []
    for price_regex_match in price_regex_matches:
        try:
            price_integers.append(
                int(int(price_regex_match) / H_IN_CZK / EUR_CZK)
            )
        except ValueError:
            pass

    try:
        lowest_price = sorted(list(filter(lambda x: x > 0, price_integers)))[0]
    except IndexError:
        lowest_price = "Error"

    return lowest_price


def get_csv_email_content(csv_dict):
    """Generate CSV output format from dict."""

    csv_output = io.StringIO()

    writer = csv.DictWriter(csv_output, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for data in csv_dict:
        writer.writerow(data)

    return csv_output.getvalue()


def get_payload(date, origin, destination, via):
    """Generating the Payload string for the API."""

    payload = (
        "ttCombination=25&"
        "formType=1&"
        "isReturnOnly=false&"
        "stations%5Bfrom%5D%5BlistID%5D=100003&"
        f"stations%5Bfrom%5D%5Bname%5D={origin}&"
        "stations%5Bfrom%5D%5BerrorName%5D=From&"
        "stations%5Bto%5D%5BlistID%5D=100003&"
        f"stations%5Bto%5D%5Bname%5D={destination}&"
        "stations%5Bto%5D%5BerrorName%5D=To&"
        "stations%5Bvias%5D%5B0%5D%5BlistID%5D=0&"
        f"stations%5Bvias%5D%5B0%5D%5Bname%5D={via}&"
        "stations%5Bvias%5D%5B0%5D%5BerrorName%5D=Via%5B1%5D&"
        "stations%5BisViaChange%5D=false&"
        "services%5Bbike%5D=false&"
        "services%5Bchildren%5D=false&"
        "services%5BwheelChair%5D=false&"
        "services%5Brefreshment%5D=false&"
        "services%5BcarTrain%5D=false&"
        "services%5BsilentComp%5D=false&"
        "services%5BladiesComp%5D=false&"
        "services%5BpowerSupply%5D=false&"
        "services%5BwiFi%5D=false&"
        "services%5BinSenior%5D=false&"
        "services%5Bbeds%5D=false&"
        "services%5BserviceClass%5D=Class2&"
        "dateTime%5BisReturn%5D=false&"
        f"dateTime%5Bdate%5D={date}&"
        "dateTime%5Btime%5D=0%3A1&"
        "dateTime%5BisDeparture%5D=true&"
        f"dateTime%5BdateReturn%5D={date}&"
        "dateTime%5BtimeReturn%5D=19%3A33&"
        "dateTime%5BisDepartureReturn%5D=true&"
        "params%5BonlyDirectConnections%5D=false&"
        "params%5BonlyConnWithoutRes%5D=false&"
        "params%5BuseBed%5D=NoLimit&"
        "params%5BdeltaPMax%5D=-1&"
        "params%5BmaxChanges%5D=4&"
        "params%5BminChangeTime%5D=-1&"
        "params%5BmaxChangeTime%5D=240&"
        "params%5BonlyCD%5D=false&"
        "params%5BonlyCDPartners%5D=true&"
        "params%5BhistoryTrain%5D=false&"
        "params%5BpsgOwnTicket%5D=false&"
        "params%5BaddServiceReservation%5D=false&"
        "params%5BaddServiceDog%5D=false&"
        "params%5BaddServiceBike%5D=false&"
        "params%5BaddServiceSMS%5D=false&"
        "passengers%5Bpassengers%5D%5B0%5D%5Bid%5D=1&"
        "passengers%5Bpassengers%5D%5B0%5D%5BtypeID%5D=5&"
        "passengers%5Bpassengers%5D%5B0%5D%5Bcount%5D=1&"
        "passengers%5Bpassengers%5D%5B0%5D%5Bage%5D=-1&"
        "passengers%5Bpassengers%5D%5B0%5D%5BageState%5D=0&"
        "passengers%5Bpassengers%5D%5B0%5D%5BcardIDs%5D=&"
        "passengers%5Bpassengers%5D%5B0%5D%5BisFavourite%5D=false&"
        "passengers%5Bpassengers%5D%5B0%5D%5BisDefault%5D=false&"
        "passengers%5Bpassengers%5D%5B0%5D%5BisSelected%5D=true&"
        "passengers%5Bpassengers%5D%5B0%5D%5Bnickname%5D=&"
        "passengers%5Bpassengers%5D%5B0%5D%5Bphone%5D=&"
        "passengers%5Bpassengers%5D%5B0%5D%5BcardTypeID%5D=0&"
        "passengers%5Bpassengers%5D%5B0%5D%5Bfullname%5D=&"
        "passengers%5Bpassengers%5D%5B0%5D%5BcardNumber%5D=&"
        "passengers%5Bpassengers%5D%5B0%5D%5Bbirthdate%5D=&"
        "passengers%5Bpassengers%5D%5B0%5D%5Bavatar%5D=&"
        "passengers%5Bpassengers%5D%5B0%5D%5Bimage%5D=&"
        "passengers%5Bpassengers%5D%5B0%5D%5BcompanyName%5D="
    )

    return payload


def cli_entry():
    """Providing a CLI entry by converting args into an AWS
    Lambda style event."""

    parser = argparse.ArgumentParser()

    parser.add_argument("--AWS_REGION", required=True, type=str)

    parser.add_argument("--EMAIL_FROM", required=True, type=str)

    parser.add_argument("--EMAIL_TO", required=True, type=str)

    parser.add_argument("--JOURNEY_ORIGIN", required=True, type=str)

    parser.add_argument("--VIA", required=True, type=str)

    parser.add_argument("--JOURNEY_DESTINATION", required=True, type=str)

    parser.add_argument("--DATES_TO_QUERY", required=True, type=int)

    args = parser.parse_args()

    cli_event = {
        "AWS_REGION": args.AWS_REGION,
        "EMAIL_FROM": args.EMAIL_FROM,
        "EMAIL_TO": args.EMAIL_TO,
        "JOURNEY_ORIGIN": args.JOURNEY_ORIGIN,
        "VIA": args.VIA,
        "JOURNEY_DESTINATION": args.JOURNEY_DESTINATION,
        "DATES_TO_QUERY": args.DATES_TO_QUERY,
    }

    lambda_handler(cli_event, None, make_network_requests=True)


if __name__ == "__main__":
    cli_entry()
