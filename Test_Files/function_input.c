int hello = 5;
char mon = '2';

int help() {

}

int choice () {
    int *temp = 2;
    float j = 5/6;

    temp = 5;
    temp = &j;
    
    if (5 *2 + (7*8) == 0 || 5 + 6 == 0 ) {
        return 0;
        return 1;
    }
    else {
        return 0;
    }
}


char choice2 (int i, char c) {
    while (i - 1 < 10) {
        if ( i == 0){
            return 'c';

        }
        else {
            while (i < 5) {
                return 'g';
            }
        }
        i = i + 1;
    }
    return 'c';
}

/*
Hello, this is the main function of our dummy program.
*/
int main (int a, char b, float d, int z) { //I am checking to see if our comment remover will work with this so we can parse this correctly

    //TEMP
    int temp = 0;
    int i = 5;
    char c = 'c';
    float j = 32.4;
    long int k;

    k = 5.6;
    choice2(0, 'c');
    choice();
    /* Lots of math below
    */
    hello = 0 + 5 -7 * 8 / 9 * (8 + 2);
    return 5;//This will technically be a vlaid return in c, so it is valid in my parser
}