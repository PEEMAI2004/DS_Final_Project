#include <stdio.h>
#include <stdlib.h>

void swap(int *xp, int *yp) {
    int temp = *xp;
    *xp = *yp;
    *yp = temp;
}

void selectionSort(int arr[], int n) {
    int i, j, min_idx;
    // One by one move boundary of unsorted subarray
    for (i = 0; i < n-1; i++) {
        // Find the minimum element in unsorted array
        min_idx = i;
        for (j = i+1; j < n; j++) {
            if (arr[j] < arr[min_idx])
                min_idx = j;
        }
        // Swap the found minimum element with the first element
        swap(&arr[min_idx], &arr[i]);
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

    // Sort the numbers using selection sort
    selectionSort(numbers, numIntegers);

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
