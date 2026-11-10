#!/usr/bin/env python3
"""Install Catsay's runtime and optionally add its zsh alias."""

import argparse
from pathlib import Path
import shlex
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=Path.home() / '.local')
    parser.add_argument('--zshrc', type=Path, help='add or update the catsay alias')
    parser.add_argument('--kitty-config', type=Path, help='enable read-only Kitty screen access for --steal')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    prefix = args.prefix.expanduser().resolve()
    runtime = prefix / 'share' / 'catsay'
    launcher = prefix / 'bin' / 'catsay'
    alias = f'alias catsay={shlex.quote(str(launcher))}\n'
    previous_alias = f'alias catsay={shlex.quote(shlex.quote(str(launcher)) + " --pet")}'

    # Check for conflicting shell configuration before installing anything.
    zshrc = args.zshrc.expanduser() if args.zshrc else None
    config = zshrc.read_text() if zshrc and zshrc.exists() else ''
    aliases = [line for line in config.splitlines() if line.strip().startswith('alias catsay=')]
    if any(line not in (alias.rstrip('\n'), previous_alias) for line in aliases):
        parser.error(f'{zshrc} already defines a different catsay alias')
    kitty_config = args.kitty_config.expanduser() if args.kitty_config else None
    kitty_text = kitty_config.read_text() if kitty_config and kitty_config.exists() else ''
    controls = [line.split() for line in kitty_text.splitlines() if line.strip().startswith('allow_remote_control ')]
    if controls and controls[-1][1] not in ('password', 'no'):
        parser.error('Kitty already has custom remote control settings; configure screen access manually (see README).')

    runtime.mkdir(parents=True, exist_ok=True)
    launcher.parent.mkdir(parents=True, exist_ok=True)
    for name in ('catsay.py', 'playground.py', 'LICENSE'):
        shutil.copy2(source / name, runtime / name)
    # Replace managed assets so upgrades also remove obsolete sprites.
    if (runtime / 'assets').exists():
        shutil.rmtree(runtime / 'assets')
    shutil.copytree(source / 'assets', runtime / 'assets')
    (runtime / 'moosay.py').unlink(missing_ok=True)
    if (runtime / '__pycache__').exists():
        shutil.rmtree(runtime / '__pycache__')
    launcher.write_text('#!/bin/sh\nexec python3 ' + shlex.quote(str(runtime / 'catsay.py')) + ' "$@"\n')
    launcher.chmod(0o755)

    if zshrc and (not aliases or previous_alias in aliases):
        if zshrc.exists():
            backup = zshrc.with_name(zshrc.name + '.catsay.bak')
            if not backup.exists():
                shutil.copy2(zshrc, backup)
        if aliases:
            zshrc.write_text(config.replace(previous_alias + '\n', alias))
        else:
            zshrc.write_text(config.rstrip('\n') + '\n\n# A little company for your terminal.\n' + alias)
    if kitty_config and 'remote_control_password catsay-screen get-text' not in kitty_text:
        if kitty_config.exists():
            backup = kitty_config.with_name(kitty_config.name + '.catsay.bak')
            if not backup.exists():
                shutil.copy2(kitty_config, backup)
        kitty_config.parent.mkdir(parents=True, exist_ok=True)
        kitty_config.write_text(kitty_text.rstrip('\n') + '\n\n# Catsay can read terminal text for --steal.\n'
                                'allow_remote_control password\nremote_control_password catsay-screen get-text\n')
        print('Kitty screen access configured. Reload Kitty config (Ctrl+Shift+F5) or open a new Kitty instance.')
    print(f'Installed {launcher}')
    if zshrc:
        print(f'Alias ready in {zshrc}: catsay (shows help; pass a message or play flag)')


if __name__ == '__main__':
    main()
