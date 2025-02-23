"""Platform for OwnerRez sensor integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from ownerrez_wrapper import API

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
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
        try:
            is_booked = await hass.async_add_executor_job(
                client.isunitbooked,
                property_id
            )
            _LOGGER.debug("OwnerRez property %s booking status: %s", property_id, is_booked)
            return {"is_booked": is_booked}
        except Exception as err:
            _LOGGER.error("Error fetching OwnerRez data: %s", err)
            raise

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"ownerrez_{entry.entry_id}",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    # Store the coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([OwnerRezPropertySensor(coordinator, entry)])


class OwnerRezPropertySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an OwnerRez sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Is Property Booked"
        self._attr_unique_id = f"{config_entry.entry_id}_is_booked"
        self._attr_device_class = BinarySensorDeviceClass.OCCUPANCY
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": f"OwnerRez Property {config_entry.data['property_id']}",
            "manufacturer": "OwnerRez",
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the property is booked."""
        return self.coordinator.data.get("is_booked") if self.coordinator.data else None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success 