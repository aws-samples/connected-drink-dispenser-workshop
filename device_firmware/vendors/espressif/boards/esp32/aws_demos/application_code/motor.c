#include "motor.h"
#include "driver/gpio.h"

#include "FreeRTOS.h"

void motor_init(Motor motor)
{
    uint8_t in1 = (motor == MOTOR_A ? AIN1 : BIN1);
    uint8_t in2 = (motor == MOTOR_A ? AIN2 : BIN2);

    gpio_config_t conf;
    conf.intr_type = GPIO_PIN_INTR_DISABLE;
    conf.mode = GPIO_MODE_OUTPUT;
    conf.pull_down_en = 1;
    conf.pin_bit_mask = 1UL << in1;
    gpio_config(&conf);
    conf.pin_bit_mask = 1UL << in2;
    gpio_config(&conf);
}


void motor_forward(Motor motor)
{
    uint8_t in1 = (motor == MOTOR_A ? AIN1 : BIN1);
    uint8_t in2 = (motor == MOTOR_A ? AIN2 : BIN2);

    gpio_set_level(in1, 1);
    gpio_set_level(in2, 0);
}

void motor_reverse(Motor motor)
{
    uint8_t in1 = (motor == MOTOR_A ? AIN1 : BIN1);
    uint8_t in2 = (motor == MOTOR_A ? AIN2 : BIN2);

    gpio_set_level(in1, 0);
    gpio_set_level(in2, 1);
}

void motor_coast(Motor motor)
{
    uint8_t in1 = (motor == MOTOR_A ? AIN1 : BIN1);
    uint8_t in2 = (motor == MOTOR_A ? AIN2 : BIN2);

    gpio_set_level(in1, 0);
    gpio_set_level(in2, 0);
}

void motor_brake(Motor motor)
{
    configPRINTF(("Breaking the motor\r\n"));
    uint8_t in1 = (motor == MOTOR_A ? AIN1 : BIN1);
    uint8_t in2 = (motor == MOTOR_A ? AIN2 : BIN2);

    gpio_set_level(in1, 1);
    gpio_set_level(in2, 1);
}
