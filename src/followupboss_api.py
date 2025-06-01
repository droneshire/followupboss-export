"""
API Docs: https://docs.followupboss.com/reference/
"""

import base64
from typing import Any, Union, cast

import requests
from ryutils import log

from constants import API_KEY


class FollowUpBossApi:
    TIMEOUT = 5

    BASE_URL = "https://api.followupboss.com/v1/"

    def __init__(self, verbose: bool = False) -> None:
        token = base64.b64encode(f"{API_KEY}:".encode()).decode()
        self.verbose = verbose
        self.headers = {"accept": "application/json", "authorization": f"Basic {token}"}

    def get_total_people(self) -> int:
        if self.verbose:
            log.print_ok_blue("Getting total people")
        response = requests.get(
            self.BASE_URL + "people",
            headers=self.headers,
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("_metadata", {}).get("total", 0)

    def get_people(
        self,
        sort: str = "created",
        limit: int = 10,
        offset: int = 0,
        include_trash: bool = False,
        include_unclaimed: bool = False,
        next_key: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Union[str, int, bool]] = {
            "sort": sort,
            "limit": limit,
            "offset": offset,
            "includeTrash": include_trash,
            "includeUnclaimed": include_unclaimed,
        }
        if next_key:
            params["next"] = next_key

        response = requests.get(
            self.BASE_URL + "people",
            headers=self.headers,
            params=cast(dict[str, Union[str, int, bool, None]], params),
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
