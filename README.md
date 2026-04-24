# GPUGOV

An lightweight daemon for AMD GPUS that intelligently manages GPU performance levels based on thermal velocity, AC status, battery levels and GPU temperatures.

## Features
- **Predictive Throttling**: Monitors temperature spikes to throttle before hitting limiters.
- **Hysteresis Logic**: Prevents state-flapping to ensure stable FPS.
- **Ultra-Low Overhead**: Uses raw syscalls (`pread`/`pwrite`) for very low cpu usage.

## Installation
```bash
chmod +x install.sh
sudo ./install.sh
```
## Uninstalling
```bash
make clean
```
