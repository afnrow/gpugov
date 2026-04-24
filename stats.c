#include "stats.h"
#include <stdio.h>
#include <sys/stat.h>

void write_stats() {
  const char *path = "/run/gpugov.stats";
  FILE *f = fopen(path, "w");
  if (f == NULL) {
    return;
  }
  int newest = (history_idx - 1 + 5) % 5;
  fprintf(f, "temp=%.2f\n", history[newest].temp);
  fprintf(f, "bat=%d\n", history[newest].bat);
  fprintf(f, "ac=%d\n", history[newest].ac);
  const char *mode_name = "AUTO";
  fprintf(f, "mode=%s\n", mode_name);
  fclose(f);
  chmod(path, 0644);
}
