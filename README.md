# IU Beside You

An unofficial, fan-made Codex pet inspired by IU, pairing a realistic face with a chibi body. Wearing a cream jumper and a lavender skirt, IU Beside You keeps you company with gentle waves, playful jumps, expressive reactions and sixteen look directions.

## Get the pet

Find IU Beside You on either pet-sharing site:

- [codex-pets.net](https://codex-pets.net/#/pets/iu-beside-you)
- [codex-pet.org](https://codex-pet.org/pets/iu-beside-you)

## Manual installation

1. Clone this repository, or download the raw [`pet.json`](pet.json) and [`spritesheet.webp`](spritesheet.webp) files.
2. Create an `iu-beside-you` folder inside your Codex home directory’s `pets` folder. By default, this is `~/.codex/pets/iu-beside-you/` on macOS and `%USERPROFILE%\.codex\pets\iu-beside-you\` on Windows. If you use a custom `CODEX_HOME`, use its `pets` folder instead.
3. Copy both files into that folder:

   ```text
   pets/
   └── iu-beside-you/
       ├── pet.json
       └── spritesheet.webp
   ```

4. Open **Settings → Pets**, click the refresh/reload button, then select **IU Beside You**.

Only these two files are needed for installation. To update an existing installation, replace both files and refresh the pet picker again. See the [official pet guide](https://learn.chatgpt.com/docs/pets#create-a-custom-pet) for more about selecting custom pets.

## Animation examples

View the gallery online: [IU Beside You · Animation examples](https://codex-pets.isarvin.com/iu-beside-you/).

To view it offline, clone this repository and open [`examples/index.html`](examples/index.html) in your browser. The gallery includes:

- **Nine animations:** resting, moving right, moving left, attention wave, jumping, disappointed, waiting for you, thinking and reviewing.
- **Frame-by-frame previews:** a separate GIF and a numbered frame sheet for each animation.
- **Sixteen look directions:** an individual direction selector and a clockwise preview.
- **Playback controls:** pause and play, with reduced-motion preferences respected.
- **Automatic light and dark themes:** follows your system preference. Animation previews retain their original light backgrounds.

Standard animation previews use Codex’s frame timings. The look-around preview is an illustrative sweep; in Codex, gaze follows the pointer. No audio or external resources are required.
