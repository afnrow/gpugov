#include "stats.h"
#include "eng.h"
#include "structs.h"
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>

static FILE *stats_f = NULL;

void write_stats() {
  if (stats_f == NULL) {
    const char *path = "/run/gpugov.stats";
    stats_f = fopen(path, "w");
    if (stats_f == NULL) {
      return;
    }
    chmod(path, 0644);
  }
  rewind(stats_f);
  int newest = (history_idx - 1 + 5) % 5;
  fprintf(stats_f, "temp=%.2f\n", history[newest].temp);
  fprintf(stats_f, "bat=%d\n", history[newest].bat);
  fprintf(stats_f, "ac=%d\n", history[newest].ac);
  fprintf(stats_f, "mode=%-16s\n", governor);
  ftruncate(fileno(stats_f), ftell(stats_f));
  fflush(stats_f);
}

void cleanup_stats() {
  if (stats_f != NULL) {
    fclose(stats_f);
    stats_f = NULL;
  }
}
