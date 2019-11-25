#ifndef SHADOW_TASK_H
#define SHADOW_TASK_H

#include "stdint.h"
#include "stdbool.h"

void xShadowTask( void * param );

struct State
{
    uint32_t dispense_time_ms;
    uint8_t led_ring_count;
    struct {
        uint32_t r;
        uint32_t g;
        uint32_t b;
    } led_ring_color;
    bool led_state;
    bool requested;
    char request_id[10];
    uint32_t cloud_start_timestamp_ms;
    uint32_t local_start_timestamp_ms; // Is necessary since we don't use RTC and we can only rely on FreeRTOS ticks;
};


#endif /* SHADOW_TASK_H */
