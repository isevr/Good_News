from connect_to_iam import IAMLogin, RefreshAccessToken
import datetime
import csv
import pandas as pd
import time

status_code, ca_access_token, ca_refresh_token = IAMLogin().login()

def append_to_csv(ca_access_token:str, ca_refresh_token:str) -> None:
    """
    Append new entries of date, access_token and
    refresh_token in the csv file.
    """

    now = datetime.datetime.now()

    # format the date and time as DD/MM/YYYY HH:MM:SS
    formatted_time = now.strftime("%d/%m/%Y %H:%M:%S")

    # append the data to a csv file
    with open("generatedTokens.csv", mode='a', newline="") as fhand:
        fieldnames = ["date", "access_token", "refresh_token"]
        writer = csv.DictWriter(fhand, fieldnames=fieldnames)

        # if the file is empty write the header row
        if fhand.tell() == 0:
            writer.writeheader()

        # write the data to a new row
        writer.writerow({'date': formatted_time, 'access_token': ca_access_token, 'refresh_token': ca_refresh_token})

append_to_csv(ca_access_token, ca_refresh_token)

while True:
    generatedTokens_df = pd.read_csv("generatedTokens.csv")
    current_access_token = generatedTokens_df["access_token"].iloc[-1]
    current_refresh_token = generatedTokens_df["refresh_token"].iloc[-1]

    # access token has a TTL of 6 hours
    time.sleep(5*3600)

    status_code, ca_access_token, ca_refresh_token = RefreshAccessToken().refresh_token(current_access_token, current_refresh_token)

    if status_code == 200:
        append_to_csv(ca_access_token, ca_refresh_token)
    else:
        print(f"****Failed to refresh token with code {status_code}****")
