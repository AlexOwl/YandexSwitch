# Yandex.Switch 🔌

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

### Home Assistant custom component to control Yandex.Switch (Tuya based)

# 💿 Installation

Follow `Community -> SETTINGS` to add custom repository to [HACS](https://github.com/custom-components/hacs) 

Fill first field with the url of this repo (https://github.com/AlexOwl/YandexSwitch) and select `Integration` category

# 📖 Configuration

### `configuration.yaml` example
```yaml
switch:
  - platform: yandex_switch
    name: Bedside Lamp
    icon: mdi:lamp
    host: 192.168.0.5
    local_key: aaaaaaaaaaaaaaaa 
    device_id: bbbbbbbbbbbbbbbbbbbbbb
```

## Basic

### `host` - Required
The local ip of your switch

### `local_key` - Required
The localKey parameter of your switch

### `device_id` - Required
The devId parameter of your switch

### `name` - Optional
The name that will be displayed in the home assistant

### `icon` - Optional
The icon that will be displayed in the home assistant

## Advanced

### `scan_interval` - Optional, default: 20 seconds
The interval in seconds to force pull update from the switch

### `schema` - Optional
The custom schema to be used instead of the yandex switch schema

Use it, if you want to change the name of the attribute or you have the Tuya switch that has the same protocol, but other dps

The switch attribute must have `switch` in the `code` parameter like `"code":"switch_2"`

### `switch_id`- Optional
The custom switch id (dps) to use instead of the found one in the schema (you can name switch attribute as you want)

# 📝 License

Released under [MIT license](https://AlexOwl.mit-license.org/)

# 🦉 [Alex Owl](https://github.com/AlexOwl)