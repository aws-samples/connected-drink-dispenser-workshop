#ifndef __MOTOR_H
#define __MOTOR_H

#define AIN1    34
#define AIN2    35
#define BIN1    12
#define BIN2    14

typedef enum
{
    MOTOR_A, MOTOR_B
} Motor;

#define DEFAULT_MOTOR    MOTOR_B
#define ADDITIONAL_MOTOR MOTOR_A

/**
 * @brief Initializes the motor
 * @param motor Which motor to initialize
 */
void motor_init( Motor motor );

/**
 * @brief Runs the motor in the forward mode
 * @param motor Which motor to start
 */
void motor_forward( Motor motor );

/**
 * @brief Runs the motor in the reverse mode
 * @param motor Which motor to reverse
 */
void motor_reverse( Motor motor );

/**
 * @brief Coasts the motor (the motor stops slowly)
 * @param motor Which motor to coast
 */
void motor_coast( Motor motor );

/**
 * @brief Brakes the motor (the motor stops abruptly)
 * https://www.allaboutcircuits.com/technical-articles/difference-slow-decay-mode-fast-decay-mode-h-bridge-dc-motor-applications/
 * @param motor Which motor to brake
 */
void motor_brake( Motor motor );

#endif /* ifndef __MOTOR_H */
