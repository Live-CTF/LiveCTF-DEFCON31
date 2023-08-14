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

#include "linkedlist.h"
#include "service.h"
#include "lib.h"

linkedList *serverList;
int adminPortOffset;

void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

int getNextAdminPort()
{
  adminPortOffset = (adminPortOffset + 4) % 4096;
  return adminPortOffset;
}

serverInfo *createServer(int length)
{
  serverInfo *pServer = zalloc(sizeof(serverInfo));
  pServer->name = generateRandomString(length);
  pServer->instances = newList(LIST_INSTANCE);
  return pServer;
}

instanceInfo *createInstance(int length)
{
  instanceInfo *pInstance = zalloc(sizeof(instanceInfo));
  pInstance->name = generateRandomString(length);
  pInstance->port = generateRandomNumber(0, 65535);
  pInstance->adminPortOffset = getNextAdminPort();
  return pInstance;
}

void addInstanceToServer(serverInfo *pServer, instanceInfo *pInstance)
{
  addToList(pServer->instances, pInstance, LIST_INSTANCE);
  pInstance->server = pServer;
}

serverInfo *findServer(char *name)
{
  link *listItem = serverList->root;
  while (listItem != NULL)
  {
    serverInfo *server = listItem->object;
    if (server == NULL)
    {
      continue;
    }
    if (strcmp(server->name, name) == 0)
    {
      return server;
    }
    listItem = listItem->next;
  }
  return NULL;
}

instanceInfo *findInstance(char *name)
{
  link *listItem = serverList->root;
  while (listItem != NULL)
  {
    serverInfo *server = listItem->object;
    if (server == NULL)
    {
      continue;
    }
    link *listItem2 = server->instances->root;
    while (listItem2 != NULL)
    {
      instanceInfo *instance = listItem2->object;
      if (instance == NULL)
      {
        continue;
      }
      if (strcmp(instance->name, name) == 0)
      {
        return instance;
      }
      listItem2 = listItem2->next;
    }
    listItem = listItem->next;
  }
  return NULL;
}

void initializeSimulation()
{
  adminPortOffset = 0;
  serverList = newList(LIST_SERVER);
  // Create Servers
  int numServers = generateRandomNumber(10,32);
  int nameLength = generateRandomNumber(34, 64);
  for (int i=0; i<numServers; i++)
  {
    serverInfo *server = createServer(nameLength - i);
    addToList(serverList, server, LIST_SERVER);
    // Create and link instances to servers
    int numInstances = generateRandomNumber(1, 15);
    int instanceLength = generateRandomNumber(32, 64);
    for(int j=0; j<numInstances; j++)
    {
      instanceInfo *instance = createInstance(instanceLength - j);
      addInstanceToServer(server, instance);
    }
  }
}

void queryOne(query *pCurrentQuery, response *pCurrentResponse)
{
  char name[64];
  for (int i=0; i< 64; i++) {
    name[i] = i;
  }
  printf("Query One\n");

  // VULN
  strcpy(name, (char *)pCurrentQuery->data);

  instanceInfo *instance = findInstance(name);
  if (instance == NULL)
  {
    printf("Not found\n");
    return;
  }
  addToResponse(pCurrentResponse, "instance:");
  addToResponse(pCurrentResponse, instance->name);
  addToResponse(pCurrentResponse, ":");
  addToResponse(pCurrentResponse, "tcp:");
  char number[12];
  sprintf(number, "%d", instance->port);
  addToResponse(pCurrentResponse, number);
  addToResponse(pCurrentResponse, ":");
  addToResponse(pCurrentResponse, "server:");
  addToResponse(pCurrentResponse, instance->server->name);
  addToResponse(pCurrentResponse, ":");
  return;
}

int main(int argc, char *argv[])
{
  char inputBuffer[1024];

  init();
  srand(0);
  initializeSimulation();

  puts("Welcome to the Server Resolution Service, commencing binary protocol");

  while (1)
  {

    int bytesReceived = receiveUntil(inputBuffer, sizeof(inputBuffer), '\n');
    if (bytesReceived < 0)
    {
      break;
    }
    if (bytesReceived == 0)
    {
      continue;
    }
    query *pCurrentQuery = parseQuery(inputBuffer);
    response *pCurrentResponse = generateBlankResponse();
    switch (pCurrentQuery->type)
    {
      case QUERY_ALL:
      {
        printf("Query All\n");
        // List all servers in network
        link *listItem = serverList->root;
        while (listItem != NULL)
        {
          serverInfo *server = listItem->object;
          if (server == NULL)
          {
            continue;
          }
          addToResponse(pCurrentResponse, "server:");
          addToResponse(pCurrentResponse, server->name);
          addToResponse(pCurrentResponse, ":");
          listItem = listItem->next;
        }
        break;
      }
      case QUERY_SERVER:
      {
        printf("Query Server\n");
        // List all instances on a server
        char *name = (char *)pCurrentQuery->data;
        serverInfo *server = findServer(name);
        if (server == NULL)
        {
          continue;
        }
        link *listItem = server->instances->root;
        while (listItem != NULL)
        {
          instanceInfo *instance = listItem->object;
          if (instance == NULL)
          {
            continue;
          }
          addToResponse(pCurrentResponse, "instance:");
          addToResponse(pCurrentResponse, instance->name);
          addToResponse(pCurrentResponse, ":");
          listItem = listItem->next;
        }
        break;
      }
      case QUERY_ONE:
      {
        queryOne(pCurrentQuery, pCurrentResponse);
        break;
      }
      // LiveCTF: commenting to reduce scope for competitors
      /*
      case QUERY_ADMIN:
      {
        // Send admin info for one instance
        printf("Query Admin\n");
        int version = pCurrentQuery->data[0];
        if (version != 1)
        {
          printf("Invalid Query\n");
          exit(0);
        }
        char instanceName[64];
        strncpy(instanceName, (char *)&pCurrentQuery->data[1], 64);
        instanceInfo *instance = findInstance(instanceName);
        if (instance == NULL)
        {
          printf("Instance Not Found\n");
          exit(0);
        }
        addToResponse(pCurrentResponse, "admin:");
        char number[12];
        memset(number, 0, sizeof(number));
        uint16_t adminPort = *(uint16_t *)((uint8_t *)free + instance->adminPortOffset);
        sprintf(number, "%x", (int)adminPort);
        addToResponse(pCurrentResponse, number);
        addToResponse(pCurrentResponse, ":");
        break;
      }
      */
      default:
      {
        // Invalid Query
        printf("Invalid Query\n");
        exit(0);
        break;
      }
    }
    sendResponse(pCurrentResponse);
    pCurrentQuery = destroyQuery(pCurrentQuery);
    pCurrentResponse = destroyResponse(pCurrentResponse);
  }
  return 0;
}
