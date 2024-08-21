from typing import ClassVar, Mapping, Sequence, Any, Dict, Optional, Tuple, Final, List, cast
from typing_extensions import Self
from typing import Final
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.components.generic import Generic
from viam.logging import getLogger
from kasa import SmartPlug
from kasa import Discover

import asyncio

LOGGER = getLogger(__name__)

class switch(Generic, Reconfigurable):
    
    """
    Generic component, which represents any type of component that can executes arbitrary commands
    """

    MODEL: ClassVar[Model] = Model(ModelFamily("joyce", "kasa"), "switch")

    # create any class parameters here, 'some_pin' is used as an example (change/add as needed)
    some_pin: int

    # Constructor
    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        # here we validate config, the following is just an example and should be updated as needed
        #  validate function to return implicit dependencies in an array
          
        plug_ip = config.attributes.fields["plug_ip"].string_value
        if plug_ip == "":
            raise Exception("plug_ip attribute is required for a KasaSmartPlug component")
        
        return []

    # Handles attribute reconfiguration
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        # here we initialize the resource instance, the following is just an example and should be updated as needed

        plug_ip = config.attributes.fields["plug_ip"].string_value
        self.plug = SmartPlug(plug_ip)

        if config.attributes.fields["default_state"].string_value.lower() == "on" or config.attributes.fields["default_state"].string_value.lower() == "off":
            default_state = config.attributes.fields["default_state"].string_value.lower()
            self.default_state = default_state
        else:
            self.default_state = "on"

        return

    async def discover_kasa_devices(self):
        devices = await Discover.discover()
        device_dict = {}

        for addr, dev in devices.items():
            await dev.update()  # Update device state

            # Format the device information
            device_info = f"<DeviceType.{dev.device_type.name} model {dev.model} at {addr} ({dev.alias}), is_on: {dev.is_on}"

            # Add to dictionary
            device_dict[addr] = device_info

        return device_dict

    async def do_command(
                self,
                command,
                *,
                timeout: Optional[float] = None,
                **kwargs
            ):
        result = {}
        for name, args in command.items():
            if name == "toggle_switch":
                await self.plug.update()
                try:
                    plug_detail = await self.toggle_switch()
                    result["toggle_switch"] = plug_detail
                except TypeError as e:
                    result["toggle_switch"] = f"TypeError: {str(e)}"
                except Exception as e:
                    result["toggle_switch"] = f"Unexpected Error: {str(e)}"

            if name == "toggle_on":
                await self.plug.update()
                try:
                    plug_detail = await self.toggle_on()
                    result["toggle_on"] = plug_detail
                except TypeError as e:
                    result["toggle_on"] = f"TypeError: {str(e)}"
                except Exception as e:
                    result["toggle_on"] = f"Unexpected Error: {str(e)}"

            if name == "toggle_off":
                await self.plug.update()
                try:
                    plug_detail = await self.toggle_off()
                    result["toggle_off"] = plug_detail
                except TypeError as e:
                    result["toggle_off"] = f"TypeError: {str(e)}"
                except Exception as e:
                    result["toggle_off"] = f"Unexpected Error: {str(e)}"

            if name == "discover_kasa_devices":
                await self.plug.update()
                try:
                    device_dict = await self.discover_kasa_devices()
                    result["discover_kasa_devices"] = device_dict
                except TypeError as e:
                    result["discover_kasa_devices"] = f"TypeError: {str(e)}"
                except Exception as e:
                    result["discover_kasa_devices"] = f"Unexpected Error: {str(e)}"

        return result 
    
    async def toggle_on(self):
        """
        Toggle switch on.
        """

        LOGGER.info('Turning On.')
        await self.plug.turn_on()

        await self.plug.update()
        return self.plug.is_on
    
    async def toggle_off(self):
        """
        Toggle switch off.
        """

        LOGGER.info('Turning Off.')
        await self.plug.turn_off()

        await self.plug.update()
        return self.plug.is_on

    async def toggle_switch(self):
        """
        Toggle switch on or off.
        """

        if self.plug.is_on: 
            LOGGER.info('Turning Off.')
            return await self.toggle_off()

        LOGGER.info('Turning On.')
        return await self.toggle_on()
    