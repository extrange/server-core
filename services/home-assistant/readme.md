# Home Assistant Configuration

Ensure devices have static DHCP leases, otherwise, detection will fail.

A useful HardwareZone [thread] on HA in general.

## Automating Motion Sensor Lights

Under the 'Actions' panel, it is necessary to wait until all the triggering motion sensors have detected the `off` occupancy. Otherwise, in the case where a sensor is in the `on` state for a prolonged period of time, the delay will still run and the light will turn off.

## Device/Integration Specific Notes/Quirks:

### Tuya Soil Moisture Sensors

They are wildly inaccurate, keep reading 100% and not waterproof. Use the Thirdreality ones instead.

### Daikin A/C

- Timer mode is sent on a separate signal channel from the state

### Bluetooth Proxy

- Model is `ESP32-D0WD-V3`
- Refer to `btproxy.yaml`
- Flash with `esphome run btproxy.yaml` over USB

### Philips Hue BLE

- Doesn't work with the USB RTL8821CU adaptor. Only works with the ESP32 bluetooth proxy.

[thread]: https://forums.hardwarezone.com.sg/threads/starting-home-assistant-ha-for-new-users.6751695/

### Tuya mmWave Motion Sensors

[z2mqtt page](https://www.zigbee2mqtt.io/devices/ZG-204ZV.html), [Aliexpress link](https://www.aliexpress.com/item/1005010114187645.html)

They are the most accurate, and way faster than the Aqara P1.
