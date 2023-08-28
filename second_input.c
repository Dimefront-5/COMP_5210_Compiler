#include <stdio.h>

#define WEIRD_MACRO(x, y) x##y

int main() {
    // Single quote within double quotes
    printf("This is a single quote: '%c'\n", '\'');

    // Escaped double quotes within a string
    printf("This is a double quote: \"%c\"\n", '\"');

    // Weird macro usage
    int abcd = WEIRD_MACRO(12, 34);
    printf("Value of abcd: %d\n", abcd);

    // Multiline string using line continuation
    printf("This is a multiline \
string using line continuation.\n");

    // Trigraph sequence
    printf("This ??!??!??!\n");

    // Unicode escape sequence
    printf("\u03A9 is the Unicode code point for capital omega.\n");

    return 0;
}