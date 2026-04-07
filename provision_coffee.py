# ============================================================
# Mr. Coffee Re-Provisioning Script - Phase 1
# ============================================================
# BEFORE RUNNING:
#   1. Fill in your WiFi details in the two lines below
#   2. Connect your PC to the Mr. Coffee's WiFi network
#      (it will appear as something like "WeMo.Coffee..." in
#      your list of available networks)
#   3. Open a terminal/command prompt and run:
#      pip install pywemo
#   4. Then run this script:
#      python provision_coffee.py
# ============================================================

YOUR_WIFI_NAME     = "REPLACE_WITH_YOUR_NETWORK_ID"      # e.g. "MyHomeNetwork"
YOUR_WIFI_PASSWORD = "REPLACE_WITH_YOUR_PASSWORD"  # e.g. "mysecretpassword"

# ============================================================
# Nothing below this line needs to be changed
# ============================================================

import pywemo
import time


def find_coffee_maker():
    print("\nLooking for Mr. Coffee on this network...")
    print("(You should be connected to the Mr. Coffee's WiFi right now)\n")

    # try auto-discovery first
    devices = pywemo.discover_devices()

    if devices:
        for device in devices:
            if "coffee" in type(device).__name__.lower() or "coffee" in device.name.lower():
                print(f"Found it! Device name: {device.name}")
                return device
        # if no coffee maker found by name, return first device found
        print(f"Found a WeMo device: {devices[0].name}")
        return devices[0]

    # if auto-discovery fails, try the default gateway address
    # (when connected to the coffee maker's network, it's usually the gateway)
    import subprocess
    import re

    print("Auto-discovery didn't find it, trying to find the device IP...")
    result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
    ips = re.findall(r"(\d+\.\d+\.\d+\.\d+)", result.stdout)

    for ip in ips:
        if ip.startswith("192.168") or ip.startswith("10."):
            try:
                print(f"  Trying {ip}...")
                url = pywemo.setup_url_for_address(ip)
                device = pywemo.discovery.device_from_description(url)
                print(f"  Found: {device.name}")
                return device
            except Exception:
                continue

    return None


def provision_device(device):
    print(f"\nSending your home WiFi details to: {device.name}")
    print(f"  Network: {YOUR_WIFI_NAME}")
    print(f"  Password: {'*' * len(YOUR_WIFI_PASSWORD)}\n")

    # pywemo tries different encryption methods automatically,
    # but we loop through all 6 combinations as a fallback
    encrypt_methods = [1, 2, 3]
    password_lengths = [True, False]

    for method in encrypt_methods:
        for add_lengths in password_lengths:
            try:
                print(f"  Trying encryption method {method}, add_lengths={add_lengths}...")
                result = device.setup(
                    ssid=YOUR_WIFI_NAME,
                    password=YOUR_WIFI_PASSWORD,
                    _encrypt_method=method,
                    _add_password_lengths=add_lengths,
                )
                if result and result[0] == "1":
                    print("\n✓ Success! The coffee maker accepted your WiFi credentials.")
                    return True
            except Exception as e:
                print(f"    (that combination didn't work: {e})")
                continue

    return False


def main():
    print("=" * 60)
    print("  Mr. Coffee WiFi Re-Provisioning Script")
    print("=" * 60)

    # sanity check - make sure placeholders were filled in
    if "REPLACE_WITH" in YOUR_WIFI_NAME or "REPLACE_WITH" in YOUR_WIFI_PASSWORD:
        print("\n⚠ ERROR: Please fill in your WiFi name and password")
        print("  at the top of this script before running it.\n")
        return

    device = find_coffee_maker()

    if device is None:
        print("\n⚠ Could not find the coffee maker.")
        print("  Make sure your PC is connected to the Mr. Coffee WiFi")
        print("  network (not your home network) and try again.\n")
        return

    success = provision_device(device)

    if success:
        print("\nNext steps:")
        print("  1. Wait about 30 seconds for the coffee maker to reboot")
        print("  2. Reconnect your PC to your normal home WiFi network")
        print("  3. The coffee maker's WiFi broadcast should disappear")
        print("     (that means it successfully joined your home network)")
        print("  4. Run the next script (schedule_coffee.py) to set your brew schedule\n")
    else:
        print("\n⚠ Could not provision the device.")
        print("  This may mean the WiFi chip needs a factory reset first.")
        print("  Try holding the Restore button on the back of the coffee")
        print("  maker for 10 seconds while it's plugged in, then try again.\n")


if __name__ == "__main__":
    main()
