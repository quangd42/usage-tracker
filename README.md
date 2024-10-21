# usage-tracker

## Description

A flexible plugin to log all of the keypresses categorized into ngrams.
This can be used as part of a corpus to create a personalized keyboard layout,
or to track hotkey usage (with window Managers, tmux, etc) and find bad habits
or optimize your workflow.

See more details in the [help file](https://github.com/quangd42/usage-tracker/blob/main/doc/utracker.txt).

---

There's a CLI that is a more general purpose version with the same functionalities
plus some niceties [here](https://github.com/quangd42/usage-tracker/tree/cli-main).

## Requirements

- Neovim 0.7+
- Python 3.12+

## Table of contents

<!-- toc -->

- [⚙️ Installation](#%E2%9A%99%EF%B8%8F-installation)
- [🛠️ Suggested Usage](#%F0%9F%9B%A0%EF%B8%8F-suggested-usage)
- [💬 Notes](#%F0%9F%92%AC-notes)
- [🚀 Features](#%F0%9F%9A%80-features)
  * [Keypress tracking](#keypress-tracking)
  * [Alternative Keyboard Layout optimizing](#alternative-keyboard-layout-optimizing)
- [🤝 Contributing](#%F0%9F%A4%9D-contributing)

<!-- tocstop -->

## ⚙️ Installation

You can use your favorite plugin manager. For example, with `lazy.nvim`

```lua
{
  "quangd42/usage-tracker",
  build = ":UpdateRemotePlugins",
}
```

**Important:** Post-install, you will need to run `:UpdateRemotePlugins` if the
plugin manager hasn't done so for you.

**Note:** Python provider for nvim is required. If you run into issue with the provider,
try following [this guide](https://neovim.io/doc/user/provider.html#_python-integration)
to install `pynvim` and configure the provider.

This plugin also depends on `pynput` and will try to install it automatically,
but if it fails you will need to install it yourself, similarly to `pynvim`.

```sh
python3 -m pip install --user --upgrade pynvim pynput
```

## 🛠️ Suggested Usage

The exposed commands are pretty straightforward:

```Vimscript
UTrackerRun
UTrackerStop
UTrackerPause
UTrackerResume
UTrackerExport
```

So you can setup your plugin like so

```lua
{
  "quangd42/usage-tracker",
  build = ":UpdateRemotePlugins",
  keys = {
    {
      "<leader>lr",
      "<cmd>UTrackerRun<cr>",
      desc = "Run Tracker",
    },
    {
      "<leader>ls",
      "<cmd>UTrackerStop<cr>",
      desc = "End Tracker",
    },
    {
      "<leader>le",
      "<cmd>UTrackerExport<cr>",
      desc = "Export Tracked Data",
    },
  },
}
```

Without further setup, the plugin will track all keypresses as long as nvim is running.

To narrow down what you want to track, you can set up autocmds.
Here's my setup to track all keypresses while inside nvim except in insert mode.

```lua

local utracker = vim.api.nvim_create_augroup("UTracker", { clear = true })
-- Pause the tracker when nvim loses focus, or when you enter Insert mode
vim.api.nvim_create_autocmd({ "FocusLost", "InsertEnter" }, {
 group = utracker,
 callback = function()
  vim.cmd("UTrackerPause")
 end,
})
-- ... and resume when you're back in nvim as long as you're not in Insert mode
vim.api.nvim_create_autocmd("FocusGained", {
 group = utracker,
 callback = function()
  local current_mode = vim.api.nvim_get_mode()
  if current_mode.mode ~= "i" then
   vim.cmd("UTrackerResume")
  end
 end,
})
-- ... or when you're out of Insert mode
vim.api.nvim_create_autocmd("InsertLeave", {
 group = utracker,
 callback = function()
  vim.cmd("UTrackerResume")
 end,
})
```

You may be interested in `ModeChanged` event `:h ModeChanged` for more flexibility.
Beware that these events are very expensive.

If the pause and resume autocmds are too noisy, you can add `silent`.

```lua
-- for example
vim.cmd("silent UTrackerResume")
```

All logged data is saved in `utracker` in your `data` directory `:echo stdpath('data')`

**_For AKL members_**

`UTrackerExport` exports logged data into a json file that genkey can use as corpus.

## 💬 Notes

In MacOS, you will have to give the terminal appropriate access.
[See other limitations here.](https://pynput.readthedocs.io/en/latest/limitations.html)

## 🚀 Features

### Keypress tracking

- Logs all keypresses to a local database, under a session name if specified.
- On macOS, when pressing opt+key the original key value will be tracked. For example,
  opt+j normally becomes ∆, but j will be logged with opt as mod instead. This
  should help with tracking hotkeys with WMs or in neovim.
- On all platforms, the unshifted value will be logged. For example, for ctrl+shift+\[,
  \[ will be logged with ctrl and shift as mods.

### Alternative Keyboard Layout optimizing

- Currently supports [genkey](https://github.com/semilin/genkey). Support for other analyzers such as Oxeylyzer to come.
- All keypresses are logged into unigrams, diagrams, trigrams and skipgrams.
  (Skipgrams in genkey's logic for now).
- Export command to output corpus json file in genkey format.

## 🤝 Contributing

If you'd like to contribute, please fork the repository and open a pull request
to the `main` branch.

If you have questions, feel free to open a new issue.
