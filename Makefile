.DEFAULT_GOAL := setup

build-ui:
	pyinstaller \
		--add-data "GadgetDeck/keyboard.json":"." \
		--add-data "GadgetDeck/*.so":"." \
 		--add-data "steam_appid.txt":"." \
 		--name "GadgetDeck" \
 		GadgetDeck/__main__.py

setup:
	mkdir -p /home/deck/.steam/steam/controller_config
	cp util/game_actions_480.vdf /home/deck/.steam/steam/controller_config/

INSTALL_DIR = /usr/share/gadget-deck
install:
	mkdir -p $(INSTALL_DIR)
	cp gadget-deck-manager.py $(INSTALL_DIR)/
	chmod +x $(INSTALL_DIR)/gadget-deck-manager.py
	cp -r "HID Descriptors" $(INSTALL_DIR)
	pip install -r requirements.txt
	cp util/gadget-deck*.service /etc/systemd/system/
	cp util/99-gadget-deck.rules /etc/polkit-1/rules.d/
