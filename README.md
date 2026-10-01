# Star Yuuki(pYthon) BOT - Yuuki

> ## WARNING: LINE will bite
>
> **Using this bot can get your LINE account banned. Permanently.**
>
> This project talks to the LINE LEGY API (LINE's private API) with
> unofficial clients. That is against the LINE Terms of Service, no
> matter how careful you are:
>
> - LINE actively detects automation and bans the accounts behind it.
> - Bans are **forever**. There is no appeal that works.
> - The bot account **and every helper account** you register are at risk.
> - Run it on throwaway accounts only. Never on your personal account.
>
> If your account gets eaten, that is on you. You have been warned.

![Version](https://img.shields.io/badge/v8-OpenSource-FF0033.svg)
![Series](https://img.shields.io/badge/syb-Series-7700FF.svg)
![License](https://img.shields.io/badge/license-MPL--2.0-FF6600.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-0066FF.svg)
![Platform](https://img.shields.io/badge/base_on-LINE-00DD00.svg)

An open-source security bot that protects LINE groups from malicious
kicks, uncontrolled invites and group-takeover attempts.

![ICON](logo.png)

## Introduction

Yuuki watches group events through a long-poll feed and reacts within
milliseconds: it rescues members who get kicked, cancels unwanted
invitations, locks down join URLs and keeps a blacklist of known
attackers.

The `v8` series is a modern rewrite of the original v6:

- single-process **asyncio** event loop, no threads or multiprocess data hacks
- decorator-based event registry (`@registry.on(OpType...)`)
- **pydantic** models and validated YAML configuration
- **FastAPI** WebAdmin with an Alpine.js console
- i18n with vue-i18n style key-value catalogues (English, Traditional Chinese)

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- LINE accounts you can afford to lose (see the warning above)

## Quick Start

```sh
# 1. Install dependencies
uv sync

# 2. Configure the bot
cp config.sample.yaml config.yaml
#    then fill in your LINE API endpoint and account credentials

# 3. Start the bot
uv run python main.py
```

The WebAdmin console (optional) is enabled with
`yuuki.webadmin_enabled: true` in `config.yaml`; the random login
password is printed at startup.

## Development

```sh
uv run pytest          # tests
uv run ruff check .    # lint
uv run basedpyright   # type check
```

## Logo Copyright

Copyright of `logo.png` belongs to
"[©川原 礫／ASCII Media Works／SAO Project](https://www.aniplex.co.jp)"
and its artists.

> (c) Neptune Studio.
