from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import UpdateFailed

from . import DOMAIN
from .entity import BaseEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    if not coordinator.data:
        return

    for fixture_id, fixture in coordinator.data.items():
        for program_name, program in fixture["programs"].items():
            for param_name, param in program["parameters"].items():
                if param["type"] == "continuous":
                    entities.append(
                        KaleidoscopeNumber(
                            coordinator,
                            fixture_id,
                            program_name,
                            param_name,
                        )
                    )

    async_add_entities(entities)


class KaleidoscopeNumber(BaseEntity, NumberEntity):
    def __init__(self, coordinator, fixture_id, program, param):
        super().__init__(coordinator, fixture_id)
        self.program = program
        self.param = param

    def _param(self):
        return self.coordinator.data[self.fixture_id]["programs"][self.program]["parameters"][self.param]

    @property
    def name(self):
        return f"{self.program} {self.param}"

    @property
    def unique_id(self):
        return f"kaleidoscope_{self.fixture_id}_{self.program}_{self.param}"

    @property
    def extra_state_attributes(self):
        return {
            "fixture_id": self.fixture_id,
            "kind": "parameter",
            "program": self.program,
            "parameter": self.param,
        }

    @property
    def native_min_value(self):
        return self._param()["lower_limit_incl"]

    @property
    def native_max_value(self):
        return self._param()["upper_limit_incl"]

    @property
    def native_value(self):
        return self._param()["current"]

    async def async_set_native_value(self, value):
        try:
            await self.coordinator.api.post_json(
                f"/fixtures/{self.fixture_id}/programs/{self.program}/parameters/{self.param}",
                {
                    "type": "continuous",
                    "value": float(value),
                },
            )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        await self.coordinator.async_request_refresh()
