#include "structs.h"
#include "eng.h"

#define TEMP_CRITICAL 85.0
#define TEMP_SPIKE 5.0
#define BAT_CRITICAL 20

void analyze() {
  static enum GOVERNOR current_state;
  float sum_temp = 0;
  int newest_idx = (history_idx - 1 + 5) % 5;
  int oldest_idx = history_idx;
  for (int i = 0; i < 5; i++) {
    sum_temp += history[i].temp;
  }
  float avg_temp = sum_temp / 5.0;
  float thermal_velocity = history[newest_idx].temp - history[oldest_idx].temp;
  enum GOVERNOR next_state;
  if (avg_temp > TEMP_CRITICAL) {
    next_state = LOW;
  } else if (thermal_velocity > TEMP_SPIKE && avg_temp > 70.0) {
    next_state = AUTO;
  } else if (history[newest_idx].ac == 1) {
    next_state = HIGH;
  } else {
    if (history[newest_idx].bat < BAT_CRITICAL) {
      next_state = LOW;
    } else {
      next_state = AUTO;
    }
  }
  if (next_state != current_state) {
    current_state = next_state;
    switch (next_state) {
    case LOW:
      set_governor("low");
      break;
    case HIGH:
      set_governor("high");
      break;
    case AUTO:
      set_governor("auto");
      break;
    default:
      set_governor("auto");
      break;
    }
  }
}
