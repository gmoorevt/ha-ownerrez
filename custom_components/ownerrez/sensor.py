"""Platform for OwnerRez sensor integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from ownerrez_wrapper import API

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OwnerRez sensor based on a config entry."""
    client = API(
        username=entry.data["username"],
        token=entry.data["token"]
    )
    property_id = int(entry.data["property_id"])

    async def async_update_data():
        """Fetch data from API endpoint."""
        is_booked = await hass.async_add_executor_job(
            client.isunitbooked,
            property_id
        )
        return {"is_booked": is_booked}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="ownerrez",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    entities = [
        OwnerRezPropertySensor(
            coordinator,
            entry,
            SensorEntityDescription(
                key="is_booked",
                name="Is Property Booked",
                icon="mdi:home-lock",
            ),
        ),
    ]

    async_add_entities(entities)


class OwnerRezPropertySensor(CoordinatorEntity, SensorEntity):
    """Representation of an OwnerRez sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"OwnerRez Property {config_entry.data['property_id']}",
            "manufacturer": "OwnerRez",
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key) 