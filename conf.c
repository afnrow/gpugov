#include "conf.h"
#include <stdio.h>
#include <string.h>

float temp_critical = 85.0;
int bat_critical = 20;
float thermal_velocity = 5.0;

void load_conf() {
  FILE *f = fopen("/etc/gpugov.conf", "r");
  if (f == NULL)
    return;
  char line[128];
  while (fgets(line, sizeof(line), f)) {
    if (line[0] == '#' || line[0] == '\n')
      continue;
    if (strstr(line, "temp_critical=")) {
      sscanf(line, "temp_critical=%f", &temp_critical);
    } else if (strstr(line, "bat_critical=")) {
      sscanf(line, "bat_critical=%d", &bat_critical);
    } else if (strstr(line, "thermal_velocity=")) {
      sscanf(line , "thermal_velocity=%f", &thermal_velocity);
    }
  }
  fclose(f);
}
