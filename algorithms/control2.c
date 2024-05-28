#include <stdio.h>
#include <stdlib.h>

int main() {
    FILE *file = fopen("numbers.bin", "rb");
    if (file == NULL) {
        printf("Error opening file!");
        return 1;
    }

    // Calculate the size of the file
    fseek(file, 0, SEEK_END);
    long fileSize = ftell(file);
    rewind(file);

    // Allocate memory to hold the file data
    int *numbers = (int *)malloc(fileSize);
    if (numbers == NULL) {
        printf("Memory allocation failed!");
        return 1;
    }

    // Read the file data into the memory buffer
    fread(numbers, fileSize, 1, file);
    fclose(file);

    // Calculate the number of integers in the file
    int numIntegers = fileSize / sizeof(int);

    // Print the numbers
    printf("Numbers read from file:\n");
    for (int i = 0; i < numIntegers; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\n");

    // Free dynamically allocated memory
    free(numbers);

    return 0;
}
