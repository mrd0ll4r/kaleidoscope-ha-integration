from homeassistant.helpers.aiohttp_client import async_get_clientsession


class KaleidoscopeAPI:
    def __init__(self, hass, base_url):
        self.base_url = base_url
        self.session = async_get_clientsession(hass)

    async def get_fixtures(self):
        async with self.session.get(f"{self.base_url}/api/v1/fixtures") as resp:
            resp.raise_for_status()
            return (await resp.json())["fixtures"]

    async def post_json(self, path, data=None):
        async with self.session.post(
                f"{self.base_url}/api/v1{path}",
                json=data,
        ) as resp:
            resp.raise_for_status()
            await resp.text()

    async def post_text(self, path, data=None):
        async with self.session.post(
                f"{self.base_url}/api/v1{path}",
                data=data,
        ) as resp:
            resp.raise_for_status()
            await resp.text()
