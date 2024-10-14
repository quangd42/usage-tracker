# Keyboard usage logger

## Description

Utility to log all of the keypresses categorized into ngrams.
~~while using nvim, mostly things that happen outside of insert mode.~~
This will be used as part of a corpus to create a keyboard layout
that is personalized and tailored to my kind of usage.

Currently supports [genkey](https://github.com/semilin/genkey).
Support for other analyzers to come.

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
klgr
```

To stop the script and save results, the current hard-coded behavior is to
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

- [x] Logs all keypresses and outputs to a local database, save every 60 seconds.
- [x] All keypresses are logged into unigrams, diagrams, trigrams and skipgrams.
      (Skipgrams in genkey's logic for now).
- [x] View command to peak at the logged stats so far.
- [x] Save command to output corpus json file in genkey format.
- [x] Logging are saved into sessions.

## Development

Start an virtual env so that this script is contained in this workspace only,
and install dependencies.

```sh
python3 -m venv .cli_venv
source .cli_venv/bin/activate
pip install -r requirements.txt
```

For local development, install with --editable flag.

```sh
pip install -e .
```
