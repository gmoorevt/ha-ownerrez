# Home Assistant OwnerRez Integration

This custom integration for Home Assistant allows you to monitor the booking status of your OwnerRez property.

## Features

- Shows whether your property is currently booked
- Updates every 5 minutes
- Easy configuration through the Home Assistant UI

## Installation

### HACS (Recommended)

1. Open HACS
2. Click on "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add `https://github.com/gmoorevt/ha-ownerrez` and select "Integration" as the category
6. Click "Add"
7. Find "OwnerRez" in the integration list and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/ownerrez` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "OwnerRez"
4. Enter your:
   - OwnerRez Username
   - API Token
   - Property ID

## Requirements

- Home Assistant 2023.8.0 or later
- OwnerRez account with API access
- Property ID from OwnerRez

## API Access

To get your API credentials:
1. Log in to your OwnerRez account
2. Go to Settings > API Access
3. Generate or copy your API token
4. Note your username and property ID

## Support

If you're having issues:
1. Check the Home Assistant logs
2. Open an issue on GitHub with:
   - Description of the problem
   - Home Assistant logs
   - Your configuration (without sensitive data)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.  New changes are welcome.

## License

[MIT](LICENSE)