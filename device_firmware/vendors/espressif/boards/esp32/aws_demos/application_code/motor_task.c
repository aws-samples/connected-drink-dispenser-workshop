#include "motor_task.h"
#include "task.h"
#include "shadow_task.h"
#include "stdio.h"
#include "led_strip/led_strip.h"
#include "stdint.h"
#include "motor.h"
#include "string.h"

#define LEDS_GPIO                 5
#define LED_STRIP_LENGTH          8U
#define LED_STRIP_RMT_INTR_NUM    19
#define LED_CHANGE_MS             100
#define LED_CHANGE_TICKS          ( LED_CHANGE_MS * configTICK_RATE_HZ / 1000 )
#define ONBOARD_LED_GPIO 2

static struct led_color_t led_strip_buf_1[ LED_STRIP_LENGTH ];
static struct led_color_t led_strip_buf_2[ LED_STRIP_LENGTH ];

#define LED_ENABLED 1

QueueHandle_t motorStatesQueue;
SemaphoreHandle_t motorTaskUpdateStateSema;

struct led_strip_t led_strip =
{
    .rgb_led_type      = RGB_LED_TYPE_WS2812,
    .rmt_channel       = RMT_CHANNEL_3,
    .rmt_interrupt_num = LED_STRIP_RMT_INTR_NUM,
    .gpio              = LEDS_GPIO,
    .led_strip_buf_1   = led_strip_buf_1,
    .led_strip_buf_2   = led_strip_buf_2,
    .led_strip_length  = LED_STRIP_LENGTH
};

void prvLedTurnOff( struct led_strip_t * led_strip,
                    int num )
{
    for( int i = 0; i < num; ++i ) /** Turn off the LEDs */
    {
        led_strip_set_pixel_rgb( led_strip, i, 0, 0, 0 );
    }

    led_strip_show( led_strip );
}

void prvLedLightColor(struct led_strip_t* led_strip, int i)
{
    configPRINTF(( "led_strip.access_semaphore is %x \n", ( size_t ) led_strip->access_semaphore ));
    hsv hsv_color = { 0, 1, 1 };
    hsv hsv_color_next = { 0, 1, 0.01 };

    hsv_color.h = 4 * i;
    hsv_color_next.h = 4 * i;

    rgb rgb_color = hsv2rgb( hsv_color );
    rgb rgb_color_next = hsv2rgb( hsv_color_next );

    led_strip_set_pixel_rgb( led_strip, i % LED_STRIP_LENGTH, rgb_color.r * 255, rgb_color.g * 255, rgb_color.b * 255 );
    led_strip_set_pixel_rgb(led_strip, (i + LED_STRIP_LENGTH - 1) % LED_STRIP_LENGTH, rgb_color_next.r * 255, rgb_color_next.g * 255, rgb_color_next.b * 255);
    led_strip_set_pixel_rgb(led_strip, (i + 1) % LED_STRIP_LENGTH, rgb_color_next.r * 255, rgb_color_next.g * 255, rgb_color_next.b * 255);

    led_strip_show( led_strip );
}

void prvLedShowNumber(struct led_strip_t* led_strip, uint8_t number, uint8_t r, uint8_t g, uint8_t b){
    prvLedTurnOff( led_strip, LED_STRIP_LENGTH );

    for (uint8_t i = 0; i < number; ++i){
        led_strip_set_pixel_rgb( led_strip, i, r, g, b);
    }
    led_strip_show( led_strip );

}

void prvLedInit(void)
{
    led_strip.access_semaphore = xSemaphoreCreateBinary();
    configPRINTF(( "led_strip.access_semaphore is %x \n", ( size_t ) led_strip.access_semaphore ));

    bool ok = led_strip_init( &led_strip );
    prvLedTurnOff( &led_strip, LED_STRIP_LENGTH );
    configPRINTF(( "Led strip initialized: %d\n", ok ));

}

void turnOn(){
    motor_forward( DEFAULT_MOTOR );
#ifdef ADDITIONAL_MOTOR
    motor_forward( ADDITIONAL_MOTOR );
#endif
    configPRINTF(( "Start the motor!" ));
}

void turnOff(){
    motor_brake( DEFAULT_MOTOR );
#ifdef ADDITIONAL_MOTOR
    motor_brake( ADDITIONAL_MOTOR );
#endif

    configPRINTF(( "Stop the motor by time passed\n" ));
}

void showCredits(struct State *state){
#if LED_ENABLED
    prvLedTurnOff( &led_strip, LED_STRIP_LENGTH );
    if (state->led_state){
        configPRINTF(( "Show credits %d, color: #%2x%2x%2x\n", state->led_ring_count, (uint8_t)state->led_ring_color.r, (uint8_t)state->led_ring_color.g, (uint8_t)state->led_ring_color.b ));
        prvLedShowNumber(&led_strip, state->led_ring_count > 8? 8 : state->led_ring_count ,
                     (uint8_t)state->led_ring_color.r, (uint8_t)state->led_ring_color.g, (uint8_t)state->led_ring_color.b);
    }
#endif
}

void xMotorTask( void * param )
{
    motorStatesQueue = xQueueCreate( 1, sizeof( struct State ) );
    motorTaskUpdateStateSema = xSemaphoreCreateBinary();
    struct State new_state = {} ;
    struct State current_state = {};
    BaseType_t status;

    #if LED_ENABLED
    prvLedInit();
    #endif

    uint32_t old_ticks = xTaskGetTickCount();
    int ticks_remained = 0;
    bool active = false; /* Flag indicating whether we stops by timeout or not */

    int i = 0;

    for( ; ; )
    {
        status = xQueueReceive( motorStatesQueue, &new_state, 0);
        if (status){
            if (new_state.requested && !active){ // We have a new dring requested
                ticks_remained = pdMS_TO_TICKS(new_state.dispense_time_ms);
                turnOn();
                active = true;
            }
            configPRINTF(("Checking for leds"));
            if (!active && (!memcmp(&current_state.led_ring_color, &new_state.led_ring_color, sizeof(new_state.led_ring_color))||
                current_state.led_state != new_state.led_state ||
                current_state.led_ring_count != new_state.led_ring_count)
                    ){
                configPRINTF(("Leds has changed, update"));
                showCredits(&new_state);
                xSemaphoreGive(motorTaskUpdateStateSema);
            }
            current_state = new_state;
        }

        if (active) {
            configPRINTF(( "tick, ticks_remained = %d\n", ticks_remained ));
            if (ticks_remained == 0){
                turnOff();
                active = false;
                showCredits(&current_state);
                xSemaphoreGive(motorTaskUpdateStateSema);
            }
            else {
#if LED_ENABLED
                prvLedLightColor(&led_strip, i);
#endif
                i = ( i + 1 ) % 80;
                int ticks_passed = ( xTaskGetTickCount() - old_ticks );
                configPRINTF(( "ticks_passed = %d\n", ticks_passed ));
                ticks_remained = ticks_remained - ticks_passed;
                ticks_remained = ticks_remained < 0 ? 0 : ticks_remained; /* Clamp it from below by zero */
            }
        }
        old_ticks = xTaskGetTickCount();
        vTaskDelay( LED_CHANGE_TICKS );

    }
}
