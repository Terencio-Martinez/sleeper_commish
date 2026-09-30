import httpx


class SleeperClient:
    BASE_URL = "https://api.sleeper.app/v1"

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def _get(self, endpoint: str):
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def get_league(self, league_id: str):
        return await self._get(f"league/{league_id}")

    async def get_users(self, league_id: str):
        return await self._get(f"league/{league_id}/users")

    async def get_rosters(self, league_id: str):
        return await self._get(f"league/{league_id}/rosters")

    async def get_matchups(self, league_id: str, week: int):
        return await self._get(f"league/{league_id}/matchups/{week}")

    async def get_transactions(self, league_id: str, round_number: int):
        return await self._get(
            f"league/{league_id}/transactions/{round_number}"
        )

    async def get_winners_bracket(self, league_id: str):
        return await self._get(
            f"league/{league_id}/winners_bracket"
        )

    async def get_losers_bracket(self, league_id: str):
        return await self._get(
            f"league/{league_id}/losers_bracket"
        )