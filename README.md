# Steam Deck Gadget
This is a program to emulate a game controller on the Steam Deck when connected over USB to another computer.

## How it works
The USB port on the Steam Deck is a USB Dual Role Port. This means that, like most phones, it can act as a USB host or device.
This is possible with the DWC3 (DesignWare Core SuperSpeed 3.0) controller in the AMD CPU.  
Using LibComposite, we can emulate a wide variety of USB devices. In this case, an HID device is emulated that has some game controller inputs.

## Prerequisites
- A password set for the `deck` user
- SSH enabled

## How to use
### 1. Enable USB Dual Role Device
On the Steam Deck, boot into the BIOS by holding the `VOLUME UP` button and pressing the power button and go to `setup utility`.
Navigate to `Advanced`>`USB Configuration`>`USB Dual Role Device` and change from `XHCI` to `DRD`.
Then `Exit`>`Exit Saving Changes`.

### 2. Download SteamDeckGadget
Clone this repository into /home/deck and run the setup script
```shell
cd ~/
git clone https://github.com/Frederic98/SteamDeckGadget.git
cd SteamDeckGadget
chmod +x setup
./setup
```

<details>
  <summary>[For contributors]</summary>

#### 2.1: Running from source
To compile the Steamworks python bindings:
- Download Steamworks SDK: https://partner.steamgames.com/dashboard
- Clone SteamworksPy: https://github.com/philippj/SteamworksPy in `/home/deck` (Or, while it's not merged yet, Frederic98/SteamworksPy)
- Copy Steamworks `sdk/public/steam` into SteamworksPy `library/sdk/steam`
- Copy Steamworks `redistibutable_bin/linux64/libsteam_api.so` into SteamworksPy `library/`
- In `SteamworksPy/library`: `make`
- Copy `SteamworksPy.so` and `libsteam_api.so` to `SteamworksPy/steamworks`
</details>

### 3. Enable USB Gadget
In a terminal from the SteamDeckGadget directory:
```shell
sudo modprobe libcomposite
sudo ./steam-gadget load
```

When the Steam Deck is connected to your computer over USB, it should now show up in `Control Panel` under `Devices and Printers`

### 4. Run SteamDeckGadget through Steam
In Desktop Mode, add the `run_ui` file to Steam through `Games`>`Add a Non-Steam Game to My Library...`.
Then, launch the program from the Steam Client

On your computer, search `game controllers` and open `Set up USB game controllers`. Move the Steam Deck joysticks, and this should be reflected on your computer.

In Steam on your computer, go to `settings`->`Controller`->`General controller settings` and enable `Generic gamepad configuration support`.  
Then, click the steam deck and map all the buttons to a controller layout.

### 5. Disable SteamDeckGadget
It should not be necessary to disable the gadget, you can just unplug the Steam Deck from the computer. But if you want:  
`sudo ./steam-gadget unload steam_deck_gadget`

## Planned improvements
- Systemd service to enable USB Gadget on boot
- On-screen keyboard with keyboard HID gadget
- Ethernet gadget for local multiplayer by connecting two Steam Decks to each other (Might need to disable charging on both to prevent one from draining the other)
- MTP gadget to browse Steam Deck files from computer
- UVC gadget for streaming game to computer without the use of an HDMI capture card
