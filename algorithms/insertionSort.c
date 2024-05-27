#include <stdio.h>
#include <stdlib.h>

void insertionSort(int arr[], int n) {
    int i, key, j;
    for (i = 1; i < n; i++) {
        key = arr[i];
        j = i - 1;

        // Move elements of arr[0..i-1], that are greater than key, to one position ahead of their current position
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j = j - 1;
        }
        arr[j + 1] = key;
    }
}

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

    // Sort the numbers using insertion sort
    insertionSort(numbers, numIntegers);

    // Print the numbers
    printf("Sorted numbers read from file:\n");
    for (int i = 0; i < numIntegers; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\n");

    // Free dynamically allocated memory
    free(numbers);

    return 0;
}
