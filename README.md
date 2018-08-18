msi-perkeyrgb
==================

This progam allows to control the SteelSeries per-key RGB keyboard backlighting on MSI laptops such as the GE63VR. It *will not work* on models with region-based backlighting (such as GE62VR and others). For those you should use tools like [MSIKLM](https://github.com/Gibtnix/MSIKLM).

Compatibility
----------

As of now, this tool was only tested on the GE63VR model. However, it should probably work on any recent MSI laptop with a per-key RGB keyboard. Please let me know if it works for your particular model, so that I can create a compatibility list.

Requirements
----------

* Python 3.4+
* libhidapi 0.8+.
	* **Archlinux** : `# pacman -S hidapi`
	* **Ubuntu** : `# apt install libhidapi-hidraw0`

Installation
----------

```
git clone https://github.com/Askannz/msi-perkeyrgb
cd msi-perkeyrgb/
chmod +x msi-perkeyrgb
```

Usage
----------

You must write your RGB configuration in a file and put it in `~/.config/msi-perkeyrgb/keyboard_configs/` (create the missing folders if necessary).

Each line of the config file has the following syntax :

```
<keycodes> <mode> <mode options>
```

* `<keycodes>` is a comma-separated list of decimal keycodes identifying the keys to apply the desired parameters to.
	* You can find the keycode of a key using the `xev` utility : launch `xev` from the terminal and look for "keycode" in `KeyPress` events.
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
all steady ffffff
arrows steady ffff00
fn steady ffc800
```

Only WASD keys (for US layout) lit up in red.
```
25,38,39,40 steady ff0000
```

#### Command-line usage

```
./msi-perkeyrgb -c <name of your configuration file>
```

Command-line options
----------

```
usage: msi-perkeyrgb [-h] [-v] [-c FILENAME] [--id VENDOR_ID:PRODUCT_ID]

Tool to control per-key RGB keyboard backlighting on MSI laptops.
https://github.com/Askannz/msi-perkeyrgb

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Prints version and exits.
  -c FILENAME, --config FILENAME
                        Loads the configuration file with the given FILENAME.
                        Configuration files should be put in ~/.config/msi-
                        perkeyrgb/keyboard_configs/. Refer to the README for
                        syntax.
  --id VENDOR_ID:PRODUCT_ID
                        This argument allows you to specify the vendor/product
                        id of your keyboard. You should not have to use this
                        unless opening the keyboard fails with the default
                        value. IDs are in hexadecimal format (example :
                        1038:1122)
```
