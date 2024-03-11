# Keyboard usage logger

## Description

Utility to log all of the keypresses categorized into ngrams.
~~while using nvim, mostly things that happen outside of insert mode.~~
This will be used as part of a corpus to create a keyboard layout
that is personalized and tailored to my kind of usage.

## Installation

This was written in python 3.12 so make sure you have python 3.12 installed.
To start just clone the repo and cd into the project folder.

```sh
git clone https://github.com/ammon134/vim-usage-logger
cd vim-usage-logger
```

Optional but recommended:
start an virtual env so that this script is contained in this workspace only.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
```

In the project root folder install the script.

```sh
pip install .
```

## Usage

In the project root folder run

```sh
vim-logger
```

To stop the script the current hard-coded behavior is to
use command `.end` in the terminal where the script is running.

```sh
Command: .end
```

Expect `logger.db` created in the root of the project folder
that contains logged usage.

## Notes

In MacOS, you will have to give the terminal appropriate access.
[See other limitations here.](https://pynput.readthedocs.io/en/latest/limitations.html)

## Features

- [x] A module with setuptools
- [x] Logs all keypresses and outputs to a local database, save every 60 seconds.
- [x] All keypresses should be logged in unigrams, diagrams and trigrams.

## TODO

- [ ] Keypresses should also be processed into skipgrams based on genkey logic,
      using the 1gram list.
  - [ ] Create table of log_1gram for each session
  - [ ] At the end of each session, process log_1gram into skipgram and save
        into table skipgram. Table skipgram should have an aggregate entry?
- [ ] Command to convert logged info to json file format that genkey understands
- [ ] Connects with neovim and only collects keypresses in Normal mode
- [ ] Auto starts on OS starts.
