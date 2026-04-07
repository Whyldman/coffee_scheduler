# ============================================================
# Mr. Coffee Brew Schedule Script - Phase 2
# ============================================================
# BEFORE RUNNING:
#   Make sure your PC is connected to your HOME WiFi network
#   (not the coffee maker's broadcast network)
#   May need to change Deco to 2.4 ghz broadcast only
#
#   Run this script:
#     python schedule_coffee.py
# ============================================================

import pywemo
import time
from datetime import datetime


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def find_coffee_maker():
    print("\nSearching for Mr. Coffee on your home network...")
    devices = pywemo.discover_devices()

    for device in devices:
        if isinstance(device, pywemo.CoffeeMaker):
            print(f"Found it! ({device.host})\n")
            return device

    print("⚠ Could not find the coffee maker on your network.")
    print("  Make sure your PC is on the same WiFi as the coffee maker")
    print("  and the green WiFi light is on, then try again.\n")
    return None


def parse_time(time_str):
    """try to parse a time string like 6:30am, 8:00 AM, 14:30, etc."""
    time_str = time_str.strip().lower().replace(" ", "")
    formats = ["%I:%M%p", "%I%p", "%H:%M", "%H"]

    for fmt in formats:
        try:
            t = datetime.strptime(time_str, fmt)
            return t.hour, t.minute
        except ValueError:
            continue

    return None, None


def prompt_schedule():
    print("=" * 60)
    print("  Brew Schedule Setup")
    print("=" * 60)
    print("\nYou can set a brew time for each day, or skip days you")
    print("don't want coffee. Times can be like: 6:30am, 7am, 8:15 AM\n")

    schedule = {}

    # ask if they want the same time every day or per-day
    print("Would you like:")
    print("  1. The same time every day")
    print("  2. Different times per day")
    print("  3. Weekdays one time, weekends another")

    while True:
        choice = input("\nEnter 1, 2, or 3: ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("  Please enter 1, 2, or 3.")

    if choice == "1":
        while True:
            time_str = input("Brew time for every day (or 'skip' to disable): ").strip()
            if time_str.lower() == "skip":
                print("  All days will be disabled.")
                return {}
            hour, minute = parse_time(time_str)
            if hour is not None:
                for day in DAYS:
                    schedule[day] = (hour, minute)
                break
            print("  Couldn't understand that time. Try something like 6:30am or 7:00 AM.")

    elif choice == "3":
        for label, days in [("Weekdays (Mon-Fri)", DAYS[:5]), ("Weekends (Sat-Sun)", DAYS[5:])]:
            while True:
                time_str = input(f"{label} brew time (or 'skip'): ").strip()
                if time_str.lower() == "skip":
                    print(f"  {label} will be disabled.")
                    break
                hour, minute = parse_time(time_str)
                if hour is not None:
                    for day in days:
                        schedule[day] = (hour, minute)
                    break
                print("  Couldn't understand that time. Try something like 6:30am or 7:00 AM.")

    else:  # choice == "2"
        for day in DAYS:
            while True:
                time_str = input(f"  {day} brew time (or 'skip'): ").strip()
                if time_str.lower() == "skip":
                    print(f"    {day} will be disabled.")
                    break
                hour, minute = parse_time(time_str)
                if hour is not None:
                    schedule[day] = (hour, minute)
                    break
                print("    Couldn't understand that time. Try something like 6:30am or 7:00 AM.")

    return schedule


def confirm_schedule(schedule):
    print("\n" + "=" * 60)
    print("  Your Schedule")
    print("=" * 60)

    for day in DAYS:
        if day in schedule:
            hour, minute = schedule[day]
            t = datetime.strptime(f"{hour}:{minute}", "%H:%M")
            print(f"  {day:<12} {t.strftime('%I:%M %p')}")
        else:
            print(f"  {day:<12} (no brew)")

    print()
    confirm = input("Send this schedule to the coffee maker? (yes/no): ").strip().lower()
    return confirm in ["yes", "y"]


def build_wemo_schedule(schedule):
    """
    build the schedule structure pywemo expects.
    pywemo uses a list of 7 entries (mon-sun), each being
    either None (disabled) or minutes-since-midnight.
    """
    wemo_schedule = []
    for day in DAYS:
        if day in schedule:
            hour, minute = schedule[day]
            wemo_schedule.append(hour * 60 + minute)
        else:
            wemo_schedule.append(None)
    return wemo_schedule


def send_schedule(device, schedule):
    wemo_schedule = build_wemo_schedule(schedule)

    print("\nSending schedule to coffee maker...")

    try:
        # call UpdateWeeklyCalendar directly on the rules service
        # each day is minutes since midnight, or -1 to disable
        device.rules.UpdateWeeklyCalendar(
            Mon   = wemo_schedule[0] if wemo_schedule[0] is not None else -1,
            Tues  = wemo_schedule[1] if wemo_schedule[1] is not None else -1,
            Wed   = wemo_schedule[2] if wemo_schedule[2] is not None else -1,
            Thurs = wemo_schedule[3] if wemo_schedule[3] is not None else -1,
            Fri   = wemo_schedule[4] if wemo_schedule[4] is not None else -1,
            Sat   = wemo_schedule[5] if wemo_schedule[5] is not None else -1,
            Sun   = wemo_schedule[6] if wemo_schedule[6] is not None else -1,
        )
        print("✓ Schedule sent successfully!\n")
        return True
    except Exception as e:
        print(f"⚠ Could not send schedule: {e}\n")
        return False


def main():
    print("=" * 60)
    print("  Mr. Coffee Brew Scheduler")
    print("=" * 60)

    device = find_coffee_maker()
    if device is None:
        return

    schedule = prompt_schedule()
    
    if not schedule:
        print("\nNo brew times set. Nothing was sent to the coffee maker.\n")
        return

    if not confirm_schedule(schedule):
        print("\nCancelled — nothing was sent to the coffee maker.\n")
        return

    success = send_schedule(device, schedule)

    if success:
        print("Your coffee maker will now brew on schedule automatically.")
        print("You can run this script any time to change the schedule.\n")
    else:
        print("Something went wrong sending the schedule.")
        print("Share the output above and we'll fix it together.\n")


if __name__ == "__main__":
    main()
