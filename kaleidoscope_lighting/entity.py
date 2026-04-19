from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from . import DOMAIN


class BaseEntity(CoordinatorEntity):
    def __init__(self, coordinator, fixture_id):
        super().__init__(coordinator)
        self.fixture_id = fixture_id

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.fixture_id)},
            name=self.fixture_id,
            manufacturer="Kaleidoscope",
        )

    def _fixture(self):
        return self.coordinator.data[self.fixture_id]
