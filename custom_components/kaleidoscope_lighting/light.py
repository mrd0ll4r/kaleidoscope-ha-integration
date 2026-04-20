from __future__ import annotations

from homeassistant.components.light import (
    LightEntity,
    ColorMode,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .entity import BaseEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        KaleidoscopeLight(coordinator, fixture_id)
        for fixture_id in coordinator.data
    ]

    async_add_entities(entities)


class KaleidoscopeLight(BaseEntity, LightEntity):
    def __init__(self, coordinator, fixture_id):
        super().__init__(coordinator, fixture_id)

    @property
    def supported_color_modes(self):
        return {ColorMode.ONOFF}

    @property
    def color_mode(self):
        return ColorMode.ONOFF

    @property
    def name(self):
        return ""

    @property
    def unique_id(self):
        return f"kaleidoscope_{self.fixture_id}__light"

    @property
    def available(self):
        return (
                self.coordinator.data is not None
                and self.fixture_id in self.coordinator.data
        )

    @property
    def is_on(self):
        return self._fixture()["selected_program"] != "OFF"

    @property
    def effect_list(self):
        programs = list(self._fixture()["programs"].keys())

        # Hide technical/internal modes from UI
        # return [
        #    p for p in programs
        #    if p not in ("MANUAL", "EXTERNAL")
        # ]
        return programs

    @property
    def effect(self):
        return self._fixture()["selected_program"]

    @property
    def extra_state_attributes(self):
        fixture = self._fixture()
        program = fixture["selected_program"]

        return {
            "active_program_parameters": fixture["programs"]
            .get(program, {})
            .get("parameters", {})
        }

    async def async_turn_on(self, **kwargs):
        """Turn on or change program."""
        effect = kwargs.get("effect")

        # If user selected a program from UI
        if effect:
            await self.coordinator.api.post_text(
                f"/fixtures/{self.fixture_id}/set_active_program",
                effect,
            )
        else:
            # default ON behavior
            await self.coordinator.api.post_text(
                f"/fixtures/{self.fixture_id}/set_active_program",
                "ON",
            )

        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.post_text(
            f"/fixtures/{self.fixture_id}/set_active_program",
            "OFF",
        )

        await self.coordinator.async_refresh()

    async def async_update(self):
        """Optional manual refresh support."""
        await self.coordinator.async_request_refresh()
