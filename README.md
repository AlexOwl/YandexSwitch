# Yandex.Switch 🔌

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

### Home Assistant custom component to control Yandex.Switch (Tuya based)

# 💿 Installation

Follow `Community -> SETTINGS` to add custom repository to [HACS](https://github.com/custom-components/hacs) 

Fill first field with the url of this repo (https://github.com/AlexOwl/YandexSwitch) and select `Integration` category

# 🔧 Initial setup

First of all, you need to get the localKey and devId of your switch

There are a lot of ways to pull it, but here is the easiest way:

1. You must have the android device, because we need to install old version of the tuya app and you can't install old version on ios, so find the android device or use emulator
2. Download [Smart Life v.3.4.1](https://apkpure.com/smart-life-smart-living/com.tuya.smartlife/versions) and install it on your android device
3. Register/Login to your Tuya account and add Yandex Switch as the normal Tuya Wi-Fi switch
4. Connect your android device and laptop/pc to the same router
5. If you don't have installed NodeJS, download [it](https://nodejs.org/en/download/current/) and install
6. Open cmd/Terminal and install [tuyapi/cli](https://www.npmjs.com/package/@tuyapi/cli) package using the following command: `npm i @tuyapi/cli -g`
7. Type `tuya-cli list-app` command and follow the instructions

P.S.
1. Instead of scanning qr-code you can type open `http://ip-of-your-laptop:8002/ca.pem`
2. Use parameter `--ip` if the wrong ip was chosen by `tuya-cli`
3. Use retrieved `id` parameter as `device_id` and `key` as `local_key`
 
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