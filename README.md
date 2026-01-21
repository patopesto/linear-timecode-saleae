# Linear Timecode Analyser

A LTC Analyser for Saleae Logic 2 software.

**Note**: This analyser only works on a LTC signal in a digital channel.


## Getting started

This is a [High-Level Analyser](https://support.saleae.com/product/user-guide/extensions-apis-and-sdks/extensions/high-level-analyzer-extensions).

1. You first need to add a Manchester analyser with the following settings:
- Mode: Bi-Phase Mark Code (FM1)
- Bit Rate: varies depending on FPS:
    - LTC 24fps: 1920 bit/s
    - LTC 25fps: 2000 bit/s
    - LTC 29.97 or 30fps: 2400 bit/s
- Bits per frame: 1 bit
- Significant bit: Least Significant Bit Sent First
- Preambule bits to ignore: 0

2. Add this LTC analyser with the input set to the Manchester analyser setup above.


## Development

1. Clone this repository.
2. In Logic 2, `Extenstions > ⋮ (top-right menu) > Load Existing Extension`, and choose the directory where you cloned this repository.


## Reference

- Saleae [API documentation](https://support.saleae.com/product/user-guide/extensions-apis-and-sdks/extensions/api-documentation).
- Linear Timecode [specification](https://ieeexplore.ieee.org/document/7291029) [wikipedia](https://en.wikipedia.org/wiki/Linear_timecode).

  