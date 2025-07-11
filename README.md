# NECTOR200 Home Assistant Integration

A custom Home Assistant integration for the Pego NECTOR200 Temperature Controller, providing comprehensive control and monitoring capabilities for your refrigeration system.

## Features

- **Climate Control**: Full temperature control with setpoint adjustment
- **Real-time Monitoring**: Current temperature and setpoint sensors
- **Switch Controls**: Light and defrost cycle management
- **Status Monitoring**: Alarm and recording status indicators
- **Standby Mode**: Energy-saving standby functionality
- **Session Management**: Automatic authentication and keepalive handling
- **Local Polling**: Direct communication with your NECTOR200 device

## Requirements

- Home Assistant 2023.1.0 or newer
- Pego NECTOR200 Temperature Controller with network connectivity
- Network access to the NECTOR200 device
- PA parameter value from your NECTOR200 device (used as password)

## Installation

### Method 1: Manual Installation

1. Download the `nector200` folder from this repository
2. Copy it to your Home Assistant configuration directory:
   ```
   <config_directory>/custom_components/nector200/
   ```
3. Restart Home Assistant

### Method 2: Git Clone

1. Navigate to your custom_components directory:
   ```bash
   cd /config/custom_components
   ```
2. Clone this repository:
   ```bash
   git clone https://github.com/daggy72/nector200.git
   ```
3. Restart Home Assistant

## Configuration

### Finding Your PA Parameter

The password for the integration is the **PA parameter** value from your NECTOR200 device:

1. Access your NECTOR200 device physically
2. Navigate to the parameters menu
3. Find parameter **PA** (password parameter)
4. Note the value (0-999) - this is your password

### Adding the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click the **Add Integration** button
3. Search for "NECTOR200"
4. Enter the required information:
   - **Host**: IP address of your NECTOR200 device
   - **Username**: Device username (default: "admin")
   - **Password**: PA parameter value from your device

## Available Entities

Once configured, the integration creates the following entities:

### Climate Entity
- **WH1 Temperature Control**: Main climate control entity
  - Supports cooling mode and standby
  - Temperature setpoint adjustment (0.1°C precision)
  - Current temperature display
  - Temperature range: -50°C to +50°C

### Sensors
- **WH1 Temperature**: Current temperature reading
- **WH1 Setpoint**: Current temperature setpoint
- **WH1 Alarm**: Alarm status (On/Off)
- **WH1 Recording**: Recording status (On/Off)

### Switches
- **WH1 Light**: Control the unit's light
- **WH1 Defrost**: Manually trigger defrost cycle

## Usage Examples

### Automation Example
```yaml
automation:
  - alias: "Refrigeration High Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.wh1_temperature
        above: 10
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          message: "WH1 temperature is above 10°C!"
```

### Lovelace Card Example
```yaml
type: thermostat
entity: climate.wh1_temperature_control
name: Wine Cellar
```

### Service Call Examples
```yaml
# Set temperature to 5°C
service: climate.set_temperature
target:
  entity_id: climate.wh1_temperature_control
data:
  temperature: 5.0

# Turn on the light
service: switch.turn_on
target:
  entity_id: switch.wh1_light

# Trigger defrost cycle
service: switch.turn_on
target:
  entity_id: switch.wh1_defrost
```

## API Information

The integration implements the NECTOR200 HTTP protocol with:

- **Authentication**: Session-based login with automatic keepalive
- **Status Updates**: Polled every 30 seconds
- **Session Management**: Automatic re-authentication when needed
- **Control Commands**: Toggle-based controls for switches
- **Parameter Updates**: Incremental temperature adjustments

## Troubleshooting

### Cannot Connect
- Verify the device IP address is correct
- Ensure the device is accessible on your network
- Check that no other connections are active (NECTOR200 has limited concurrent sessions)
- Verify the PA parameter value is correct

### "Too Many Users" Error
- Close any web browser connections to the device
- Power cycle the NECTOR200 device
- Wait 2-3 minutes for sessions to timeout

### Entities Not Updating
- Check the device's web interface is accessible
- Verify network connectivity
- Review Home Assistant logs for error messages

### Password Issues
- The password must be the PA parameter value (0-999)
- The integration automatically formats it correctly
- Common default values: 0, 30, 100, 111, 123

## Technical Details

### Supported NECTOR200 Firmware
- Tested with firmware.bin Rev. 4
- HTTP protocol version: HTTP_NECTOR_01-21

### API Endpoints Used
- `/log.cgi` - Authentication
- `/alive.cgi` - Session keepalive
- `/ajax_data.cgi` - Status polling
- `/btnfunct.cgi` - Control commands
- `/pdatamod.cgi` - Parameter modifications

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

If you encounter issues:

1. Enable debug logging for the integration
2. Check the [Home Assistant logs](https://www.home-assistant.io/docs/configuration/troubleshooting/#enabling-debug-logging)
3. Open an issue on GitHub with:
   - Home Assistant version
   - NECTOR200 firmware version
   - Error messages from logs
   - Steps to reproduce

## Author

**Dagmar** - [@daggy72](https://github.com/daggy72)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Home Assistant Community
- Pego for the NECTOR200 device and protocol documentation