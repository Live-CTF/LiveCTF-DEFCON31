#include <stdio.h>
#include <stdlib.h>
#include <time.h>

unsigned long long int function_0(unsigned long long int value) {
    value /= 13;
    return value;
}

unsigned long long int function_1(unsigned long long int value) {
    value += 7569522408655332926;
    return value;
}

unsigned long long int function_2(unsigned long long int value) {
    value /= 13;
    return value;
}

unsigned long long int function_3(unsigned long long int value) {
    value /= 101;
    return value;
}

unsigned long long int function_4(unsigned long long int value) {
    value *= 2527994158430899012;
    return value;
}

unsigned long long int function_5(unsigned long long int value) {
    value -= 189866154583718698;
    return value;
}

unsigned long long int function_6(unsigned long long int value) {
    value -= 7689855765606705449;
    return value;
}

unsigned long long int function_7(unsigned long long int value) {
    value -= 5930075953319435687;
    return value;
}

unsigned long long int function_8(unsigned long long int value) {
    value *= 3302618126280440659;
    return value;
}

unsigned long long int function_9(unsigned long long int value) {
    value *= 1275116684460247581;
    return value;
}

unsigned long long int function_10(unsigned long long int value) {
    value *= 1833511686154153449;
    return value;
}

unsigned long long int function_11(unsigned long long int value) {
    value *= 4241329626364948373;
    return value;
}

unsigned long long int function_12(unsigned long long int value) {
    value += 1956183603436484305;
    return value;
}

unsigned long long int function_13(unsigned long long int value) {
    value *= 5252608370602572355;
    return value;
}

unsigned long long int function_14(unsigned long long int value) {
    value /= 73;
    return value;
}

unsigned long long int function_15(unsigned long long int value) {
    value += 7537511426490674727;
    return value;
}

unsigned long long int function_16(unsigned long long int value) {
    value += 6677467636412849891;
    return value;
}

unsigned long long int function_17(unsigned long long int value) {
    value += 4882838825844109126;
    return value;
}

unsigned long long int function_18(unsigned long long int value) {
    value /= 59;
    return value;
}

unsigned long long int function_19(unsigned long long int value) {
    value -= 4376854289540620114;
    return value;
}

unsigned long long int function_20(unsigned long long int value) {
    value += 2714490925107135810;
    return value;
}

unsigned long long int function_21(unsigned long long int value) {
    value /= 61;
    return value;
}

unsigned long long int function_22(unsigned long long int value) {
    value *= 7706468032073994496;
    return value;
}

unsigned long long int function_23(unsigned long long int value) {
    value *= 1944864038549343827;
    return value;
}

unsigned long long int function_24(unsigned long long int value) {
    value += 9149399232606838820;
    return value;
}

unsigned long long int function_25(unsigned long long int value) {
    value *= 7176976270523575767;
    return value;
}

unsigned long long int function_26(unsigned long long int value) {
    value += 7028937678081350508;
    return value;
}

unsigned long long int function_27(unsigned long long int value) {
    value += 4564166705989247848;
    return value;
}

unsigned long long int function_28(unsigned long long int value) {
    value += 165156912168189001;
    return value;
}

unsigned long long int function_29(unsigned long long int value) {
    value -= 6858884378534482958;
    return value;
}

unsigned long long int function_30(unsigned long long int value) {
    value *= 3578149508214746498;
    return value;
}

unsigned long long int function_31(unsigned long long int value) {
    value /= 137;
    return value;
}

unsigned long long int function_32(unsigned long long int value) {
    value -= 688536493232538734;
    return value;
}

unsigned long long int function_33(unsigned long long int value) {
    value -= 5365814489109451082;
    return value;
}

unsigned long long int function_34(unsigned long long int value) {
    value /= 101;
    return value;
}

unsigned long long int function_35(unsigned long long int value) {
    value -= 7941002930763697033;
    return value;
}

unsigned long long int function_36(unsigned long long int value) {
    value /= 89;
    return value;
}

unsigned long long int function_37(unsigned long long int value) {
    value *= 1094286351883042652;
    return value;
}

unsigned long long int function_38(unsigned long long int value) {
    value *= 5228697329485816791;
    return value;
}

unsigned long long int function_39(unsigned long long int value) {
    value /= 5;
    return value;
}

void init(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

int main() {
    init();
    srand(0);
    int order[40];
    for (int i = 0; i < 40; i++) order[i] = i;
    for (int i = 39; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = order[i];
        order[i] = order[j];
        order[j] = temp;
    }

    printf("Enter the initial value: ");
    unsigned long long int value;
    scanf("%llu", &value);
    for (int i = 0; i < 40; i++) {
        switch(order[i]) {
            case 0:
                value = function_0(value);
                break;
            case 1:
                value = function_1(value);
                break;
            case 2:
                value = function_2(value);
                break;
            case 3:
                value = function_3(value);
                break;
            case 4:
                value = function_4(value);
                break;
            case 5:
                value = function_5(value);
                break;
            case 6:
                value = function_6(value);
                break;
            case 7:
                value = function_7(value);
                break;
            case 8:
                value = function_8(value);
                break;
            case 9:
                value = function_9(value);
                break;
            case 10:
                value = function_10(value);
                break;
            case 11:
                value = function_11(value);
                break;
            case 12:
                value = function_12(value);
                break;
            case 13:
                value = function_13(value);
                break;
            case 14:
                value = function_14(value);
                break;
            case 15:
                value = function_15(value);
                break;
            case 16:
                value = function_16(value);
                break;
            case 17:
                value = function_17(value);
                break;
            case 18:
                value = function_18(value);
                break;
            case 19:
                value = function_19(value);
                break;
            case 20:
                value = function_20(value);
                break;
            case 21:
                value = function_21(value);
                break;
            case 22:
                value = function_22(value);
                break;
            case 23:
                value = function_23(value);
                break;
            case 24:
                value = function_24(value);
                break;
            case 25:
                value = function_25(value);
                break;
            case 26:
                value = function_26(value);
                break;
            case 27:
                value = function_27(value);
                break;
            case 28:
                value = function_28(value);
                break;
            case 29:
                value = function_29(value);
                break;
            case 30:
                value = function_30(value);
                break;
            case 31:
                value = function_31(value);
                break;
            case 32:
                value = function_32(value);
                break;
            case 33:
                value = function_33(value);
                break;
            case 34:
                value = function_34(value);
                break;
            case 35:
                value = function_35(value);
                break;
            case 36:
                value = function_36(value);
                break;
            case 37:
                value = function_37(value);
                break;
            case 38:
                value = function_38(value);
                break;
            case 39:
                value = function_39(value);
                break;
        }
    }
    if (value == 0x6fd86066670e9100) { // Fixup after generation
        printf("Congratulations! Your initial value has produced the correct final value!\n");
        system("/bin/sh");
    } else {
        printf("Try again. Final value is not correct.\n");
    }
    return 0;
}
