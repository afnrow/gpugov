#include "eng.h"
#include "structs.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void set_governor(char *level) {
  if (strcmp(level, governor) != 0) {
    if (power_fd < 0) {
      char full_path[512];
      snprintf(full_path, sizeof(full_path),
               "%s/power_dpm_force_performance_level", gpu_path);
      power_fd = open(full_path, O_WRONLY);
      if (power_fd < 0) {
        perror("Failed to open GPU control file");
        return;
      }
    }
    pwrite(power_fd, level, strlen(level), 0);
    strncpy(governor, level, sizeof(governor) - 1);
    governor[sizeof(governor) - 1] = '\0';
  }
}

int read_fd(int fd) {
  if (fd < 0)
    return -1;
  char buf[16];
  ssize_t bytes = pread(fd, buf, sizeof(buf) - 1, 0);
  if (bytes <= 0)
    return -1;
  buf[bytes] = '\0';
  char *endptr;
  long val = strtol(buf, &endptr, 10);
  if (buf == endptr)
    return -1;
  return (int)val;
}
