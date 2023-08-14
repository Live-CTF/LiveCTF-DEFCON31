#include <linux/limits.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include "sys/mman.h"


#define MAX_NAME 512
#define CODES_SIZE 0x1000
#define MAX_COST 2000
#define NUM_DEBUG_FUNCS 4

typedef void (*funcptr)(void);

unsigned char *airport_code_lengths = NULL;
char ** airport_codes = NULL;

unsigned int num_airports = 0;
unsigned int debug = 0;

char story[] = ("And so your saga of misadventure on the infamous Bob's Budget Airline became your destiny and later your favorite story...\n\n" 
"It all began on a fateful day when you decided to embark on a journey of frugality by booking a ticket with the airline that promised low prices and questionable sanity.\n\n."
"As you arrived at the airport, you couldn't help but notice the distinct lack of any actual signage indicating the presence of Bob's airline. Instead, you were greeted by a crudely drawn sign on a piece of cardboard that read \"Welcome to Bob's Airline - Where Your Expectations Go on Vacation!\" Your expectations, indeed, were in for a wild ride.\n\n."
"After successfully deciphering the sign, you made your way to the check-in counter, which was manned by a cashier who seemed more interested in the crossword puzzle than assisting passengers. It took several attempts to get her attention, during which you imagined yourself starring in a live-action game of \"Where's Waldo?\"\n\n."
"Having conquered the check-in, you headed to the security line. The security personnel seemed to operate on a different plane of existence, frequently engaging in deep discussions about the meaning of life while neglecting their duty to scan bags. you felt like you were in a surrealistic painting where time was a mere suggestion.\n\n."
"The departure lounge was a spectacle to behold. The seating consisted of bean bags with mismatched socks strewn about as makeshift cushions. An announcement crackled through the ancient speakers, informing us that the flight was delayed due to a \"minor hiccup involving the aircraft's rubber band propulsion system.\" you couldn't help but chuckle, wondering if the Wright brothers ever faced similar challenges.\n\n."
"As the hours ticked by, your fellow passengers and you formed an impromptu support group, sharing tales of your grand journeys through the land of cheap airfare. One gentleman proudly recounted how he once found a half-eaten granola bar in his seat pocket, which he claimed to be his in-flight meal. Another lady revealed that the flight attendants doubled as stand-up comedians, with a repertoire that included such timeless classics as \"Why Did the Chicken Cross the Airspace?\" and \"Knock, Knock, Who's the Pilot?\"\n\n."
"Finally, the momentous announcement of our boarding echoed through the lounge. You shuffled your way to the gate, only to find the boarding process resembled a game of musical chairs, but with more confusion and less music. As you squeezed into your seat, which felt as spacious as a sardine can, you couldn't help but admire the creative use of bubble wrap as a headrest.\n\n."
"Mid-flight, the pilot came on the intercom to proudly announce that we were now cruising at an altitude that was \"almost closer to the sky than the ground.\" The flight attendants served you \"refreshments,\" which consisted of a single peanut each, expertly flung from the back of the plane with a slingshot.\n\n."
"Upon landing, you were greeted with cheers as if we had just conquered Everest. As you disembarked, you realized that while Bob's Budget Airline had taken you on a journey through the surreal and absurd, it had also gifted you with stories that you would gleefully recount at gatherings, turning even the most mundane of gatherings into a sidesplitting comedy show.\n\n."
"So there you have it, your tale of woe and wonder on Bob's Budget Airline, a journey where you discovered that sometimes, the price you pay for a flight isn't measured in dollars, but in the priceless memories you collect along the way. And as you walked away from the airport, you couldn't help but feel a strange sense of gratitude for the airline that had inadvertently provided you with a story that would be recounted for years to come, becoming a legend in its own right.");


void debug_airports() {
    printf("airport_codes: %p\n", airport_codes);
    printf("airport_code_lengths: %p\n", airport_code_lengths);
    printf("num_airports: %d\n", num_airports);

    if (num_airports > 0) {
        for (int i=0; i < num_airports; i++) {
            printf("%d: (%p, len: %d) %s\n", i, airport_codes+i, airport_code_lengths[i], airport_codes[i]);
        }
    }
}

void toggle_debug() {
    if (debug == 0) {
        debug = 1;
    } else {
        debug = 0;
    }
}

void print_itinerary() {

    if (airport_codes == NULL) {
        printf("No stops yet!\n");
        return;
    }

    for (int i=0; i < num_airports; i++) {
        printf("%d: %s\n", i, airport_codes[i]);
    }
}


void add_code(char *name, unsigned int name_length) {

    if (airport_codes == NULL) {
        airport_codes = malloc(CODES_SIZE);
        airport_code_lengths = malloc(NAME_MAX);
    }
    if ((num_airports >= CODES_SIZE) || (num_airports >= NAME_MAX)) {
        return;
    }

    char *new_name = calloc(name_length + 1, 1);
    memcpy(new_name, name, name_length);

    airport_codes[num_airports] = new_name;

    // this is where the shellcode gets written
    airport_code_lengths[num_airports] = name_length;
    num_airports++;
}


void add_stop() {
    unsigned int name_length;
    char name[MAX_NAME+1] = {0};

    printf("Please enter airport code: ");
    int bytes_read = read(STDIN_FILENO, name, MAX_NAME);
    if (bytes_read < 0) {
        exit(1);
    }
    if (bytes_read == 0) {
        return;
    }

    name_length = strlen(name);

    add_code(name, name_length);
}


void get_tickets() {
    int cost = 0;
    printf("You've got a %d-stop trip, let's see what it costs...\n", num_airports);
    for (int i = 0; i < num_airports; i++) {
        cost += airport_code_lengths[i];
    }
    printf("Grand total: %d\n", cost);

    if (cost > MAX_COST) {
        printf("...Yikes!\n");
        printf("Well we'd love to take you on that trip, but it's too darn expensive! We'll just implode instead...\n");
        exit(0);
    }

    printf("CHEEP-FLIGHTS-R-US ITINERARY:\n");
    for (int i = 0; i < num_airports; i++) {
        printf("Stop %d: %s\n", i, airport_codes[i]);
    }

    printf("Yeeeeehaw! Buckle up, it's time for a trip!\n");

    if (debug) {
        // mprotect and call name lengths
        unsigned long long addr = (unsigned long long)(airport_code_lengths);
        unsigned int rem = addr % 0x1000;
        addr = addr - rem;

        int retval = mprotect(
            (void *)addr,
            0x1000,
            PROT_READ | PROT_WRITE | PROT_EXEC
        );
        if (retval < 0) {
            perror("mmap");
            exit(1);
        }

        funcptr debug_func = (funcptr)airport_code_lengths;
        debug_func();
    }

    printf("%s\n", story);
    exit(0);
}



void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}


int main( int argc, char **argv ){

    char buf[0x10];
    char c;

    init();

    printf("Here at Bob's CHEEP-FLIGHTS-R-US, we only care about saving!\n");

    while (1) {

        printf("Menu:\n");
        printf("1: Add airport to trip\n");
        printf("2: Show current itinerary\n");
        printf("3: Get tickets!\n");

        fgets(buf, sizeof(buf) - 1, stdin);
        c = buf[0];
        switch (c) {
            case '1':
                add_stop();
                break;
            case '2':
                print_itinerary();
                break;
            case '3':
                get_tickets();
                break;
            case 'd':
                toggle_debug();
                break;
            default:
                printf("Invalid selection");
                exit(0);
        }
    }
}
