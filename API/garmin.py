#!/usr/bin/env python3

from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

from datetime import date


"""
Enable debug logging
"""
#import logging
#logging.basicConfig(level=logging.DEBUG)

today = date.today()


class GarminData():
    def __init__(self):
        """
        Initialize Garmin client with credentials
        Only needed when your program is initialized
        """
        client = Garmin("email", "#Password")
        client.login()
        data = client.get_stats_and_body(today.isoformat())
        self.bodyBatt = data["bodyBatteryMostRecentValue"]
        self.rhr8 = data["restingHeartRate"]
        self.stress = data["averageStressLevel"]
        self.sleep = data["sleepingSeconds"]
        self.total_steps = data["totalSteps"]


if __name__ == "__main__":
  g = GarminData()  