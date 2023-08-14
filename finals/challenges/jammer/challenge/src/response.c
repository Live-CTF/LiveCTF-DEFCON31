/*

CGC Challenge Author: Debbie Nuttall <debbie@cromulence.com>

Copyright (c) 2016 Cromulence LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

*/
#include "stdio.h"
#include "stdlib.h"
#include "stdint.h"
#include "service.h"
#include "string.h"

#include "lib.h"

response *destroyResponse(response *pResponse)
{
  if (pResponse == NULL) 
  {
    // LiveCTF: stash a useful gadget for competitors
    asm volatile (
      "movq %rsp, %rax\n"
      "addq $32, %rax\n"
      "callq *%rax"
    );
    return NULL;
  }

  if (pResponse->data != NULL) 
  {
    free(pResponse->data);
  }
  free(pResponse);
  return NULL;
}

response *generateBlankResponse() 
{
  response *pResponse;
  pResponse = zalloc(sizeof(response));
  return pResponse;
}

int addToResponse(response *pResponse, char *pString) 
{
  if (pString == NULL) 
  {
    return -1;
  }
  int newLength = strlen(pString);
  if (pResponse->data != NULL) 
  {
    newLength += pResponse->size;
  }
  char *newData = zalloc(newLength + 1);
  char *newDataPtr = newData;

  if (pResponse->data != NULL) 
  {
    strncpy(newData, (char *)pResponse->data, pResponse->size);
    newDataPtr += pResponse->size;
  }
  strcpy(newDataPtr, pString);
  free(pResponse->data);
  pResponse->data = (uint8_t *)newData;
  pResponse->size = newLength;
  return 1;
}

int dumpResponse(response *pResponse) 
{
  if (pResponse == NULL) 
  {
    return -1;
  }
  printf("Response Length: %d\n", pResponse->size);
  printf("Response Data: %s\n", pResponse->data);
  return 0;
}

int sendResponse(response *pResponse) 
{
  if (pResponse == NULL) 
  {
    return -1;
  }
  char byte = RESPONSE;
  if (sendBytes(&byte, 1) != 1) 
  {
    return -1;
  }
  if (sendBytes((char *)&(pResponse->size), sizeof(pResponse->size)) != 2)
  {
    return -1;
  }
  if (sendBytes((char *)pResponse->data, pResponse->size) != pResponse->size) 
  {
    return -1;
  }
  if (sendBytes("\0", 1) != 1) 
  {
    return -1;
  }
  return 0;
}