# Home Assistant Configuration

Ensure devices have static DHCP leases, otherwise, detection will fail.

A useful HardwareZone [thread] on HA in general.

## Integration Specific Notes/Quirks:

### Daikin A/C

- Timer mode is sent on a separate signal channel from the state

### Bluetooth Proxy

- Model is `ESP32-D0WD-V3`
- Refer to `btproxy.yaml`
- Flash with `esphome run btproxy.yaml` over USB

### Philips Hue BLE

- Doesn't work with the USB RTL8821CU adaptor. Only works with the ESP32 bluetooth proxy.

[thread]: https://forums.hardwarezone.com.sg/threads/starting-home-assistant-ha-for-new-users.6751695/
