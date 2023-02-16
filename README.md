# GadgetDeck
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

### 2. Install GadgetDeck
In a terminal, run
```shell
curl -s https://raw.githubusercontent.com/Frederic98/GadgetDeck/main/setup | sudo bash
```
This should download and install GadgetDeck and everything it needs to work. When this is done, you should have a new item in your Steam library under `non-steam`.  
:exclamation:It is possible that it shows up as a blank tile without a name. This should be fixed after a reboot.

Start GadgetDeck, and assign actions to all inputs appropriately. When this is done, connect your Deck to a PC and test if the keyboard and mouse work.

On your computer, search `game controllers` and open `Set up USB game controllers`. Move the Steam Deck joysticks, and this should be reflected on your computer.

In Steam on your computer, go to `settings`->`Controller`->`General controller settings` and enable `Generic gamepad configuration support`.  
Then, click the steam deck and map all the buttons to a controller layout.

### 5. Disable GadgetDeck
Not really necessary. But, to stop the USB gadgets, either reboot the Deck, or, in a terminal, type `systemctl stop gadget-deck-base`.

## Planned improvements
- Ethernet gadget for local multiplayer by connecting two Steam Decks to each other (Might need to disable charging on both to prevent one from draining the other)
- MTP gadget to browse Steam Deck files from computer
- UVC gadget for streaming game to computer without the use of an HDMI capture card
