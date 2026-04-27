#ifndef ENG_H
#define ENG_H

#define MAX_SAMPLES 5
#define TEMP_LIMIT 85
#define THERMAL_VEL_LIMIT 3.0

void set_governor(char* level);
int read_fd(int fd);

extern char governor[16];

#endif
