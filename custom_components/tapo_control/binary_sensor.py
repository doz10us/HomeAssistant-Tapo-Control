from typing import Optional
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    events = hass.data[DOMAIN][entry.entry_id]['events']
    name = hass.data[DOMAIN][entry.entry_id]['name']
    entities = {
        event.uid: TapoBinarySensor(event.uid, events, name)
        for event in events.get_platform("binary_sensor")
    }

    async_add_entities(entities.values())

    @callback
    def async_check_entities():
        new_entities = []
        for event in events.get_platform("binary_sensor"):
            if event.uid not in entities:
                entities[event.uid] = TapoBinarySensor(event.uid, events, name)
                new_entities.append(entities[event.uid])
        async_add_entities(new_entities)

    events.async_add_listener(async_check_entities)

    return True

class TapoBinarySensor(BinarySensorEntity):

    def __init__(self, uid, events, name):
        self._name = name
        BinarySensorEntity.__init__(self)

        self.uid = uid
        self.events = events

    @property
    def is_on(self) -> bool:
        return self.events.get_uid(self.uid).value

    @property
    def name(self) -> str:
        return f"{self._name} - Motion"

    @property
    def device_class(self) -> Optional[str]:
        return self.events.get_uid(self.uid).device_class

    @property
    def unique_id(self) -> str:
        return self.uid

    @property
    def entity_registry_enabled_default(self) -> bool:
        return self.events.get_uid(self.uid).entity_enabled

    @property
    def should_poll(self) -> bool:
        return False

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.events.async_add_listener(self.async_write_ha_state)
        )
