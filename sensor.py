"""Platform for sensor integration."""
from __future__ import annotations

import datetime
import logging

from .agso_cloud import AgsoCloud

from homeassistant.const import UnitOfVolume
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorStateClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

POLL_INTERVAL = datetime.timedelta(minutes=5)


def get_subscribers(agso):
    return agso.get_subscribers()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Agso sensor."""
    config = {**config_entry.data}
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    agso = AgsoCloud(username, password)
    subscribers = await hass.async_add_executor_job(get_subscribers, agso)

    uniqueId = (
        str(subscribers[0].customer_number)
        + "-"
        + subscribers[0].subscriber_number
        + "-"
        + str(subscribers[0].meters[0].meter_number)
    )

    # Todo create probe for every water meter
    probe = AgsoMeterProbe(
        agso,
        "AccumulatedValue",
        subscribers[0].customer_number,
        subscribers[0].subscriber_number,
        subscribers[0].meters[0].meter_number,
    )
    entities = [AgsoAccumulatedConsumption(probe, uniqueId)]

    async_add_entities(entities, True)


class AgsoMeterProbe:
    """The class for handling data retrieval."""

    def __init__(
        self, agso, data_type, customer_number, subscription_number, meter_number
    ):
        """Initialize the probe."""

        self.agso = agso
        self.data_type = data_type
        self.customer_number = customer_number
        self.subscription_number = subscription_number
        self.meter_number = meter_number
        self.value = 0

    @Throttle(POLL_INTERVAL)
    def update(self):
        """Update probe data."""

        _LOGGER.info("Fetching AGSO data")

        try:
            if self.data_type == "AccumulatedValue":
                self.value = self.agso.get_current_meter_reading().value
                _LOGGER.info(
                    "Got accumulated value: "
                    + str(self.agso.get_current_meter_reading().value)
                )

        except:
            _LOGGER.error("Unable to get " + self.data_type + " from the AGSO cloud")


class AgsoAccumulatedConsumption(SensorEntity):
    def __init__(self, probe, unique_id):
        self.probe = probe
        self._attr_name = "Accumulated Water Consumption"
        self._attr_unique_id = unique_id + "-accumulated-consumption"
        self._attr_native_unit_of_measurement = UnitOfVolume.LITERS
        self._attr_device_class = SensorDeviceClass.WATER
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.probe.value

    def update(self) -> None:
        self.probe.update()
