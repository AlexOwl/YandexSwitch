import logging
import voluptuous as vol
from datetime import timedelta
import asyncio

from homeassistant.components.switch import SwitchDevice, PLATFORM_SCHEMA, ATTR_TODAY_ENERGY_KWH, ATTR_CURRENT_POWER_W, DEVICE_CLASS_OUTLET
from homeassistant.const import CONF_NAME, CONF_ICON, CONF_HOST, CONF_DEVICE_ID, CONF_SCAN_INTERVAL
from homeassistant.helpers.event import track_time_interval
import homeassistant.helpers.config_validation as cv


from .tuya_client import TuyaClient
from . import helper

CONF_LOCAL_KEY = 'local_key'
CONF_SCHEMA = 'schema'
CONF_SWITCH_ID = 'switch_id'

# REAL SCHEMA: [{"mode":"rw","code":"switch_1","name":"开关1","property":{"type":"bool"},"iconname":"icon-dp_power2","id":1,"type":"obj","desc":""},{"mode":"rw","code":"countdown_1","name":"开关1倒计时","property":{"unit":"s","min":0,"max":86400,"scale":0,"step":1,"type":"value"},"iconname":"icon-dp_time2","id":9,"type":"obj","desc":""},{"mode":"rw","code":"add_ele","name":"增加电量","property":{"unit":"","min":0,"max":50000,"scale":3,"step":100,"type":"value"},"iconname":"icon-battery","id":17,"type":"obj","desc":""},{"mode":"ro","code":"cur_current","name":"当前电流","property":{"unit":"mA","min":0,"max":30000,"scale":0,"step":1,"type":"value"},"iconname":"icon-Ele","id":18,"type":"obj","desc":""},{"mode":"ro","code":"cur_power","name":"当前功率","property":{"unit":"W","min":0,"max":50000,"scale":1,"step":1,"type":"value"},"iconname":"icon-dp_tool","id":19,"type":"obj","desc":""},{"mode":"ro","code":"cur_voltage","name":"当前电压","property":{"unit":"V","min":0,"max":5000,"scale":1,"step":1,"type":"value"},"iconname":"icon-a_function_turbo","id":20,"type":"obj","desc":""},{"mode":"ro","code":"test_bit","name":"产测结果位","property":{"unit":"","min":0,"max":5,"scale":0,"step":1,"type":"value"},"iconname":"icon-dp_direction","id":21,"type":"obj","desc":""},{"mode":"ro","code":"voltage_coe","name":"电压校准系数","property":{"unit":"","min":0,"max":1000000,"scale":0,"step":1,"type":"value"},"iconname":"icon-gaodiyin","id":22,"type":"obj","desc":""},{"mode":"ro","code":"electric_coe","name":"电流校准系数","property":{"unit":"","min":0,"max":1000000,"scale":0,"step":1,"type":"value"},"iconname":"icon-gaodiyin","id":23,"type":"obj","desc":""},{"mode":"ro","code":"power_coe","name":"功率校准系数","property":{"unit":"","min":0,"max":1000000,"scale":0,"step":1,"type":"value"},"iconname":"icon-gaodiyin","id":24,"type":"obj","desc":""},{"mode":"ro","code":"electricity_coe","name":"电量校准系数","property":{"unit":"","min":0,"max":1000000,"scale":0,"step":1,"type":"value"},"iconname":"icon-gaodiyin","id":25,"type":"obj","desc":""},{"mode":"ro","code":"fault","scope":"fault","name":"故障告警","property":{"label":["ov_cr"],"type":"bitmap","maxlen":1},"id":26,"type":"obj","desc":"ov_cr：过流保护"}]

SCHEMA_DEFAULT = [{"mode":"rw","code":"switch","property":{"type":"bool"},"id":1},{"mode":"rw","code":"countdown","property":{"unit":"s","min":0,"max":86400,"scale":0,"step":1,"type":"value"},"id":9},{"mode":"rw","code":"statistics_function","property":{"unit":"","min":0,"max":50000,"scale":3,"step":100,"type":"value"},"id":17},{"mode":"ro","code":"current_current_mA","property":{"unit":"mA","min":0,"max":30000,"scale":0,"step":1,"type":"value"},"id":18},{"mode":"ro","code":ATTR_CURRENT_POWER_W,"property":{"unit":"W","min":0,"max":50000,"scale":1,"step":1,"type":"value"},"id":19},{"mode":"ro","code":"current_voltage_v","property":{"unit":"V","min":0,"max":5000,"scale":1,"step":1,"type":"value"},"id":20},{"mode":"ro","code":"test_bit","property":{"unit":"","min":0,"max":5,"scale":0,"step":1,"type":"value"},"id":21},{"mode":"ro","code":"voltage_coefficient","property":{"unit":"","min":0,"max":1000000,"scale":0,"step":1,"type":"value"},"id":22},{"mode":"ro","code":"electric_coefficient","property":{"unit":"","min":0,"max":1000000,"scale":0,"step":1,"type":"value"},"id":23},{"mode":"ro","code":"power_coefficient","property":{"unit":"","min":0,"max":1000000,"scale":0,"step":1,"type":"value"},"id":24},{"mode":"ro","code":"electricity_coefficient","property":{"unit":"","min":0,"max":1000000,"scale":0,"step":1,"type":"value"},"id":25},{"mode":"ro","code":"overcurrent_protection","scope":"fault","property":{"label":["ov_cr"],"type":"bitmap","maxlen":1},"id":26}]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(CONF_ICON): cv.icon,
    vol.Optional(CONF_SCAN_INTERVAL, default=20): cv.positive_int,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
    vol.Required(CONF_LOCAL_KEY): cv.string,
    vol.Optional(CONF_SCHEMA, default=SCHEMA_DEFAULT): list,
    vol.Optional(CONF_SWITCH_ID): cv.string
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([
            YandexSwitchDevice(
                config.get(CONF_NAME),
                config.get(CONF_ICON),
                config.get(CONF_SCAN_INTERVAL),
                config.get(CONF_HOST),
                config.get(CONF_DEVICE_ID),
                config.get(CONF_LOCAL_KEY),
                config.get(CONF_SCHEMA),
                config.get(CONF_SWITCH_ID)
            )
    ])

class YandexSwitchDevice(SwitchDevice):

    def __init__(self, name, icon, scan_interval, host, deviceid, localkey, schema, switch_id = None):
        self._name = name
        self._icon = icon
        self._scan_interval = scan_interval
        self._schema = schema

        self._status = dict()

        self._tuya_client = TuyaClient(host, deviceid, localkey, schema, switch_id)
        self._tuya_client.listeners.append(self._listener)

    async def _listener(self, reply):
        if "dps" in reply:
            self._status.update(reply["dps"])

        self.async_schedule_update_ha_state()
        
    async def async_added_to_hass(self):
        asyncio.create_task(self._tuya_client.run_forever(loop=self.hass.loop))
        asyncio.create_task(self._update_task())

    async def _update_task(self):
        while True:
            asyncio.create_task(self.async_update())
            await asyncio.sleep(self._scan_interval, loop=self.hass.loop)

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        return False

    @property
    def is_on(self):
        return self._status.get(self._tuya_client.switch_id) or False

    @property
    def device_state_attributes(self):
        if self._status.get(self._tuya_client.switch_id) is not None:
            return helper.dps_to_value(self._schema, self._status)

    @property
    def icon(self):
        return self._icon

    async def async_turn_on(self, **kwargs):
        await self._tuya_client.send_control_request({ self._tuya_client.switch_id: True })

    async def async_turn_off(self, **kwargs):
        await self._tuya_client.send_control_request({ self._tuya_client.switch_id: False })

    async def async_update(self):
        await self._tuya_client.send_control_request()

    @property
    def current_power_w(self):
        return self.device_state_attributes.get(ATTR_CURRENT_POWER_W) if self.device_state_attributes is not None else None

    @property
    def today_energy_kwh(self):
        # TODO
        return None
    
    @property
    def device_class(self):
        return DEVICE_CLASS_OUTLET
