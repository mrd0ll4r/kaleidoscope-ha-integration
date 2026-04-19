from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import DeviceInfo
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
        entities.append(KaleidoscopeProgramSelect(coordinator, fixture_id))

        for program_name, program in fixture["programs"].items():
            for param_name, param in program["parameters"].items():
                if param["type"] == "discrete":
                    entities.append(
                        KaleidoscopeDiscreteParam(
                            coordinator,
                            fixture_id,
                            program_name,
                            param_name,
                        )
                    )

    async_add_entities(entities)


class KaleidoscopeProgramSelect(BaseEntity, SelectEntity):
    @property
    def name(self):
        return f"{self.fixture_id}.program"

    @property
    def unique_id(self):
        return f"{self.fixture_id}__program_selector"

    @property
    def options(self):
        programs = list(self._fixture()["programs"].keys())

        def sort_key(p):
            if p == "OFF":
                return 0, ""
            if p == "ON":
                return 1, ""
            if p == "MANUAL":
                return 3, ""
            if p == "EXTERNAL":
                return 4, ""
            return 2, p.lower()

        return sorted(programs, key=sort_key)

    @property
    def current_option(self):
        return self._fixture()["selected_program"]

    async def async_select_option(self, option):
        try:
            await self.coordinator.api.post_text(
                f"/fixtures/{self.fixture_id}/set_active_program",
                option,
            )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        await self.coordinator.async_request_refresh()


class KaleidoscopeDiscreteParam(BaseEntity, SelectEntity):
    def __init__(self, coordinator, fixture_id, program, param):
        super().__init__(coordinator, fixture_id)
        self.program = program
        self.param = param

    @property
    def name(self):
        return f"{self.fixture_id}.{self.program}.{self.param}"

    def _param(self):
        return self._fixture()["programs"][self.program]["parameters"][self.param]

    @property
    def unique_id(self):
        return f"{self.fixture_id}_{self.program}_{self.param}"

    @property
    def options(self):
        return sorted(self._param()["levels"].keys())

    @property
    def current_option(self):
        return self._param()["current_level"]

    @property
    def extra_state_attributes(self):
        return {
            "options_with_description": self._param()["levels"]
        }

    async def async_select_option(self, option):
        try:
            await self.coordinator.api.post_json(
                f"/fixtures/{self.fixture_id}/programs/{self.program}/parameters/{self.param}",
                {
                    "type": "discrete",
                    "level": option,
                },
            )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        await self.coordinator.async_request_refresh()
