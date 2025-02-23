"""Platform for OwnerRez sensor integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from ownerrez_wrapper import API

from homeassistant.components.sensor import (
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

SENSORS = [
    SensorEntityDescription(
        key="is_booked",
        name="Is Property Booked",
        icon="mdi:home-lock",
    ),
    SensorEntityDescription(
        key="guest_name",
        name="Guest Name",
        icon="mdi:account",
    ),
    SensorEntityDescription(
        key="guest_email",
        name="Guest Email",
        icon="mdi:email",
    ),
    SensorEntityDescription(
        key="guest_phone",
        name="Guest Phone",
        icon="mdi:phone",
    ),
]

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
            # First check if unit is booked
            is_booked = await hass.async_add_executor_job(
                client.isunitbooked,
                property_id
            )
            
            data = {"is_booked": "Yes" if is_booked else "No"}
            
            # If booked, get guest information
            if is_booked:
                today = datetime.today()
                bookings = await hass.async_add_executor_job(
                    client.getbookings,
                    property_id,
                    today
                )
                
                # Find current booking
                current_booking = None
                for booking in bookings:
                    arrival = booking.arrival if isinstance(booking.arrival, datetime) else datetime.strptime(booking.arrival, "%Y-%m-%d")
                    departure = booking.departure if isinstance(booking.departure, datetime) else datetime.strptime(booking.departure, "%Y-%m-%d")
                    if arrival <= today and departure >= today:
                        current_booking = booking
                        break
                
                if current_booking and current_booking.guest_id:
                    guest = await hass.async_add_executor_job(
                        client.getguest,
                        current_booking.guest_id
                    )
                    data.update({
                        "guest_name": guest.name,
                        "guest_email": guest.email,
                        "guest_phone": guest.phone
                    })
                else:
                    data.update({
                        "guest_name": None,
                        "guest_email": None,
                        "guest_phone": None
                    })
            else:
                data.update({
                    "guest_name": None,
                    "guest_email": None,
                    "guest_phone": None
                })
            
            _LOGGER.debug("OwnerRez property %s data: %s", property_id, data)
            return data
            
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

    entities = [
        OwnerRezPropertySensor(coordinator, entry, description)
        for description in SENSORS
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
        return self.coordinator.data.get(self.entity_description.key) if self.coordinator.data else None 