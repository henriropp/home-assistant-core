"""Support for Tibber sensors."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from random import randrange

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import Throttle, dt as dt_util

from .const import DOMAIN as TIBBER_DOMAIN, MANUFACTURER
from .price_logic import PriceLogic

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:currency-usd"
SCAN_INTERVAL = timedelta(minutes=1)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Tibber sensor."""

    tibber_connection = hass.data[TIBBER_DOMAIN]

    entities: list[TibberSensor] = []
    for home in tibber_connection.get_homes(only_active=False):
        try:
            await home.update_info()
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout connecting to Tibber home: %s ", err)
            raise PlatformNotReady() from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Tibber home: %s ", err)
            raise PlatformNotReady() from err

        if home.has_active_subscription:
            entities.append(TibberSensorElPrice(home))

    async_add_entities(entities, True)


class TibberSensor(SensorEntity):
    """Representation of a generic Tibber sensor."""

    def __init__(self, *args, tibber_home, **kwargs):
        """Initialize the sensor."""
        super().__init__(*args, **kwargs)
        self._tibber_home = tibber_home
        self._home_name = tibber_home.info["viewer"]["home"]["appNickname"]
        if self._home_name is None:
            self._home_name = tibber_home.info["viewer"]["home"]["address"].get(
                "address1", ""
            )
        self._device_name = None
        self._model = None

    @property
    def device_info(self):
        """Return the device_info of the device."""
        device_info = DeviceInfo(
            identifiers={(TIBBER_DOMAIN, self._tibber_home.home_id)},
            name=self._device_name,
            manufacturer=MANUFACTURER,
        )
        if self._model is not None:
            device_info["model"] = self._model
        return device_info


class TibberSensorElPrice(TibberSensor):
    """Representation of a Tibber sensor for el price."""

    def __init__(self, tibber_home):
        """Initialize the sensor."""
        super().__init__(tibber_home=tibber_home)
        self._last_updated = None
        self._spread_load_constant = randrange(5000)

        self._attr_available = False
        self._attr_extra_state_attributes = {
            "app_nickname": None,
            "grid_company": None,
            "estimated_annual_consumption": None,
            "price_level": None,
            "max_price": None,
            "avg_price": None,
            "min_price": None,
            "off_peak_1": None,
            "peak": None,
            "off_peak_2": None,
        }
        self._attr_icon = ICON
        self._attr_name = f"Electricity price {self._home_name}"
        self._attr_unique_id = self._tibber_home.home_id
        self._model = "Price Sensor"

        self._device_name = self._home_name

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        now = dt_util.now()
        if (
            not self._tibber_home.last_data_timestamp
            or (self._tibber_home.last_data_timestamp - now).total_seconds()
            < 5 * 3600 + self._spread_load_constant
            or not self.available
        ):
            _LOGGER.debug("Asking for new data")
            await self._fetch_data()

        elif (
            self._tibber_home.current_price_total
            and self._last_updated
            and self._last_updated.hour == now.hour
            and self._tibber_home.last_data_timestamp
        ):
            return

        res = self._tibber_home.current_price_data()
        self._attr_native_value, price_level, self._last_updated = res
        self._attr_extra_state_attributes["price_level"] = price_level

        attrs = self._tibber_home.current_attributes()
        self._attr_extra_state_attributes.update(attrs)
        self._attr_available = self._attr_native_value is not None
        self._attr_native_unit_of_measurement = self._tibber_home.price_unit

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def _fetch_data(self):
        _LOGGER.debug("Fetching data")
        try:
            await self._tibber_home.update_info_and_price_info()
        except (asyncio.TimeoutError, aiohttp.ClientError):
            return
        data = self._tibber_home.info["viewer"]["home"]
        self._attr_extra_state_attributes["app_nickname"] = data["appNickname"]
        self._attr_extra_state_attributes["grid_company"] = data["meteringPointData"][
            "gridCompany"
        ]
        self._attr_extra_state_attributes["estimated_annual_consumption"] = data[
            "meteringPointData"
        ]["estimatedAnnualConsumption"]

        self._price_logic = PriceLogic(self._tibber_home.price_total)
        now = dt_util.now()
        self._price_logic.calculate_cheapest_hours(now)
        hours_3 = self._price_logic.get_cheapest_hours(3)
        self._attr_extra_state_attributes["3hours_next"] = hours_3[0][0]
        self._attr_extra_state_attributes["3hours_next_price"] = hours_3[0][1]
        self._attr_extra_state_attributes["3hours_next_active"] = (
            dt_util.parse_datetime(hours_3[0][0]).hour == now.hour
        )
