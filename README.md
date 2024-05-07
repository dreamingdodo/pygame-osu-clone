# Pygame OSU! Clone

## Description
This project is a small school assignment aimed at learning the basics of Pygame. It's a clone of OSU! (osu.ppy.sh), a rhythm game. While development will cease after the presentation, the project is open for others to run and contribute to. Below, you'll find documentation and a startup guide.

## How to Run
### Prerequisites
This project requires the following packages:
- Python
- Pygame
- os
- zipfile
- math
- bisect
- numpy
- shutil
- tkinter

### Instructions
1. **Install Packages**: Ensure you have Python installed, then install the required packages listed above.
2. **Run `new_song.py`**: This script allows you to select a beatmap (`.osz` file) from your system. Beatmap files contain song information, circle placements, and more. You can learn about beatmap formats [here](https://osu.ppy.sh/wiki/en/Client/File_formats/osu_(file_format)). Beatmaps can be downloaded from [osu.ppy.sh/beatmapsets](https://osu.ppy.sh/beatmapsets).
    - **Note**: Installing a new beatmap will replace the existing one.
3. **Run `osu.py`**: This script prompts you to select a difficulty using your mouse.
4. **Play OSU!**: Enjoy the game!

### How to play
1. **Options**: In the main menu, press `o` to open the options menu. To change the keybindings, click the button you want to change and press the key/button you want to replace it with. These keybindings will be reset everytime you run `osu.py`.

### TODO
1. Save keybindings
2. Sliders an option to enable (off by default)
3. Miss sound
4. Write technical documentation

## Credits
- AI-assisted parts of the code are marked with comments.
- Preinstalled assets are sourced from [this skin](https://osu.ppy.sh/community/forums/topics/1491596).
