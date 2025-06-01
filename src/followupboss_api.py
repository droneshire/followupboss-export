"""
API Docs: https://docs.followupboss.com/reference/
"""

import base64

import requests

from constants import API_KEY


class FollowUpBossApi:
    TIMEOUT = 5

    BASE_URL = "https://api.followupboss.com/v1/"

    def __init__(self):
        token = base64.b64encode(f"{API_KEY}:".encode()).decode()
        self.headers = {"accept": "application/json", "authorization": f"Basic {token}"}

    def get_people(
        self,
        sort="created",
        limit=10,
        offset=0,
        include_trash=False,
        include_unclaimed=False,
        next_key=None,
    ):
        params = {
            "sort": sort,
            "limit": limit,
            "offset": offset,
            "includeTrash": str(include_trash).lower(),
            "includeUnclaimed": str(include_unclaimed).lower(),
        }
        if next_key:
            params["next"] = next_key
        response = requests.get(
            self.BASE_URL + "people",
            headers=self.headers,
            params=params,
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
