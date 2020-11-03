"""Local support for Adax wifi-enabled home heaters."""
import asyncio
import time

import async_timeout


class Adax:
    """Adax data handler."""

    def __init__(self, ip, access_token, websession, timeout=15):
        """Init adax data handler."""
        self.ip = ip
        self._access_token = access_token
        self.websession = websession
        self._url = "https://" + self.ip + "/api"
        self._headers = {"Authorization": "Basic " + self._access_token}
        self._timeout = timeout

    async def set_target_temperature(self, target_temperature):
        payload = {
            "command": "set_target",
            "time": int(time.time()),
            "value": int(target_temperature * 100),
        }
        with async_timeout.timeout(self._timeout):
            async with self.websession.get(
                self._url, params=payload, headers=self._headers
            ) as response:
                return response.status

    async def get_status(self):
        payload = {"command": "stat", "time": int(time.time())}
        try:
            with async_timeout.timeout(self._timeout):
                async with self.websession.get(
                    self._url, params=payload, headers=self._headers
                ) as response:
                    response_json = await response.json()
        except asyncio.TimeoutError:
            return None, None

        target_temperature = response_json["targTemp"]
        current_temperature = response_json["currTemp"]
        return current_temperature / 100, target_temperature / 100
