from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady

from .coordinator import KaleidoscopeCoordinator

DOMAIN = "kaleidoscope_lighting"
PLATFORMS = ["select", "number", "button", "light"]

from . import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict):
    # No YAML setup.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    base_url = entry.data["base_url"]
    interval = entry.options.get(
        "polling_interval",
        entry.data.get("polling_interval", 3),
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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)
