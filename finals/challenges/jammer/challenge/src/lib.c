#include "stdlib.h"
#include "unistd.h"
#include "errno.h"


int random_in_range(int min, int max) {
    int offset = rand() % (max - min + 1);
    return min + offset;
};

char *generateRandomString(int length) 
{
  if (length <= 0) 
  {
    return NULL;
  }
  char *string = calloc(length + 1, 1);
  for (int i=0; i < length; i++) 
  {
    string[i] = random_in_range(0x41, 0x7a);
  }
  return string;
}

unsigned int generateRandomNumber(int min, int max) 
{
  return random_in_range(min, max);
}

int receive(int fd, void *buf, size_t count, size_t *rx_bytes) {
    const ssize_t ret = read(fd, buf, count);

    if (ret < 0) {
        return errno;
    } else if (rx_bytes != NULL) {
        *rx_bytes = ret;
    }

    return 0;
}

char receiveBuffer[1024];
char *pData = receiveBuffer;
int bytesInBuffer = 0;
int receiveUntil(char *buf, int length, char delim)
{
	char c;
	int bytesCopied = 0;
	*buf = 0;
	while (1)
	{
		if (bytesInBuffer > 0)
		{	
			c = *pData++;
			bytesInBuffer--;
			if (bytesInBuffer == 0)
			{
				pData = receiveBuffer;
			}
		} else {
			int ret;
            size_t bytesReceived = 0;
			ret = receive(STDIN_FILENO, receiveBuffer , 1024 , &bytesReceived);
	    if (ret != 0) {
	      return -1;
	    }
	   	if (bytesReceived == 0)
	   	{
	   		break;
	   	}
	   	bytesInBuffer = bytesReceived - 1;
	   	pData = receiveBuffer;
	   	c = *pData++;
	  }
	  if (c == delim)
	  {
	  	break;
	  }
	  if (bytesCopied < length - 1)
	  {
		  *buf++ = c;
		  bytesCopied++;
		}
	}
	*buf = '\0';
	return bytesCopied;
}

int transmit(int fd, const void *buf, size_t count, size_t *tx_bytes) {
    const ssize_t ret = write(fd, buf, count);

    if (ret < 0) {
        return errno;
    } else if (tx_bytes != NULL) {
        *tx_bytes = ret;
    }

    return 0;
}

int sendBytes(char *buffer, int length) 
{
  int totalSent = 0;
  int returnValue;
  size_t bytesSent;
  while(totalSent < length) 
  {
    returnValue = transmit(STDOUT_FILENO, buffer + totalSent, length - totalSent, &bytesSent);
    if (returnValue != 0)
    {
      // error
      return -1;
    }
    if (bytesSent == 0) 
    {
      break;
    }
    totalSent += bytesSent;
  }
  return totalSent;
}