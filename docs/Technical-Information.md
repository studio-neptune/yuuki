Star Yuuki BOT is the software to deploy an automated management service of group for [LINE](http://line.me) platform via their private API with `Apache Thrift Compact Protocol`.

The new programming structure since the version `v6.5` is based on `NightCrazy`, supporting multiprocessing, and getting flexiable for extending.

There are two modes, choosing the compatible one for your environment.

- [Legacy](#legacy-mode) is used for some old or performance losing devices.
- [Advanced](#advanced-mode) will enable multiprocessing for improving the compute speed.

To configure the mode for executing, please read [`Configure`](https://github.com/star-inc/star_yuuki_bot/wiki/Configure) for getting how to set it up.

## Legacy Mode

The mode takes only one thread for running, and [WebAmin](https://github.com/star-inc/star_yuuki_bot#webadmin) or any extra features will be shutdown automatically, no matter if you already turn them on.

### Flow Chart

![Legacy Mode](https://line.starinc.xyz/wp-content/uploads/2020/11/Legacy.png)

## Advanced Mode

This is used as multiprocessing support for improving performance while computing, and provides some extra features.

### Flow Chart

![Advanced Mode](https://line.starinc.xyz/wp-content/uploads/2020/11/Advanced.png)
