# NECTOR200 Home Assistant Integration

A custom Home Assistant integration for the Pego NECTOR200 Temperature Controller, providing comprehensive control and monitoring capabilities for your refrigeration system.

## Features

- **Climate Control**: Full temperature control with setpoint adjustment
- **Real-time Monitoring**: Current temperature and setpoint sensors
- **Switch Controls**: Light and defrost cycle management
- **Status Monitoring**: Alarm and recording status indicators
- **Standby Mode**: Energy-saving standby functionality
- **Local Polling**: Direct communication with your NECTOR200 device

## Requirements

- Home Assistant 2023.1.0 or newer
- Pego NECTOR200 Temperature Controller with network connectivity
- Network access to the NECTOR200 device
- Device credentials (username and password)

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

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click the **Add Integration** button
3. Search for "NECTOR200"
4. Enter the required information:
   - **Host**: IP address of your NECTOR200 device
   - **Username**: Device username (default: "admin")
   - **Password**: Device password

## Available Entities

Once configured, the integration creates the following entities:

### Climate Entity
- **WH1 Temperature Control**: Main climate control entity
  - Supports cooling mode and standby
  - Temperature setpoint adjustment (0.1°C precision)
  - Current temperature display

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

## API Information

The integration communicates with the NECTOR200 device using HTTP requests:

- **Status Endpoint**: `http://{device_ip}/ajax_data.cgi?pgd='{password}'`
- **Control Endpoint**: `http://{device_ip}/set_param.cgi`

Data is polled every 30 seconds to keep the status up to date.

## Troubleshooting

### Cannot Connect
- Verify the device IP address is correct
- Ensure the device is accessible on your network
- Check username and password are correct
- Confirm Home Assistant can reach the device's network

### Entities Not Updating
- Check the device's web interface is accessible
- Verify network connectivity
- Review Home Assistant logs for error messages

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

If you encounter issues:

1. Check the [Home Assistant logs](https://www.home-assistant.io/docs/configuration/troubleshooting/#enabling-debug-logging)
2. Open an issue on GitHub with:
   - Home Assistant version
   - Integration version
   - Error messages from logs
   - Steps to reproduce

## Author

**Dagmar** - [@daggy72](https://github.com/daggy72)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Home Assistant Community
- Pego for the NECTOR200 device documentation