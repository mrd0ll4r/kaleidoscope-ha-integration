from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import KaleidoscopeCoordinator

DOMAIN = "kaleidoscope_lighting"
PLATFORMS = ["select", "number", "button", "light"]

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall

from . import DOMAIN

SERVICE_SET_PARAMETER = "set_parameter"

SET_PARAMETER_SCHEMA = vol.Schema({
    vol.Required("fixture"): str,
    vol.Required("parameter"): str,
    vol.Required("value"): vol.Any(int, float, str),
})

async def async_setup(hass: HomeAssistant, config: dict):
    # No YAML setup.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    base_url = entry.data["base_url"]
    interval = entry.options.get(
        "scan_interval",
        entry.data.get("scan_interval", 5),
    )

    coord = KaleidoscopeCoordinator(hass, base_url, interval)

    try:
        await coord.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to fetch initial data: {err}") from err

    hass.data[DOMAIN][entry.entry_id] = coord

    entry.async_on_unload(
        entry.add_update_listener(async_reload_entry)
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_PARAMETER,
        async_set_parameter,
        schema=SET_PARAMETER_SCHEMA,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_set_parameter(call: ServiceCall):
    hass = call.hass
    data = hass.data[DOMAIN]

    fixture_id = call.data["fixture"]
    param = call.data["parameter"]
    value = call.data["value"]

    # find coordinator (single entry assumption)
    coord = next(iter(data.values()))

    fixture = coord.data.get(fixture_id)
    if not fixture:
        return

    program = fixture["selected_program"]
    params = fixture["programs"][program]["parameters"]

    if param not in params:
        return

    await coord.api.post_json(
        f"/fixtures/{fixture_id}/programs/{program}/parameters/{param}",
        {
            "type": params[param]["type"],
            "value": value,
        },
    )

    await coord.async_request_refresh()