# IU Beside You

An unofficial, fan-made Codex pet inspired by IU, pairing a realistic face with a chibi body. Wearing a cream jumper and a lavender skirt, IU Beside You keeps you company with gentle waves, playful jumps, expressive reactions and sixteen look directions.

## Get the pet

Find IU Beside You on either pet-sharing site:

- [codex-pets.net](https://codex-pets.net/#/pets/iu-beside-you)
- [codex-pet.org](https://codex-pet.org/pets/iu-beside-you)

## Use a cloud pet

1. Download the raw [`spritesheet.webp`](spritesheet.webp). In ChatGPT’s **Settings → Personalization → Pet**, choose **Upload pet**, or ask the Pets plugin to upload it as **IU Beside You**. If it is already in your cloud pet library, skip this step.
2. Select **IU Beside You** in the pet picker. In the desktop app, open **Settings → Pets** (or **Mini & Pets**, depending on the version).

No local `pets` folder or `pet.json` is needed for a cloud pet. To update it, replace the sprite sheet on the existing cloud pet through the pet editor or Pets plugin.

The [official guide](https://learn.chatgpt.com/docs/pets) documents uploads and says local pets do not automatically sync to the web. Our desktop checks found separate local and cloud copies; replacing local files left the cloud copy unchanged.

## Local installation (alternative)

1. Clone this repository, or download the raw [`pet.json`](pet.json) and [`spritesheet.webp`](spritesheet.webp) files.
2. Create an `iu-beside-you` folder inside your Codex home directory’s `pets` folder. By default, this is `~/.codex/pets/iu-beside-you/` on macOS and `%USERPROFILE%\.codex\pets\iu-beside-you\` on Windows. If you use a custom `CODEX_HOME`, use its `pets` folder instead.
3. Copy both files into that folder:

   ```text
   pets/
   └── iu-beside-you/
       ├── pet.json
       └── spritesheet.webp
   ```

4. Open **Settings → Mini & Pets**, click the refresh/reload button, then select **IU Beside You**.

Only these two files are needed for local installation. To update a local pet, replace both files and refresh the pet picker again.

## Animation examples

View the gallery online: [IU Beside You · Animation examples](https://codex-pets.isarvin.com/iu-beside-you/).

To view it offline, clone this repository and open [`examples/index.html`](examples/index.html) in your browser. The gallery includes:

- **Nine animations:** resting, moving right, moving left, attention wave, jumping, disappointed, waiting for you, thinking and reviewing.
- **Frame-by-frame previews:** a separate GIF and a numbered frame sheet for each animation.
- **Sixteen look directions:** an individual direction selector and a clockwise preview.
- **Playback controls:** pause and play, with reduced-motion preferences respected.
- **Automatic light and dark themes:** follows your system preference. Animation previews retain their original light backgrounds.

Standard animation previews use Codex’s frame timings. The look-around preview is an illustrative sweep; in Codex, gaze is controlled by the app. The gallery plays without audio and requires no external resources.

## Social media examples

Watch the [demonstration video](examples/social-media/demo.mp4) or download the [cover image](examples/social-media/cover.png). The 45-second video shows the pet in use on the desktop, followed by its animations in a scrapbook layout, with Chinese captions and a licensed piano soundtrack.

See [social media examples](examples/social-media/README.md) for details and instructions on rebuilding the video.
