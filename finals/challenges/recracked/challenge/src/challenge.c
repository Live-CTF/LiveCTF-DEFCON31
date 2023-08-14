/*
        Copyright (c) 2011, Thomas Dullien
        All rights reserved.

        Redistribution and use in source and binary forms, with or without 
        modification, are permitted provided that the following conditions
        are met:

        Redistributions of source code must retain the above copyright notice,
        this list of conditions and the following disclaimer. Redistributions 
        in binary form must reproduce the above copyright notice, this list of
        conditions in the documentation and/or other materials provided with 
        the distribution.
*/

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

const char *copyright = "Copyright (c) 2011, Thomas Dullien\nAll rights reserved.";

#define INPUTSIZE 400
#define BUFFERSIZE 200
#define TRUE 1
#define FALSE 0

void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

char *upperlimit;
char *p;
char *d;
char *bufstart;
int quotation = FALSE;
int roundquote = FALSE;

int copy_it( char * input )
{
    char localbuf[ BUFFERSIZE ];
    volatile char c;
    void *v = &system;

    p = input;
    d = &localbuf[0];
    bufstart = d;
    upperlimit = &localbuf[ BUFFERSIZE-10 ];

    memset( localbuf, 0, BUFFERSIZE );

    while( (c = *p++) != '\0' ){
        if(( c == '<' ) && (!quotation)){
            quotation = TRUE;
            upperlimit--;}
        if(( c == '>' ) && (quotation)){
            quotation = FALSE;
            upperlimit++;}
        if(( c == '(' ) && ( !quotation ) && !roundquote){
            roundquote = TRUE;
            /*upperlimit--;*/}
        if(( c == ')' ) && ( !quotation ) && roundquote){
            roundquote = FALSE;
            upperlimit++;}
        // If there is sufficient space in the buffer, write the character.
        if( d < upperlimit )
            *d++ = c;
    }
    if( roundquote )
            *d++ = ')';
    if( quotation )
            *d++ = '>';

    //printf("addr: \"%s\"\n", bufstart);
    printf("%s\n\n", bufstart);

    return 0;
}

int main( int argc, char **argv ){
    char inputbuf[INPUTSIZE] = {0};

    init();

    printf("Welcome to the mail server...\n");

    while (TRUE) {
        //fread(inputbuf, 1, sizeof(inputbuf)-1, stdin);
        read(0, inputbuf, sizeof(inputbuf)-1);
        copy_it( inputbuf );
    }
}