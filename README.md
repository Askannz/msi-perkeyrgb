msi-perkeyrgb
==================

This progam allows to control the SteelSeries per-key RGB keyboard backlighting on MSI laptops such as the GE63VR. It *will not work* on models with region-based backlighting (such as GE62VR and others). For those you should use tools like [MSIKLM](https://github.com/Gibtnix/MSIKLM).

This fork is a test version that has been partially rewritten to support the Effects protocol. 

This is an unofficial tool, I am not affiliated to MSI nor SteelSeries in any way.


Installation
----------

If you are on Archlinux, use this AUR package : [msi-perkeyrgb](https://aur.archlinux.org/packages/msi-perkeyrgb/)

For Ubuntu or others :

```
git clone https://github.com/TauAkiou/msi-perkeyrgb
cd msi-perkeyrgb/
sudo python3 setup.py install
sudo cp 99-msi-rgb.rules /etc/udev/rules.d/
```

After installation, you must reboot your computer (necessary for the udev rule to take effect, if you don't you will run into permission problems)


Command-line options
----------

```
usage: msi-perkeyrgb [-h] [-v] [-c FILEPATH] [-d] [--id VENDOR_ID:PRODUCT_ID]
                     [--list-presets] [-p PRESET] [-m MODEL] [--list-models]
                     [-s HEXCOLOR] [-b HEXCOLOR] [-V FILEPATH]

Tool to control per-key RGB keyboard backlighting on MSI laptops.
https://github.com/Askannz/msi-perkeyrgb

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Prints version and exits.
  -c FILEPATH, --config FILEPATH
                        Loads the configuration file located at FILEPATH.
                        Refer to the README for syntax. If set to "-", the
                        configuration file is read from the standard input
                        (stdin) instead.
  -d, --disable         Disable RGB lighting.
  --id VENDOR_ID:PRODUCT_ID
                        This argument allows you to specify the vendor/product
                        id of your keyboard. You should not have to use this
                        unless opening the keyboard fails with the default
                        value. IDs are in hexadecimal format (example :
                        1038:1122)
  --list-presets        List available presets for the given laptop model.
  -p PRESET, --preset PRESET
                        Use vendor preset (see --list-presets).
  -m MODEL, --model MODEL
                        Set laptop model (see --list-models). If not
                        specified, will use GE63 as default.
  --list-models         List available laptop models.
  -s HEXCOLOR, --steady HEXCOLOR
                        Set all of the keyboard to a steady html color. ex.
                        00ff00 for green
  -b HEXCOLOR, --breathe HEXCOLOR
                        Set all of the keyboard to breathing effect of defined
                        color. ex. 00ff00 for green
  -V FILEPATH, --verify FILEPATH
                        Verifies the configuration file located at FILEPATH.
                        Refer to the readme for syntax. If set to "-", the
                        configuration file is read from the standard output
                        (stdin) instead.
```

Features
----------

Keyboard wide setup from the command line supports `steady` and `breathe` modes.

Per-key configuration supports most if not all supported custom effects, including colorshift effects and `reactive` keys through a configuration file.

Presets are available for supported models, which emulate vendor-provided SteelSeries configurations.


Compatibility
----------

This tool should probably work on any recent MSI laptop with a per-key RGB keyboard. 

The original codebase has been succesfully tested with the following models :

| Model |
| ----  |
| GE63  |
| GE73  |
| GE75  |
| GS63  |
| GT63  |
| GS65  |
| GS75  |
| GL63  |


The newly added 'effect' support has been successfully tested with the following models:

| Model |
| ----- |
| GS65  |

Please let me know if it works for your particular model, so that I can update this list.

Requirements
----------

* Python 3.4+
* setuptools
  * **Archlinux** : `# pacman -S python-setuptools`
  * **Ubuntu** : `# apt install python3-setuptools`
  * **Fedora** : `# dnf install python3-setuptools`
* libhidapi 0.8+
	* **Archlinux** : `# pacman -S hidapi`
	* **Ubuntu** : `# apt install libhidapi-hidraw0`
	* **Fedora** : `# dnf install hidapi`


Permissions
----------

**IMPORTANT** : you need to have read/write access to the HID interface of your keyboard. The included udev rule should take care of that, but here are some instructions just in case :

The HID interface is shown as `/dev/hidraw*` where `*` can be 0, 1, 2... (there can be more than one if you have a USB mouse or keyboard plugged in). Find the right one (try them all if necessary) and give yourself permissions with `# chmod 666 /dev/hidraw*`.


Usage
----------

```
msi-perkeyrgb --model <MSI model> -p <preset>
```
(see `--list-presets` for available options)

**or**

```
msi-perkeyrgb --model <MSI model> -c <path to your configuration file>
```

The configuration file can take any extension. There are two types of entries:


**Key Entries**
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

* `<mode>` : RGB mode for the selected keys:
    * Available Modes:
        * `steady <color>`: Fixed color mode.
        * `effect <name>`: User-defined effect. See 'effect blocks' below for instructions on how to define a new effect.
        * `reactive <start color> <press color> <duration>`: Reactive mode; the color will change when you press the key and revert to normal after `duration` ms.
* `<mode options>` :
    * `steady`: The desired color in HTML notation. Example : `00ff00` (green).
    * `effect`: The identifier of an assigned effect block. Example: `effect1`.
    * `reactive`: The desired starting & target colors in HTML notation, followed by the duration of the effect (in ms). Example: `ff0000 0000ff 250`(Red to Blue with a 250ms duration.)


If the same key is configured differently by multiple lines, the lowest line takes priority.

**Effect Blocks**

```
effect <effectname>
    start <startcolor>
    trans <color> <duration>
    ...
end
```

* `<effectname>` : A short identifying name for an effect. This name is used to associate effects with keys.
* `start <startcolor>` : Indicates what the starting color of the effect will be, before any transitions take place.
* `trans <color> <duration>` : Defines a transition.
    * A transition is a shift between two color states. Transitions are loaded in the order they are defined. 
    * Up to 16 transitions can be registered to a single effect.
    * Transitions operate in a 'loop' - they will repeat in the defined order indefinitely.
    * When the animation ends, the color immediately changes back to the starting color before looping again. This creates an effect I call a "seam". A good way of avoiding the seam is to create a transition
    that returns to the starting color.
    * The combined duration of all transitions in the loop cannot be greater then 65535 milliseconds. The MSI Control Center
    only supports up to a 30 second duration, so that is a good rule of thumb to go by.
        * `color` : The desired color in HTML notation. Example : 00ff00
        * `duration` : The duration of this transition, in milliseconds. 
* `wave <origin x> <origin y> <axis> <wavelength> <direction>`: Activates the 'wave' effect.
    * The wave effect will ONLY play across keys that share the same effect.
    * The seam is exceptionally visible when Wave Mode is being used.
        * `<origin x>, <origin y>`: Defines the starting point of the wave effect on the keyboard, in percentage form - 0-100 (0, 0 is the upper left corner of the keyboard.)
        * `<axis>`: Defines which axes that the wave will radiate on. (Supported: `x`, `y`, `xy`)
        * `<wavelength>`: Defines the length of each wave pulse. (0-100, percentage)
        * `<direction>`: Defines whether the wave will go inwards or outwards. (Supported: `in`, `out`)
    
Lines prefixed with `#` and blank lines are ignored.



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

Reactive keys that start red, and change to blue for 250ms when the key is pressed.
```
25,38,39,40 reactive ff0000 0000ff 250
```

Defines an effect called `shift1` that transitions from red, to green, to blue over approximately 15 seconds. The final transition is given an extra 1.5 seconds to make the transition from blue back to red smoother (hiding the 'seam').
```
effect shift1
	start ff0000
	trans 00ff00 500
	trans 0000ff 500
	trans ff0000 750
end
```
An effect that uses wave mode. Starts blue, and creates three short waves that flow outward from the center in different colors.
```
effect threewave
	start 0000ff
	trans 000000 200
	trans 00ff00 150
	trans 000000 200
	trans ff0000 150
	trans 000000 250
	wave 40 60 xy 5 out
end
```

An iteration of the first effect, only the arrow and function keys use the `shift1` effect.
```
all steady ffffff
arrows steady shift1
fn steady shift1
```

A simple, keyboard-wide effect that uses the 'threewave' effect.
```
all effect threewave
```



How does it work ?
----------

[Original Author]

The SteelSeries keyboard is connected to the MSI laptop by two independent interfaces :
* A PS/2 interface to send keypresses
* a USB HID-compliant interface to receive RGB commands

On my laptop (GE63VR), the USB interface has the vendor/product ID 0x1038:0x1122. It should be the same for other models, but if it is not, you can specify it yourself with the `--id` option (see above).

I used Wireshark to capture the USB traffic between the SteelSeries Engine on Windows and the keyboard. Then it was a matter of figuring out the protocol used. Due to a lack of time, I have only been able to reverse-engineer the "Steady" mode for each key. Feel free to improve on this work, I will review pull requests.

The HID communication code was inspired by other tools designed for previous generations of MSI laptops, such as [MSIKLM](https://github.com/Gibtnix/MSIKLM).
