msi-perkeyrgb
==================

This progam allows to control the SteelSeries per-key RGB keyboard backlighting on MSI laptops such as the GE63VR. It *will not work* on models with region-based backlighting (such as GE62VR and others). For those you should use tools like [MSIKLM](https://github.com/Gibtnix/MSIKLM).

This is an unofficial tool, I am not affiliated to MSI nor SteelSeries in any way.


Installation
----------

```
git clone https://github.com/Askannz/msi-perkeyrgb
cd msi-perkeyrgb/
sudo python setup.py install
sudo cp 99-msi-rgb.rules /etc/udev/rules.d/
```

If you are on Archlinux, use this AUR package : [msi-perkeyrgb](https://aur.archlinux.org/packages/msi-perkeyrgb/)

After installation, you must reboot your computer (necessary for the udev rule to take effect, if you don't you will run into permission problems)


Command-line options
----------

```
usage: msi-perkeyrgb [-h] [-v] [-c FILEPATH] [--id VENDOR_ID:PRODUCT_ID]

Tool to control per-key RGB keyboard backlighting on MSI laptops.
https://github.com/Askannz/msi-perkeyrgb

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Prints version and exits.
  -c FILEPATH, --config FILEPATH
                        Loads the configuration file located at FILEPATH.
                        Refer to the README for syntax.
  --id VENDOR_ID:PRODUCT_ID
                        This argument allows you to specify the vendor/product
                        id of your keyboard. You should not have to use this
                        unless opening the keyboard fails with the default
                        value. IDs are in hexadecimal format (example :
                        1038:1122)
```

Features
----------
Only "Steady" mode (fixed color for each key) is available for now, as I have not figured out the rest of the USB protocol yet. I will add more features later if enough people are interested.


Compatibility
----------

As of now, this tool was only tested on the GE63VR model. However, it should probably work on any recent MSI laptop with a per-key RGB keyboard. Please let me know if it works for your particular model, so that I can create a compatibility list.

Requirements
----------

* Python 3.4+
* libhidapi 0.8+.
	* **Archlinux** : `# pacman -S hidapi`
	* **Ubuntu** : `# apt install libhidapi-hidraw0`


Permissions
----------

**IMPORTANT** : you need to have read/write access to the HID interface of your keyboard. The included udev rule should take care of that, but here are some instructions just in case :

The HID interface is shown as `/dev/hidraw*` where `*` can be 0, 1, 2... (there can be more than one if you have a USB mouse or keyboard plugged in). Find the right one (try them all if necessary) and give yourself permissions with `# chmod 666 /dev/hidraw*`.


Usage
----------

You must write your RGB configuration in a file.

**First line** of the configuration file should have the following syntax :

```
model <laptop model> 
```

Where `<laptop model>` is any of the following :

	GE63
	GE73
	GS63
	GS73
	GX63
	GT63

If your laptop is not in this list, put the closest one or a model with a similar keyboard layout.


**Other lines** have the following syntax :

```
<keycodes> <mode> <mode options>
```

* `<keycodes>` is a comma-separated list of decimal keycodes identifying the keys to apply the desired parameters to.
	* You can find the keycode of a key using the `xev` utility (part of `xorg-xev` in Archlinux, `x11-utils` in Ubuntu) : launch `xev` from the terminal, press the desired key and look for "keycode" in the `KeyPress` event.
	* You can specify a range of keycodes, example : `15-23`
	* There are a few built-in aliases you can use in lieu of keycodes :
		* `all` : the whole keyboard
		* `f_row`: F1-F12 row
		* `arrows` : directional arrows
		* `numrow` : numerical row (above letters), including symbols
		* `numpad` : numerical pad, including symbols, numlock, Enter
		* `characters` : letters+characters except numrow
	* The Function key (Fn) does not have a keycode, so it is identified by the special alias `fn`.
	* You can mix keycodes, keycode ranges and aliases. Example : `45,arrows,79-82,fn,18`

* `<mode>` : RGB mode for the selected keys. For now only the `steady` mode (fixed color) is available.

* `<mode options>` : for `steady` mode, the desired color in HTML notation. Example : `00ff00` (green)


If the same key is configured differently by multiple lines, the lowest line takes priority.

#### Examples

All keys white except yellow arrows and orange "Fn" key.
```
model GE63
all steady ffffff
arrows steady ffff00
fn steady ffc800
```

Only WASD keys (for US layout) lit up in red.
```
model GS65
25,38,39,40 steady ff0000
```

#### Command-line usage

```
msi-perkeyrgb -c <path to your configuration file>
```

How does it work ?
----------

The SteelSeries keyboard is connected to the MSI laptop by two independent interfaces :
* A PS/2 interface to send keypresses
* a USB HID-compliant interface to receive RGB commands

On my laptop (GE63VR), the USB interface has the vendor/product ID 0x1038:0x1122. It should be the same for other models, but if it is not, you can specify it yourself with the `--id` option (see above).

I used Wireshark to capture the USB traffic between the SteelSeries Engine on Windows and the keyboard. Then it was a matter of figuring out the protocol used. Due to a lack of time, I have only been able to reverse-engineer the "Steady" mode for each key. Feel free to improve on this work, I will review pull requests.

The HID communication code was inspired by other tools designed for previous generations of MSI laptops, such as [MSIKLM](https://github.com/Gibtnix/MSIKLM).
