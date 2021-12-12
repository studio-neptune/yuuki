> :warning: Warning
>
> Due to protect the talk service of LINE, the software **never** provides any login method, for raising the development threshold.
>
> If you are the developer, we hope you have the sincere spirit only, for improving the Internet, and respect for their hard. :pray: 

## Preparing

+ Copying `config.yaml` from `config.sample.yaml`

+ Following the [guide](#configuring), configure your settings and environment in `config.yaml`.

## Configuring

Star Yuuki BOT never provides any login method for connecting LINE talk service, you need to collect the information required, for continuing.

The config file format is [YAML](https://yaml.org), please understanding the syntax, documents, tutorials, and how to write that for configuring.

### Sample Config File

This is the required information to boot the software for working correctly, and optional settings can be set by override as `config.py` listed.

```yaml
# Sample Config File for star_yuuki_bot
# Please replace setting options from `libs/config.py`

Yuuki:
  SecurityService: True
  Default_Language: en

LINE:
  Server:
    Host: https://example.com
    Command_Path: /example_path
    LongPoll_path: /example_path

  Account:
    X-Line-Application: LINE_Application_Identification
    X-Line-Access: LINE_Application_AccessKey
    User-Agent: LINE_Application_User-Agent
```

Please make sure all of information above are filled correctly.

### Optional Settings

The guide will lead you to override the settings of `config.py`.

The config file is separated as two major parts, [`Yuuki`](#Yuuki) and [`LINE`](#LINE).

#### Yuuki

| In `config.py` | Converting to `config.yaml`  |
|---|---|
| systemConfig | Yuuki |

The part is used for configuring how the software works and computes.

Taking the optional setting, `Advanced`, for example, it belongs to `systemConfig -> Advanced` as `Python dict` default in `config.py`.

So if you hope to set the option to `True`, according the converting table, the config file should be

```yaml
Yuuki:
  Advanced: True
```

The feature, `Advanced`, will be active as you set.

As the result, the new config file will be

```yaml
Yuuki:
  SecurityService: True
  Default_Language: en
  Advanced: True

LINE:
  Server:
    Host: https://example.com
    Command_Path: /example_path
    LongPoll_path: /example_path

  Account:
    X-Line-Application: LINE_Application_Identification
    X-Line-Access: LINE_Application_AccessKey
    User-Agent: LINE_Application_User-Agent
```

That is the way to config the software correctly without any programming modification. 

#### LINE

| In `config.py` | Converting to `config.yaml`  |
|---|---|
| connectInfo | LINE -> Server |
| connectHeader | LINE -> Account |

- X-Line-Application: `LINE_Application_Identification` means the Product ID for LINE server to identify the client.
- X-Line-Access: `LINE_Application_AccessKey` as known as an access token of LINE user.
- User-Agent: `LINE_Application_User-Agent` is the field to be used as HTTP header to connect LINE server.

These are the required config for connecting LINE server, that you should collect them by yourself.

As the guide part [`Yuuki`](#Yuuki) did, overriding settings as needing.

## Next

If you are ready, let's [run it up](https://github.com/star-inc/star_yuuki_bot/wiki/Execute-and-Maintain)!