#include "rc4.h"
#define N 256   // 2^8

void swap(unsigned char *a, unsigned char *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

int KSA(unsigned char *S, unsigned char *key, size_t keylen) {
    int j = 0;
    for(int i = 0; i < N; i++) {
        S[i] = i;
    }

    for(int i = 0; i < N; i++) {
        j = (j + S[i] + key[i % keylen]) % N;
        swap(&S[i], &S[j]);
    }

    return 0;
}

int PRGA(unsigned char *S, unsigned char *src, unsigned char *dst, size_t len) {

    int i = 0;
    int j = 0;

    for(size_t n = 0; n < len; n++) {
        i = (i + 1) % N;
        j = (j + S[i]) % N;

        swap(&S[i], &S[j]);
        int rnd = S[(S[i] + S[j]) % N];

        dst[n] = rnd ^ src[n];

    }

    return 0;
}

int RC4(unsigned char *key, size_t keylen, unsigned char *src, unsigned char *dst, size_t len) {
    unsigned char S[N];
    KSA(S, key, keylen);
    PRGA(S, src, dst, len);

    return 0;
}
