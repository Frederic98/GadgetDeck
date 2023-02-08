.DEFAULT_GOAL := setup

build-ui:
	pyinstaller \
		--add-data "SteamDeckGadget/keyboard.json":"." \
		--add-data "SteamDeckGadget/*.so":"." \
 		--add-data "steam_appid.txt":"." \
 		--name "SteamDeckGadget" \
 		SteamDeckGadget/main.py

setup:
	mkdir -p /home/deck/.steam/steam/controller_config
	cp util/game_actions_480.vdf /home/deck/.steam/steam/controller_config/

INSTALL_DIR = /usr/share/steam-gadget
install:
	mkdir -p $(INSTALL_DIR)
	cp steam-gadget.py $(INSTALL_DIR)/
	chmod +x $(INSTALL_DIR)/steam-gadget.py
	cp -r "HID Descriptors" $(INSTALL_DIR)
	pip install -r requirements.txt
	cp util/steam-gadget@.service /etc/systemd/system/
	cp util/steam-gadget-base.service /etc/systemd/system/
	cp util/99-steam-gadget.rules /etc/polkit-1/rules.d/
