/*
 * Amazon FreeRTOS Shadow Demo V1.2.3
 * Copyright (C) 2017 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
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


#include "shadow_task.h"


/* FreeRTOS includes */
#include "FreeRTOS.h"
#include "FreeRTOSConfig.h"
#include "task.h"
#include "queue.h"
/* AWS libs */
#include "aws_clientcredential.h"
#include "aws_shadow.h"
#include "iot_mqtt_agent.h"

#include <string.h>

#include "semphr.h"
#include "json.h"
#include "driver/gpio.h"
#include "motor.h"
#include "motor_task.h"

/* Timeout for connection to the MQTT broker (300 milliseconds) */
#define MQTT_TIMEOUT                  ( 150 )
/* Send buffer size */
#define SEND_BUFFER_SIZE              1024
/* Maximum number of tokens that can be contained in a JSON document */
#define MAX_JSON_TOKENS               172
/* Wait timeout for update queue */
#define UPDATE_TIMEOUT                50
/* Update queue size */
#define UPDATE_QUEUE_SIZE             5
/* Defines for parsing helpers */
#define NO_SUCH_KEY                   ( -1 )

#define DEFAULT_DISPOSE_DURATION      2

#define SHADOW_UPDATE_PERIOD_MS       1 * 1000

#define TICKS_TO_MS(ticks) (uint32_t)(ticks * 1000 / configTICK_RATE_HZ)

/* Handle of the shadwow client */
static ShadowClientHandle_t xClientHandle;

char buffer[ SEND_BUFFER_SIZE ];

static struct State current_state = { DEFAULT_DISPOSE_DURATION, 0, {255, 255, 255}, false, false, {}, 0, 0};

/* Template for the reported JSON */
/* the %s under dispense_time_ms holds the "response" object */
/* We set the request object to null in desired state to clear the request so */
/* it won't trigger a second dispense. */
static const char shadowReportJSon[] =
        "{"
        "   \"state\":{"
        "      \"reported\":{"
        "         \"led_ring\":{"
        "            \"count\":%d,"
        "            \"color\":\"#%02X%02X%02X\""
        "         },"
        "         \"led\":\"%s\","
        "         \"dispense_time_ms\":%u"
        "%s"
        "      },"
        "      \"desired\":{"
        "        \"request\":null"
        "      }"
        "   },"
        "\"clientToken\": \"token-%d\""
        "}";

static const char shadowResponseJSon[] =
        ",\"response\":{"
        "\"command\":\"dispense\","
        "\"requestId\":\"%s\","
        "\"result\":\"%s\","
        "\"timestamp\":%u"
        "}";

static void prvShadowResponseBuild(struct State state, bool finished){
    char response_buffer[256] = "";
    TickType_t current_tick_count  = xTaskGetTickCount();
    if (finished){
        uint32_t ms_passed = TICKS_TO_MS(current_tick_count) - state.local_start_timestamp_ms;
        sprintf(response_buffer, shadowResponseJSon, state.request_id, "success", state.cloud_start_timestamp_ms + ms_passed);
    }

    sprintf(buffer, shadowReportJSon, state.led_ring_count, state.led_ring_color.r, state.led_ring_color.g, state.led_ring_color.b,
            state.led_state ? "on": "off",
            state.dispense_time_ms,
            response_buffer,
            current_tick_count
            );
}

QueueHandle_t resetSema;

void prvUpdateShadow( struct State new_state );

static void changeState( struct State new_state )
{
    current_state = new_state;
    xQueueSend( motorStatesQueue, &current_state, 0 );
}

static json_object_entry * find_key( json_value * o,
                                     const char * key )
{
    for( int i = 0; i < o->u.object.length; ++i )
    {
        if( strcmp( o->u.object.values[ i ].name, key ) == 0 )
        {
            return &o->u.object.values[ i ];
        }
    }

    configPRINTF(( "key not found: %s\n", key ));
    return NULL;
}

void prvPopulateState(json_object_entry* state, struct State *new_state)
{
    json_object_entry * led_ring = find_key( state->value, "led_ring" );
    json_object_entry * led = find_key( state->value, "led" );
    json_object_entry * dispense_time_ms = find_key( state->value, "dispense_time_ms" );
    json_object_entry * request = find_key( state->value, "request" );

    if( led_ring )
    {
        json_object_entry * led_ring_count = find_key( led_ring->value, "count" );
        json_object_entry * led_ring_color = find_key( led_ring->value, "color" );
        if (led_ring_count){
            new_state->led_ring_count = led_ring_count->value->u.integer;
        }
        if (led_ring_color){
            sscanf(led_ring_color->value->u.string.ptr, "#%2x%2x%2x", &new_state->led_ring_color.r, &new_state->led_ring_color.g, &new_state->led_ring_color.b);
        }
    }

    if (led) {
        if (strncmp(led->value->u.string.ptr, "on", led->value->u.string.length) == 0){
            new_state->led_state = true;
        } else {
            new_state->led_state = false;
        }
    }

    if( dispense_time_ms )
    {
        new_state->dispense_time_ms = dispense_time_ms->value->u.integer;
    }

    if (request)
    {
        // We assume that if there is request, then the command is always "dispense"
        new_state->requested = true;
        json_object_entry * request_id = find_key( request->value, "requestId" );
        json_object_entry * timestamp = find_key( request->value, "timestamp" );
        if ( request_id ){
            strncpy(new_state->request_id, request_id->value->u.string.ptr, request_id->value->u.string.length);
        }
        if (timestamp){
            new_state->cloud_start_timestamp_ms = timestamp->value->u.integer;
        }
    } else {
        new_state->requested = false;
    }

}

static BaseType_t prvDeltaCallback( void * pvUserData,
                                    const char * const pcThingName,
                                    const char * const pcDeltaDocument,
                                    uint32_t ulDocumentLength,
                                    MQTTBufferHandle_t xBuffer )
{
    ( void ) xBuffer;
    ( void ) pvUserData;
    ( void ) pcThingName;
    configPRINTF(( "DELTA: %s\n", pcDeltaDocument ));
    struct State new_state = current_state; /* We need a correct initial value */
    json_value * val = json_parse( pcDeltaDocument, ulDocumentLength );
    json_object_entry * state = find_key( val, "state" );

    if( !state )
    {
        json_value_free( val );
        return pdTRUE;
    }

    prvPopulateState(state, &new_state);

    changeState( new_state );
    json_value_free( val );
    SHADOW_ReturnMQTTBuffer( xClientHandle, xBuffer );
    return pdTRUE;
}



static ShadowReturnCode_t prvGetState()
{
    ShadowOperationParams_t xOperationParams;
    ShadowReturnCode_t xReturn;
    struct State new_state = current_state; // The current state should already contain reasonable defaults

    memset( &xOperationParams, 0, sizeof( xOperationParams ) );
    xOperationParams.pcThingName = clientcredentialIOT_THING_NAME;
    xOperationParams.xQoS = 1;
    configPRINTF(( "Shadow Get \n" ));
    xReturn = SHADOW_Get( xClientHandle, &xOperationParams, MQTT_TIMEOUT * 3 );
    configPRINTF(( "Shadow Get return: %d\n", xReturn ));

    if( xReturn != eShadowSuccess )
    {
        return xReturn;
    }

    configPRINTF(( "%s %d\n", xOperationParams.pcData, xOperationParams.ulDataLength ));
    json_value * val = json_parse( xOperationParams.pcData, xOperationParams.ulDataLength );
    json_object_entry * state = find_key( val, "state" );

    if( !state )
    {
        json_value_free( val );
        return pdTRUE;
    }

    json_object_entry * reported = find_key( state->value, "reported" );

    if( !reported )
    {
        json_value_free( val );
        return pdTRUE;
    }
    prvPopulateState(reported, &new_state);

    /* Now populate missing fields with the desired data */
    json_object_entry * desired = find_key( state->value, "desired" );
    prvPopulateState(desired, &new_state);
    configPRINTF(("Initial state change\r\n"));
    changeState( new_state );
    json_value_free( val );
    SHADOW_ReturnMQTTBuffer( xClientHandle, xOperationParams.xBuffer );
    return xReturn;
}

ShadowReturnCode_t prvConnectToShadow( void )
{
    ShadowCreateParams_t xCreateParam;
    ShadowReturnCode_t xReturn;
    MQTTAgentConnectParams_t xConnectParams;

    xCreateParam.xMQTTClientType = eDedicatedMQTTClient;
    configPRINTF(( "SHADOW_ClientConnect ...\n" ));
    xReturn = SHADOW_ClientCreate( &xClientHandle, &xCreateParam );

    if( xReturn == eShadowSuccess )
    {
        memset( &xConnectParams, 0, sizeof( xConnectParams ) );
        xConnectParams.pcURL = clientcredentialMQTT_BROKER_ENDPOINT;
        xConnectParams.usPort = clientcredentialMQTT_BROKER_PORT;
        xConnectParams.xFlags =
            mqttagentREQUIRE_TLS;
        xConnectParams.pcCertificate = NULL;
        xConnectParams.ulCertificateSize = 0;
        xConnectParams.pvUserData = &xClientHandle;
        xConnectParams.pucClientId = ( const unsigned char * )
                                     clientcredentialIOT_THING_NAME;
        xConnectParams.usClientIdLength = strlen( clientcredentialIOT_THING_NAME );
        xReturn = SHADOW_ClientConnect( xClientHandle, &xConnectParams, MQTT_TIMEOUT * 3 );

        if( xReturn != eShadowSuccess )
        {
            configPRINTF(( "SHADOW_ClientConnect unsuccessful: %d\n", xReturn ));
        }
    }
    else
    {
        configPRINTF(( "SHADOW_ClientCreate unsuccessful: %d\n", xReturn ));
    }

    return xReturn;
}

void xShadowTask( void * param )
{
    ( void ) param;
    ShadowReturnCode_t xReturn;
    ShadowCallbackParams_t xCallbackParams;
    ShadowOperationParams_t xUpdateParam;
    resetSema = xSemaphoreCreateBinary();
    xReturn = prvConnectToShadow();
    TickType_t xLastWakeTime;

    if( xReturn == eShadowSuccess )
    {
        /* Set the callbacks sent by the IoT shadow */
        xCallbackParams.pcThingName = clientcredentialIOT_THING_NAME;
        xCallbackParams.xShadowDeletedCallback = NULL;
        xCallbackParams.xShadowDeltaCallback = prvDeltaCallback;
        xCallbackParams.xShadowUpdatedCallback = NULL;
        xReturn = SHADOW_RegisterCallbacks( xClientHandle, &xCallbackParams, MQTT_TIMEOUT * 3 );

        if( xReturn == eShadowSuccess )
        {
            /* Receive the current shadow state */
            xReturn = prvGetState();
            /*            if (xReturn != eShadowSuccess) return; */

            xLastWakeTime = xTaskGetTickCount();

            for( ; ; )
            {
//                if( xSemaphoreTake( motorStopSema, 0 ) == pdTRUE ) /* reset desired */
                xSemaphoreTake( motorTaskUpdateStateSema, portMAX_DELAY );/* reset desired */
                if (current_state.requested){
                    current_state.requested = false;
                    prvShadowResponseBuild(current_state, true);
                }
                else
                {
                    prvShadowResponseBuild(current_state, false);
                }

                xUpdateParam.pcThingName = clientcredentialIOT_THING_NAME;
                xUpdateParam.xQoS = eMQTTQoS0;
                xUpdateParam.pcData = buffer;
                xUpdateParam.ucKeepSubscriptions = pdTRUE;
                /* Generate data for sending to the shadow */
                xUpdateParam.ulDataLength = ( uint32_t ) strlen( buffer );

                xReturn = SHADOW_Update( xClientHandle, &xUpdateParam, MQTT_TIMEOUT * 2 );

                if( xReturn == eShadowSuccess )
                {
                    configPRINTF( ( "Successfully performed update.\r\n" ) );
                }
                else
                {
                    configPRINTF( ( "Update failed, returned %d.\r\n", xReturn ) );
                }

                configPRINTF(( "Free mem: %d\n", xPortGetFreeHeapSize() ));
                vTaskDelayUntil( &xLastWakeTime, pdMS_TO_TICKS(SHADOW_UPDATE_PERIOD_MS) );
            }
        }
    }
}
