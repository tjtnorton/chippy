# chippy
A(nother) **CHIP8 / SCHIP** emulator (interpreter) implemented in Python.
<p align="center">
  <img src="https://raw.githubusercontent.com/tjtnorton/chippy/master/img/chippy_blinky.png", title="CHIPPY running BLINKY">
</p>

CHIP8 is an interpreted programming language that was developed by Joseph Weisbecker in the 1970s for use on 8-bit microcomputers such as the COSMAC VIP and Telmac 1800 (cf. <https://en.wikipedia.org/wiki/CHIP-8> for more details).

## Installation
### Virtual environments
It is advised, but by no means necessary, to setup a virtual environment for installing **chippy**. For those using the latest version of the [Anaconda](https://www.anaconda.com/download/) distribution the following commands will setup your environment:
```console
conda create -n chippy27 python=2.7
```
```console
conda activate chippy27
```
Once finished, you can return to your base environment as follows:
```console
conda deactivate
``` 
### Git installation
The **chippy** package can be installed directly from GitHub using pip:
```console
pip install git+https://github.com/tjtnorton/chippy.git
``` 
If behind a proxy, then the following pattern can be invoked:
```console
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --proxy http://[USER]:[PASSWORD]@[PROXY] git+https://github.com/tjtnorton/chippy.git
``` 
## Launching a game
Once the package is installed a CHIP8 or SCHIP game can be launched from the command line using the pattern:
```console
python -m chippy.main games\[CHIP_VERSION]\[GAME]
```
For example:
```console
python -m chippy.main games\chip8\BRIX
```
```console
python -m chippy.main games\schip\ANT
```
A list of available games can be found in games library table below.
## Playing a game
CHIP8 games were originally designed to be played on a 16-key hexadecimal keypad. The following keyboard mapping has been used in this package:

<table align='center'>
<tr><th>ORIGINAL </th><th>MAPPED</th></tr>
<tr><td>

|   |   |   |   |
|:-:|:-:|:-:|:-:|
| 1 | 2 | 3 | C |
| 4 | 5 | 6 | D |
| 7 | 8 | 9 | E |
| A | 0 | B | F |

</td><td>

|   |   |   |   |
|:-:|:-:|:-:|:-:|
| 1 | 2 | 3 | 4 |
| q | w | e | r |
| a | s | d | f |
| z | x | c | v |

</td></tr>
</table>




# Games library
The **chippy** package comes equipped with a selection of Chip8 and SCHIP ROMs. Their CHIP_VERSION and GAME titles are given in the table below:

| CHIP8    | SCHIP    |
|:--------:|:--------:|
| 15PUZZLE | ALIEN    |
| BLINKY   | ANT      |
| BLITZ    | BLINKY   |
| CONNECT4 | CAR      |
| GUESS    | FIELD    |
| HIDDEN   | JOUST    |
| INVADERS | PIPER    |
| KALEID   | RACE     |
| MAZE     | SPACEFIG |
| MERLIN   | UBOAT    |
| MISSILE  | WORM3    |
| mVBRIX   | -        |
| PONG     | -        |
| PONG2    | -        |
| PUZZLE   | -        |
| SYZYGY   | -        |
| TANK     | -        |
| TETRIS   | -        |
| TICTAC   | -        |
| UFO      | -        |
| VBRIX    | -        |
| VERS     | -        |
| WIPEOFF  | -        |

**Note**: mVBRIX is a slightly modified version of VBRIX. This version addresses an issue with the random starting position of the ball. 

# Extras Details
## Additional Features
A few extra features have been introduced with this implementation . In particular,
* **Pause** - A game can be paused at anytime using the p-key.
* **Reset** - A game can be reset using the tab-key.
* **Exit** - A game can be terminated at anytime using the esc-key.

## Graphics
### Upscaling and Smoothing
The original CHIP8 screen has a resolution of 64x32. In this implementation we upscale the draw screen to 800x600 and use a 3x3 median blur filter to round of sharp edges. These modifications were made using the [OpenCV](https://opencv.org/) library.

### Flickering
A straightforward implementation of a CHIP8 interpreter on a modern machine will find that significant flickering occurs on screen. In order to remedy this behaviour a "voting" strategy is applied, that is, only when a pixel has been in the OFF position for a given number of updates (default = 5) will we actually draw it as OFF.
