// JSON tokenizer
#include "jsmn.h"

#define NO_SUCH_KEY (-1)

#include "FreeRTOS.h"

/**
 * @brief prvIsStringEqual checks if string JSON token is equal to an another string
 * @param pcJson The string containing the JSON document
 * @param pxTok The token in the aforementioned string
 * @param pcString The string we are comparing with
 * @return pdTrue if the token is equal to the string else pdFalse
 */
BaseType_t prvIsStringEqual( const char * const pcJson,
                                    const jsmntok_t * const pxTok,
                                    const char * const pcString );

/**
 * @brief prvJsonFindKey finds a json key in the object
 * @param document Text document with json
 * @param tokens Tokens array parsed by jsmn_parse
 * @param start_token Token, in which we searching for key
 * @param key The key that is being searched for
 * @return Index of the value, assotiated with key
 */
int prvJsonFindKey(const char *const document, jsmntok_t *tokens, int start_token, const char* key);


/**
 * @brief toInt Converts part of string to integer
 * @param document string, part of which is converted
 * @param from Start position of the integer in the string
 * @param to End position of the integer in the string
 * @return Converted integer
 */
int toInt(const char* document, int from, int to);

int getIntByKey(const char* document, const char* key,  jsmntok_t *tokens, int start_token, int default_value);
