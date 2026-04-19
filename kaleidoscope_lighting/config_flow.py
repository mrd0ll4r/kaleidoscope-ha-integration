from homeassistant import config_entries
import voluptuous as vol
import asyncio
from aiohttp import ClientError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

DOMAIN = "kaleidoscope_lighting"


async def _test_connection(hass, base_url):
    session = async_get_clientsession(hass)
    try:
        async with session.get(f"{base_url}/api/v1/fixtures", timeout=5) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return "fixtures" in data
    except (ClientError, asyncio.TimeoutError):
        return False


class KaleidoscopeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        return KaleidoscopeOptionsFlow()

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Remove trailing API path, if present.
            base_url = user_input["base_url"].rstrip("/")

            if base_url.endswith("/api/v1"):
                base_url = base_url[: -len("/api/v1")]

            user_input["base_url"] = base_url

            ok = await _test_connection(self.hass, user_input["base_url"])

            if not ok:
                errors["base_url"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input["base_url"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input["base_url"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("base_url"): str,
                vol.Required("scan_interval", default=5): vol.All(int, vol.Range(min=1, max=60)),
            }),
            errors=errors,
        )


class KaleidoscopeOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            "scan_interval",
            self.config_entry.data.get("scan_interval", 5),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("scan_interval", default=current): vol.All(int, vol.Range(min=1, max=60)),
            }),
        )
