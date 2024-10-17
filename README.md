# Keyboard usage logger

## Description

A CLI to log all of the keypresses categorized into ngrams.
This can be used as part of a corpus to create a personalized keyboard layout,
or to track hotkey usage (with window Managers, tmux, vim, etc) and find bad habits
or optimize your workflow.

Currently supports [genkey](https://github.com/semilin/genkey).
Support for other analyzers such as Oxeylyzer to come.

<img width="667" alt="image" src="https://github.com/user-attachments/assets/1f4fc03b-2ce2-4552-a6af-ff96a2c5a078">
<img width="757" alt="image" src="https://github.com/user-attachments/assets/b1d16057-677f-4e03-acf2-b2dd94193cac">


## Table of contents

<!-- toc -->

- [⚙️ Installation](#%E2%9A%99%EF%B8%8F-installation)
- [🛠️ Suggested Usage](#%F0%9F%9B%A0%EF%B8%8F-suggested-usage)
- [💬 Notes](#%F0%9F%92%AC-notes)
- [🚀 Features](#%F0%9F%9A%80-features)
- [🤝 Contributing](#%F0%9F%A4%9D-contributing)

<!-- tocstop -->

## ⚙️ Installation

This CLI requires Python 3.12+
To start just clone the repo and cd into the project folder.

```sh
git clone https://github.com/ammon134/usage-tracker
cd usage-tracker
```

Optional but recommended:
start an virtual env so that this script is contained in this workspace only.

```sh
python3 -m venv .venv
source .venv/bin/activate
```

In the project root folder install the script.

```sh
pip install .
```

## 🛠️ Suggested Usage

In the project root folder run

```sh
klgr run -n <session-name>
```

To stop the script and save results, the current hard-coded behavior is to
use command `.end` in the terminal where the script is running.

```sh
Command: .end
```

Expect `logger.db` created in the root of the project folder
that contains logged usage.

To view logged data

```sh
klgr view <session-name> -n letters
```

If you're using this to track keypresses in your workflow (with tile window manager,
vim, tmux, etc), you can view aggregated stats for keypresses with mods, including
special keys like \<space\>, \<enter\>, \<backspace\>.

```sh
klgr view <session-name> -n letters -a
```

To export logged data to use with genkey

```sh
klgr export <session-name>
```

Run --help to explore all features and flags.

```sh
klgr --help
```

## 💬 Notes

In MacOS, you will have to give the terminal appropriate access.
[See other limitations here.](https://pynput.readthedocs.io/en/latest/limitations.html)

## 🚀 Features

- Logs all keypresses and outputs to a local database, save every 60 seconds.
- All keypresses are logged into unigrams, diagrams, trigrams and skipgrams.
  (Skipgrams in genkey's logic for now).
- View command to peak at the logged stats so far.
- Export command to output corpus json file in genkey format.
- Logging are saved into sessions.
- On macOS, when pressing opt+key the original key value will be tracked. For example,
  opt+j normally becomes ∆, but j will be logged with opt as mod instead. This
  should help with tracking hotkeys with WMs or in neovim.
- On all platforms, the unshifted value will be logged. For example, for ctrl+shift+\[,
  \[ will be logged with ctrl and shift as mods.

## 🤝 Contributing

If you'd like to contribute, please fork the repository and open a pull request
to the `main` branch.

For local development, start an virtual env so that this script is contained in
this workspace, and install dependencies.

```sh
python3 -m venv .cli_venv
source .cli_venv/bin/activate
pip install -r requirements.txt
```

Install with --editable flag allows the latest changes to apply without rebuilding.

```sh
pip install -e .
```
