from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import UpdateFailed

from . import DOMAIN
from .entity import BaseEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    if not coordinator.data:
        return

    entities = [
        KaleidoscopeCycleButton(coordinator, fixture_id)
        for fixture_id in coordinator.data
    ]

    async_add_entities(entities)


class KaleidoscopeCycleButton(BaseEntity, ButtonEntity):
    def __init__(self, coordinator, fixture_id):
        super().__init__(coordinator, fixture_id)

    @property
    def name(self):
        return f"{self.fixture_id} cycle program"

    @property
    def unique_id(self):
        return f"{self.fixture_id}__cycle_program_button"

    async def async_press(self):
        try:
            await self.coordinator.api.post_json(
                f"/fixtures/{self.fixture_id}/cycle_active_program",
                None,
            )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        await self.coordinator.async_refresh()
