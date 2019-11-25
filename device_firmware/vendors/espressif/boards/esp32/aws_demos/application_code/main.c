/*
 * Amazon FreeRTOS V1.4.7
 * Copyright (C) 2018 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * http://aws.amazon.com/freertos
 * http://www.FreeRTOS.org
 */

#include "iot_config.h"

/* FreeRTOS includes. */

#include "FreeRTOS.h"
#include "task.h"

/* Demo includes */
#include "aws_demo.h"
#include "aws_dev_mode_key_provisioning.h"

/* AWS System includes. */
#include "bt_hal_manager.h"
#include "iot_system_init.h"
#include "iot_logging_task.h"
#include "iot_config.h"
#include "iot_init.h"
#include "iot_demo_logging.h"

#include "nvs_flash.h"

#include "FreeRTOS_Sockets.h"

#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_interface.h"
#include "esp_bt.h"
#if CONFIG_NIMBLE_ENABLED == 1
#include "esp_nimble_hci.h"
#else
#include "esp_gap_ble_api.h"
#include "esp_bt_main.h"
#endif

#include "driver/uart.h"
#include "aws_application_version.h"

#include "iot_network_manager_private.h"

#include "motor.h"
#include "motor_task.h"
#include "shadow_task.h"


/* Logging Task Defines. */
#define mainLOGGING_MESSAGE_QUEUE_LENGTH ( 32 )
#define mainLOGGING_TASK_STACK_SIZE ( configMINIMAL_STACK_SIZE * 4 )
#define mainDEVICE_NICK_NAME "Espressif_Demo"

static TaskHandle_t xShadowTaskHandle;
static TaskHandle_t xMotorTaskHandle;


/* A semaphore that is responsible for network events */
static IotSemaphore_t xNetworkSemaphore = {};

/* Previously connected network */
static uint32_t puConnectedNetwork = AWSIOT_NETWORK_TYPE_NONE;

static IotNetworkManagerSubscription_t subscription = IOT_NETWORK_MANAGER_SUBSCRIPTION_INITIALIZER;

/* Static arrays for FreeRTOS+TCP stack initialization for Ethernet network connections
 * are use are below. If you are using an Ethernet connection on your MCU device it is
 * recommended to use the FreeRTOS+TCP stack. The default values are defined in
 * FreeRTOSConfig.h. */

/**
 * @brief Initializes the board.
 */
static void prvMiscInitialization( void );

int vInitialize();
/*-----------------------------------------------------------*/

static void initPeripheral(){
    motor_init(DEFAULT_MOTOR);
#ifdef ADDITIONAL_MOTOR
    motor_init(ADDITIONAL_MOTOR);
#endif
}

/*-----------------------------------------------------------*/
bool bLoggingInitialized = false;

/**
 * @brief Application runtime entry point.
 */
int app_main( void )
{
    /* Perform any hardware initialization that does not require the RTOS to be
     * running.  */

    prvMiscInitialization();
    initPeripheral();

    if( SYSTEM_Init() == pdPASS )
    {
        /* A simple example to demonstrate key and certificate provisioning in
         * microcontroller flash using PKCS#11 interface. This should be replaced
         * by production ready key provisioning mechanism. */
        vDevModeKeyProvisioning();

        ESP_ERROR_CHECK( esp_bt_controller_mem_release( ESP_BT_MODE_CLASSIC_BT ) );
        ESP_ERROR_CHECK( esp_bt_controller_mem_release( ESP_BT_MODE_BLE ) );

        if( vInitialize() == pdPASS )
        {
            configPRINTF( ( "Connected to the network\r\n" ) );
            xTaskCreate(xMotorTask, "mt", 12000, NULL, tskIDLE_PRIORITY + 5, &xMotorTaskHandle);
            xTaskCreate(xShadowTask, "ShadowTask", 12000, NULL, tskIDLE_PRIORITY + 5, &xShadowTaskHandle);
        }
    }

    /* Start the scheduler.  Initialization that requires the OS to be running,
     * including the WiFi initialization, is performed in the RTOS daemon task
     * startup hook. */
    /* Following is taken care by initialization code in ESP IDF */
    /* vTaskStartScheduler(); */
    return 0;
}

/*-----------------------------------------------------------*/
extern void vApplicationIPInit( void );
static void prvMiscInitialization( void )
{
    /* Initialize NVS */
    esp_err_t ret = nvs_flash_init();

    if( ( ret == ESP_ERR_NVS_NO_FREE_PAGES ) || ( ret == ESP_ERR_NVS_NEW_VERSION_FOUND ) )
    {
        ESP_ERROR_CHECK( nvs_flash_erase() );
        ret = nvs_flash_init();
    }

    ESP_ERROR_CHECK( ret );

    /* Create tasks that are not dependent on the WiFi being initialized. */
    xLoggingTaskInitialize( mainLOGGING_TASK_STACK_SIZE,
                            tskIDLE_PRIORITY + 5,
                            mainLOGGING_MESSAGE_QUEUE_LENGTH );

    vApplicationIPInit();
}

/*-----------------------------------------------------------*/

extern void esp_vApplicationTickHook();
void IRAM_ATTR vApplicationTickHook()
{
    esp_vApplicationTickHook();
}

/*-----------------------------------------------------------*/
extern void esp_vApplicationIdleHook();
void vApplicationIdleHook()
{
    esp_vApplicationIdleHook();
}

/*-----------------------------------------------------------*/

void vApplicationDaemonTaskStartupHook( void )
{
}

/*-----------------------------------------------------------*/

void vApplicationIPNetworkEventHook( eIPCallbackEvent_t eNetworkEvent )
{
    uint32_t ulIPAddress, ulNetMask, ulGatewayAddress, ulDNSServerAddress;
    system_event_t evt;

    if( eNetworkEvent == eNetworkUp )
    {
        /* Print out the network configuration, which may have come from a DHCP
         * server. */
        FreeRTOS_GetAddressConfiguration(
                &ulIPAddress,
                &ulNetMask,
                &ulGatewayAddress,
                &ulDNSServerAddress );

        evt.event_id = SYSTEM_EVENT_STA_GOT_IP;
        evt.event_info.got_ip.ip_changed = true;
        evt.event_info.got_ip.ip_info.ip.addr = ulIPAddress;
        evt.event_info.got_ip.ip_info.netmask.addr = ulNetMask;
        evt.event_info.got_ip.ip_info.gw.addr = ulGatewayAddress;
        esp_event_send( &evt );
    }
}

void vNetworkChangedCB( uint32_t ulNetworkType,
                        AwsIotNetworkState_t xNetworkState,
                        void * pvContext )
{
    if( ( xNetworkState == eNetworkStateEnabled ) && ( puConnectedNetwork == AWSIOT_NETWORK_TYPE_NONE ) )
    {
        puConnectedNetwork = ulNetworkType;
        IotSemaphore_Post( &xNetworkSemaphore );
    }
}


int vInitialize()
{
    {
        int status = EXIT_SUCCESS;
        bool commonLibrariesInitialized = false;
        bool semaphoreCreated = false;

        /* Initialize common libraries required by network manager and demo. */
        if( IotSdk_Init() == true )
        {
            commonLibrariesInitialized = true;
        }
        else
        {
            IotLogInfo( "Failed to initialize the common library." );
            status = EXIT_FAILURE;
        }

        if( status == EXIT_SUCCESS )
        {
            if( AwsIotNetworkManager_Init() != pdTRUE )
            {
                IotLogError( "Failed to initialize network manager library." );
                status = EXIT_FAILURE;
            }
        }

        if( status == EXIT_SUCCESS )
        {
            /* Create semaphore to signal that a network is available for the demo. */
            if( IotSemaphore_Create( &xNetworkSemaphore, 0, 1 ) != true )
            {
                IotLogError( "Failed to create semaphore to wait for a network connection." );
                status = EXIT_FAILURE;
            }
            else
            {
                semaphoreCreated = true;
            }
        }

        if( status == EXIT_SUCCESS )
        {
            /* Subscribe for network state change from Network Manager. */
            if( AwsIotNetworkManager_SubscribeForStateChange( configENABLED_NETWORKS,
                                                              vNetworkChangedCB,
                                                              NULL,
                                                              &subscription ) != pdTRUE )
            {
                IotLogError( "Failed to subscribe network state change callback." );
                status = EXIT_FAILURE;
            }
        }

        /* Initialize all the  networks configured for the device. */
        if( status == EXIT_SUCCESS )
        {
            configPRINTF( ( "Connecting to network\r\n" ) );
            if( AwsIotNetworkManager_EnableNetwork( configENABLED_NETWORKS ) != configENABLED_NETWORKS )
            {
                IotLogError( "Failed to intialize all the networks configured for the device." );
                configPRINTF( ( " .... RESETING ............ \r\n" ) );
                esp_restart();
                status = EXIT_FAILURE;
            }
        }

        if( status == EXIT_SUCCESS )
        {
            /* Wait for network configured for the demo to be initialized. */
            puConnectedNetwork = AwsIotNetworkManager_GetConnectedNetworks() & configENABLED_NETWORKS;

            if( puConnectedNetwork == AWSIOT_NETWORK_TYPE_NONE )
            {
                /* Network not yet initialized. Block for a network to be intialized. */
                IotLogInfo( "No networks connected for the demo. Waiting for a network connection. " );
                IotSemaphore_Wait( &xNetworkSemaphore );
                puConnectedNetwork = AwsIotNetworkManager_GetConnectedNetworks() & configENABLED_NETWORKS;
            }
        }

        if( status == EXIT_FAILURE )
        {
            configPRINTF( ( " .... RESETING ............ \r\n" ) );
            esp_restart();

            if( semaphoreCreated == true )
            {
                IotSemaphore_Destroy( &xNetworkSemaphore );
            }

            if( commonLibrariesInitialized == true )
            {
                IotSdk_Cleanup();
            }
        }

        return status == 0 ? pdPASS : pdFAIL;
    }
}
