"""Support for Adax wifi-enabled home heaters."""
import asyncio
import bleak
import operator
import urllib
import secrets
import sys


ADAX_DEVICE_TYPE_HEATER_BLE = 5
BLE_COMMAND_STATUS_OK = 0
BLE_COMMAND_STATUS_INVALID_WIFI = 1
MAX_BYTES_IN_COMMAND_CHUNK = 17
UUID_ADAX_BLE_SERVICE = "3885cc10-7c18-4ad4-a48d-bf11abf7cb92"
UUID_ADAX_BLE_SERVICE_CHARACTERISTIC_COMMAND = "0000cc11-0000-1000-8000-00805f9b34fb"


class AdaxConfig:
    """Adax config handler."""

    def __init__(self, wifi_ssid, wifi_psk, access_token):
        self.wifi_ssid = wifi_ssid
        self.wifi_psk = wifi_psk
        self.access_token = access_token
        self.ip = None

    def command_notification_handler(self, uuid, data):
        byte_list = None if not data else list(data)
        status = None if not byte_list else byte_list[0]
        print("command_notification_handler", data, status)
        if status == BLE_COMMAND_STATUS_OK:
            ip = (
                None
                if not byte_list or len(byte_list) < 5
                else "%d.%d.%d.%d"
                % (byte_list[1], byte_list[2], byte_list[3], byte_list[4])
            )
            print("Heater Registered, use with IP:", ip)
            self.ip = ip
        elif status == BLE_COMMAND_STATUS_INVALID_WIFI:
            print("Invalid WiFi crendentials")
        print(status, byte_list)

    async def register_devices(self):
        print(
            "Press and hold OK button of the heater until the blue led starts blinking \n\n"
        )
        device = await scan_for_any_available_ble_device()
        print()
        print()
        print("device", device)
        if not device:
            return
        async with bleak.BleakClient(device) as client:
            print("connect")
            await client.connect()
            print("start_notify")
            await client.start_notify(
                UUID_ADAX_BLE_SERVICE_CHARACTERISTIC_COMMAND,
                self.command_notification_handler,
            )
            ssid_encoded = urllib.parse.quote(self.wifi_ssid)
            psk_encoded = urllib.parse.quote(self.wifi_psk)
            access_token_encoded = urllib.parse.quote(self.access_token)
            byte_list = list(
                bytearray(
                    "command=join&ssid="
                    + ssid_encoded
                    + "&psk="
                    + psk_encoded
                    + "&token="
                    + access_token_encoded,
                    "ascii",
                )
            )
            print("write_command")
            await write_command(byte_list, client)
            k = 0
            while k < 20 and client.is_connected():
                await asyncio.sleep(2)
                k += 1
            if self.ip:
                print(
                    "\n Your ip is %s and the token is %s".format(
                        self.ip, self.access_token
                    )
                )


async def scan_for_any_available_ble_device():
    discovered = await bleak.discover(timeout=60)
    print(discovered)
    if not discovered:
        return None
    for discovered_item in discovered:
        metadata = discovered_item.metadata
        uuids = metadata.get("uuids")
        if uuids is None or UUID_ADAX_BLE_SERVICE not in uuids:
            continue
        print("Found adax")
        manufacturer_data = metadata.get("manufacturer_data")
        print("manufacturer_data", manufacturer_data)
        if not manufacturer_data:
            continue
        first_bytes = next(iter(manufacturer_data))
        print("first", first_bytes)
        if first_bytes is None:
            continue
        other_bytes = manufacturer_data[first_bytes]
        print(other_bytes)
        manufacturer_data_list = [
            first_bytes % 256,
            operator.floordiv(first_bytes, 256),
        ] + list(other_bytes)
        print(manufacturer_data_list)
        if is_available_device(manufacturer_data_list):
            return discovered_item.address
        print("Device not available")
    return None


def is_available_device(manufacturer_data):
    print("is_available_device")
    if not manufacturer_data and len(manufacturer_data) < 10:
        return False

    type_id = manufacturer_data[0]
    status_byte = manufacturer_data[1]
    mac_id = 0
    for byte in manufacturer_data[2:10]:
        mac_id = mac_id * 256 + byte
    registered = status_byte & (0x1 << 0)
    managed = status_byte & (0x1 << 1)
    print("is_available_device", mac_id, type_id, registered, managed)
    return (
        mac_id
        and type_id == ADAX_DEVICE_TYPE_HEATER_BLE
        and not registered
        and not managed
    )


async def write_command(command_byte_list, client):
    byte_count = len(command_byte_list)
    chunk_count = operator.floordiv(byte_count, MAX_BYTES_IN_COMMAND_CHUNK)
    if chunk_count * MAX_BYTES_IN_COMMAND_CHUNK < byte_count:
        chunk_count += 1
    sent_byte_count = 0
    chunk_nr = 0
    while chunk_nr < chunk_count:
        is_last = chunk_nr == (chunk_count - 1)
        chunk_data_length = (
            byte_count - sent_byte_count if is_last else MAX_BYTES_IN_COMMAND_CHUNK
        )
        chunk = [chunk_nr, 1 if is_last else 0] + command_byte_list[
            sent_byte_count : (sent_byte_count + chunk_data_length)
        ]
        await client.write_gatt_char(
            UUID_ADAX_BLE_SERVICE_CHARACTERISTIC_COMMAND, bytearray(chunk)
        )
        sent_byte_count += chunk_data_length
        chunk_nr += 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Run the script as  python adax_config.py YOUR_WIFI_SSID YOUR_WIFI_PASSWORD"
        )
    token = secrets.token_hex(9)
    configurator = AdaxConfig(sys.argv[1], sys.argv[2], token)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(configurator.register_devices())
    loop.close()
