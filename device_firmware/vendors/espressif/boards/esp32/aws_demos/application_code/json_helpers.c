#include "json_helpers.h"
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

/**
 * @brief prvIsStringEqual checks if string JSON token is equal to an another string
 * @param pcJson The string containing the JSON document
 * @param pxTok The token in the aforementioned string
 * @param pcString The string we are comparing with
 * @return pdTrue if the token is equal to the string else pdFalse
 */
BaseType_t prvIsStringEqual( const char * const pcJson,
                                    const jsmntok_t * const pxTok,
                                    const char * const pcString )
{
    // If it is not a string, then why are we here?
    if (pxTok->type != JSMN_STRING) return pdFALSE;
    // Ok, it's a string, but how long is it?
    uint32_t ulSize = (uint32_t)(pxTok->end - pxTok->start);
    // The string we compare with shuld be null-terminated
    // and this null must be in the correct position
    if (pcString[ulSize] == 0 &&
            strncmp(pcJson + pxTok->start, pcString, ulSize) == 0){
        return pdTRUE;
    }
    return pdFALSE;
}


/**
 * @brief prvJsonFindKey finds a json key in the object
 * @param document Text document with json
 * @param tokens Tokens array parsed by jsmn_parse
 * @param start_token Token, in which we searching for key
 * @param key The key that is being searched for
 * @return Index of the value, assotiated with key
 */
int prvJsonFindKey(const char *const document, jsmntok_t *tokens, int start_token, const char* key){
    jsmntok_t token_value = tokens[start_token];
    int processing_token = start_token + 1;
    if (token_value.type != JSMN_OBJECT) {
//        printf ("Token %s found not found -1\n", key);
        return NO_SUCH_KEY;
    }
    for (int i = 0; i < token_value.size; ++i){
        if (prvIsStringEqual(document, &tokens[processing_token], key)){
//            printf ("Token %s found: %d\n", key, processing_token + 1);
            return processing_token + 1;
        }
        else {
            int skip_size = tokens[processing_token + 1].end; //Skip the associated value
            while (skip_size > tokens[processing_token].start) processing_token++;
        }
    }
//    printf ("Token %s found not found\n", key);
    return NO_SUCH_KEY;
}

/**
 * @brief toInt Converts part of string to integer
 * @param document string, part of which is converted
 * @param from Start position of the integer in the string
 * @param to End position of the integer in the string
 * @return Converted integer
 */
int toInt(const char* document, int from, int to){
    char tempBuf[40];
    strncpy(tempBuf, &document[from],
            (size_t)(to - from));
    tempBuf[to - from] = 0;
    printf("ATOI BUFFER: %s\n", tempBuf);
    return atoi(tempBuf);

}

int getIntByKey(const char* document, const char* key,  jsmntok_t *tokens, int start_token, int default_value){
    int token =  prvJsonFindKey(document, tokens, start_token, key);
    if (token != NO_SUCH_KEY)
        return toInt(document, tokens[token].start,
                                        tokens[token].end);
    return default_value;
}

