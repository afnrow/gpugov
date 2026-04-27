#ifndef STATS_H
#define STATS_H

#include "structs.h"

#define STATS_PATH "/run/gpugov.stats"

void write_stats();
void cleanup_stats();

#endif
