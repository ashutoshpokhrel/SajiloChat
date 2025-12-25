#!/bin/bash

# ====== CONFIGURE THESE ======
# Android emulator name (from `flutter emulators`)
ANDROID_EMULATOR="pixel_7_api_34"

# iOS simulator UDID (from `xcrun simctl list devices`)
IOS_UDID="1FA10354-D2FB-4B60-8CCD-8B3598A163E7"
# ============================

# Detect OS
OS=$(uname)

if [[ "$OS" == "Darwin" ]]; then
    # macOS → Try iOS first
    echo "Booting iOS simulator..."
    xcrun simctl boot $IOS_UDID 2>/dev/null || echo "Simulator already booted"
    open -a Simulator
    sleep 5
    echo "Running Flutter on iOS..."
    flutter run -d $IOS_UDID

else
    # Assume Linux/Windows → Android
    echo "Launching Android emulator..."
    flutter emulators --launch $ANDROID_EMULATOR
    sleep 5
    echo "Running Flutter on Android..."
    flutter run -d $ANDROID_EMULATOR
fi

