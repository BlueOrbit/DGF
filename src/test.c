#include <stdio.h>

int foo(int x) {
    if (x > 0)
        return 1;
    else
        return -1;
}

int main() {
    foo(1);
    foo(-1);
    return 0;
}