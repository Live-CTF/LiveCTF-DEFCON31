#include <stdlib.h>

int KSA(unsigned char *S, unsigned char *key, size_t keylen);
int PRGA(unsigned char *S, unsigned char *src, unsigned char *dst, size_t len);
int RC4(unsigned char *key, size_t keylen, unsigned char *src, unsigned char *dst, size_t len);
