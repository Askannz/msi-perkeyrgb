msi-perkeyrgb
==================

This progam allows to control the SteelSeries per-key RGB keyboard backlighting on MSI laptops such as the GE63VR. It *will not work* on models with region-based backlighting (such as GE62VR and others). For those you should use tools like [MSIKLM](https://github.com/Gibtnix/MSIKLM).

This is an unofficial tool, I am not affiliated to MSI nor SteelSeries in any way.


Installation
----------

If you are on Archlinux, use this AUR package : [msi-perkeyrgb](https://aur.archlinux.org/packages/msi-perkeyrgb/) (not up-to-date with the Git version yet)

For Ubuntu or others :

```
git clone https://github.com/Askannz/msi-perkeyrgb
cd msi-perkeyrgb/
sudo python3 setup.py install
sudo cp 99-msi-rgb.rules /etc/udev/rules.d/
```

After installation, you must reboot your computer (necessary for the udev rule to take effect, if you don't you will run into permission problems)

Features
----------

Keyboard wide setup from the command line supports `steady` and `breathe` modes.

Per-key configuration supports most if not all supported custom effects, including colorshift effects and `reactive` keys through a configuration file.

Presets are available for supported models, which emulate vendor-provided SteelSeries configurations.


Compatibility
----------

This tool should probably work on any recent MSI laptop with a per-key RGB keyboard. It was tested with the following models :

| Model | Basic color support | Effects support
| ----  | ------------------- | --------------
| GE63  | Yes                 | Yes
| GE73  | Yes                 | Untested
| GE75  | Yes                 | Untested
| GL63  | Yes                 | Untested
| GS63  | Yes                 | Untested
| GS65  | Yes                 | Yes
| GS75  | Yes                 | Untested
| GT63  | Yes                 | Untested
| GT75  | Yes                 | Untested

If you have some additional test results, feel free to open a GitHub issue to help expand this list !

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

### Simple usage

Steady color :
```
msi-perkeyrgb --model <MSI model> -s <COLOR>
```

"Breathe" color :
```
msi-perkeyrgb --model <MSI model> -b <COLOR>
```

Built-in preset (see `--list-presets` for available options) :
```
msi-perkeyrgb --model <MSI model> -p <preset>
```

### Advanced usage

Set from configuration file :
```
msi-perkeyrgb --model <MSI model> -c <path to your configuration file>
```
This is by far the most flexible and powerful way to use this tool, since the configuration file allows you to set individual key configurations and supports a wide range of lighting effects.

The configuration file can have any extension. See the [dedicated wiki page](https://github.com/Askannz/msi-perkeyrgb/wiki/Configuration-file-guide) for its syntax and examples.


How does it work ?
----------

The SteelSeries keyboard is connected to the MSI laptop by two independent interfaces :
* A PS/2 interface to send keypresses
* a USB HID-compliant interface to receive RGB commands

Talking to the RGB controller from Linux is a matter of sending the correct binary packets on the USB HID interface. I used Wireshark to capture the traffic between the SteelSeries Engine on Windows and the keyboard, and then analyzed the captured data to figure out the protocol used. I was only able to reverse-engineer the simple "steady color" commands, but that work was massively improved upon by https://github.com/TauAkiou, who figured out the rest of the protocol and implemented the remaining effects. His work include a detailed write-up of the protocol which you can read [here](documentation/0b_packet_information/msi-kb-effectdoc).

The HID communication code was inspired by other tools designed for previous generations of MSI laptops, such as [MSIKLM](https://github.com/Gibtnix/MSIKLM).
