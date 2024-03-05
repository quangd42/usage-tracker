# Keyboard usage

## Description

Utility to log all of the keypresses while using nvim, mostly things that happen outside of insert mode.

## TODO

- [x] A module with setuptools
- [x] Logs all keypresses and outputs to a txt file.
- [ ] Converts to the format that genkey understands.
  - [x] Converts space key to space?
- [ ] Allows a timer to auto turn off.
- [ ] Filters out keypresses in insert mode.
  - [ ] Connects with neovim somehow to only collect info on neovim
  - [ ] Only collect info when neovim is not in insert mode
