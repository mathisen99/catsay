# catsay

A smoky gray cat in a crooked black hat, causing entirely unnecessary trouble
in your Kitty terminal. Give it something to say, chase yarn, or let it steal
letters from your screen.

## Run

Requires Python 3.10+ and [Kitty](https://sw.kovidgoyal.net/kitty/). No Python
packages or background services are needed. Run directly in Kitty, outside tmux.

```sh
./catsay                         # show help
./catsay "The build passed."      # say your message, then leave
printf 'Time for coffee.' | ./catsay
./catsay --pet "Remember to stretch."
./catsay --loop "You should probably be working."
```

Supply a message or choose a play mode.
**Space** advances message pages, **p** pauses, and **q**, **Escape**, or
**Ctrl+C** exits. `--pet` adds wandering between message pages. `--loop`
repeats until dismissed; `--duration` sets a time limit.

The terminal screen and input settings are restored on exit. Speech is visual,
with no audio or AI service. Redirected output emits plain text.

Use `--size 180`, `--size 270`, or `--size 360` to choose the cat's size.
Pass just one number: `catsay --yarn --size 180`. Braces such as
`{180,270,360}` expand into separate arguments in the shell; extra words are
treated as the cat's message.
`--speed`, `--hold`, `--typing-speed`, and `--fps` adjust the animation.
Long messages wrap into pages.

## Install for your user

```sh
git clone https://github.com/mathisen99/catsay.git
cd catsay
python3 tools/install.py --zshrc ~/.zshrc
source ~/.zshrc
catsay
catsay "Hello from anywhere."
```

This installs the runtime and bundled PNGs under `~/.local/share/catsay`, adds
`~/.local/bin/catsay`, and creates a plain `catsay` alias. Running it without a
message or play flag shows help; press **q** to dismiss an animation early. The
installation works even if you move the checkout. No sudo or Python packages
are needed. The installer saves
your original shell configuration as `~/.zshrc.catsay.bak` before adding the alias;
rerunning it updates the installed runtime without duplicating the alias.

Omit `--zshrc` to install just the command. Ensure `~/.local/bin` is in your PATH.
For plain text in scripts, the installed command also accepts piped input.

## Terminal mischief

```sh
catsay --yarn                 # chase a bouncing ball over your actual terminal
catsay --laser                # chase the red dot; space moves it
catsay --zoomies              # high-speed terminal parkour
catsay --overlay              # a quiet stroll across your existing text
catsay --steal                # pull letters out of your terminal and carry them off
catsay --yarn --loop          # endless terrible productivity
catsay --zoomies --duration 8 --size 180
```

These modes run for 20 seconds (16 for stealing) unless you give `--duration` or
`--loop`. **p** pauses, **q** / **Escape** / **Ctrl+C** exits. The overlay modes
draw only temporary graphics over the existing screen and restore the cursor
when done. They need no screen-reading permission. They occupy the terminal
until they finish.

### Screen stealing

`--steal` reads the visible text, including colors, into memory and animates a
copy on the alternate screen. It returns to your original terminal afterwards.
It never executes, edits, or sends commands to your shell. Ordinary text and
colors are copied; existing terminal images are not copied.

To enable it in Kitty:

```sh
python3 tools/install.py --kitty-config ~/.config/kitty/kitty.conf
```

Reload Kitty with **Ctrl+Shift+F5** or open a new Kitty instance. The installer
backs up the configuration and enables password-based remote control with the
`catsay-screen` password restricted to `get-text`. This permits reading terminal
text, including from other Kitty windows, without granting other remote control
commands. To configure it manually, add:

```conf
allow_remote_control password
remote_control_password catsay-screen get-text
```

See Kitty's [remote control documentation](https://sw.kovidgoyal.net/kitty/remote-control/).

## Development

`catsay.py` handles text, animation, and the Kitty graphics protocol;
`playground.py` contains the play modes. The cat has 72 bundled PNG poses at
three sizes. Frames are uploaded once and reused during animation.

The original SVG rig lives in `tools/cat_art.py`. To rebuild the PNGs, install
ImageMagick with SVG support and run:

```sh
python3 tools/build_assets.py
python3 -m unittest discover -s tests -v
```

Intermediate SVGs use a temporary directory and are removed after the build.
Protocol reference: [Kitty graphics protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/).

## License

Code and original character artwork are available under the [MIT License](LICENSE).
Built with LLM assistance.
