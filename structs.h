#ifndef STRUCTS_H
#define STRUCTS_H

typedef enum GOVERNOR {
    AUTO = 0,
    LOW,
    HIGH,
    MANUAL,
    PROFILE_PEAK
} GOVERNOR;

struct sample {
  int bat;
  int ac;
  float temp;
};

extern struct sample history[5];
extern int history_idx;
extern int power_fd;
extern char gpu_path[256];

#endif
