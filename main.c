#include "analyze.h"
#include "conf.h"
#include "eng.h"
#include "stats.h"
#include "structs.h"
#include <dirent.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

volatile sig_atomic_t running = 1;
volatile sig_atomic_t reload_config = 0;
void handle_sig(int sig) {
  if (sig == SIGHUP)
    reload_config = 1;
  else if (sig == SIGINT || sig == SIGTERM)
    running = 0;
}

char gpu_path[256] = "";
char bat_path[256] = "";
char ac_path[256] = "";
char temp_path[256] = "";

int power_fd = -1;
int ac_fd = -1;
int battery_fd = -1;
int gpu_temp_fd = -1;

struct sample history[5];
int history_idx = 0;

void discover_paths() {
  for (int i = 0; i <= 9; i++) {
    char control[512];
    snprintf(control, sizeof(control),
             "/sys/class/drm/card%d/device/power_dpm_force_performance_level",
             i);
    if (access(control, F_OK) == 0) {
      snprintf(gpu_path, sizeof(gpu_path), "/sys/class/drm/card%d/device", i);
      break;
    }
  }
  DIR *d = opendir("/sys/class/power_supply");
  if (d) {
    struct dirent *dir;
    while ((dir = readdir(d)) != NULL) {
      if (dir->d_name[0] == '.')
        continue;
      if ((strstr(dir->d_name, "AC") ||
          strstr(dir->d_name, "ADP")) && ac_path[0] == '\0')
        snprintf(ac_path, sizeof(ac_path), "/sys/class/power_supply/%s/online",
                 dir->d_name);
      if (strstr(dir->d_name, "BAT") && bat_path[0] == '\0')
        snprintf(bat_path, sizeof(bat_path),
                 "/sys/class/power_supply/%s/capacity", dir->d_name);
    }
    closedir(d);
  }
  char hwmon_base[512];
  snprintf(hwmon_base, sizeof(hwmon_base), "%s/hwmon", gpu_path);
  DIR *hd = opendir(hwmon_base);
  if (hd) {
    struct dirent *hdir;
    while ((hdir = readdir(hd)) != NULL) {
      if (hdir->d_name[0] == 'h') {
        snprintf(temp_path, sizeof(temp_path), "%s/%s/temp1_input", hwmon_base,
                 hdir->d_name);
        break;
      }
    }
    closedir(hd);
  }
}

void write_sample(float temp, int bat, int ac) {
  history[history_idx].temp = temp;
  history[history_idx].ac = ac;
  history[history_idx].bat = bat;
  history_idx = (history_idx + 1) % 5;
}

void init_data() {
  if (gpu_temp_fd < 0 && temp_path[0] != '\0') {
    gpu_temp_fd = open(temp_path, O_RDONLY);
  }
  if (gpu_temp_fd < 0) {
    char temp[512];
    snprintf(temp, sizeof(temp), "%s/temp1_input", gpu_path);
    gpu_temp_fd = open(temp, O_RDONLY);
  }
  int temp = read_fd(gpu_temp_fd);
  if (ac_fd < 0)
    ac_fd = open(ac_path, O_RDONLY);
  int ac = read_fd(ac_fd);
  if (battery_fd < 0)
    battery_fd = open(bat_path, O_RDONLY);
  int bat = read_fd(battery_fd);
  write_sample((float)temp / 1000.0, bat, ac);
}

int main() {
  signal(SIGHUP, handle_sig);
  signal(SIGTERM, handle_sig);
  signal(SIGINT, handle_sig);
  load_conf();
  discover_paths();
  struct timespec ts = {.tv_sec = 2, .tv_nsec = 0};
  for (int i = 0; i < 5; i++) {
    init_data();
  }
  while (running == 1) {
    if (reload_config) {
      load_conf();
      reload_config = 0;
    }
    init_data();
    analyze();
    write_stats();
    nanosleep(&ts, NULL);
  }
  close(gpu_temp_fd);
  close(ac_fd);
  close(power_fd);
  close(battery_fd);
  remove(STATS_PATH);
  return 0;
}
