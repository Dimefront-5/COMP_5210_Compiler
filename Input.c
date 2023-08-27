/*make a hello world program

int void main {
    printf("Hello World");
    return 0;
}*/

#include <stdio.h>

int main() {
    // Declare variables
    int num1 = 42;
    double num2 = 3.14;
    char ch = 'A';
    void *ptr = NULL;
    
    // Conditional statement
    if(num1 > 0xBEEF&&num2<4){
        printf("Both conditions are true\n");
    } else {
        printf("At least one condition is false\n");
    }
    
    // Loop
    for (int i = 0; i < 5; i++) {
        printf("Iteration %d\n", i);
    }
    
    // Return statement
    return 0;
}





