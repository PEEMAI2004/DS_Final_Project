#include <stdio.h>
#include <stdlib.h>

void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int partition(int arr[], int low, int high) {
    int pivot = arr[high]; // pivot
    int i = (low - 1); // Index of smaller element

    for (int j = low; j <= high - 1; j++) {
        // If current element is smaller than the pivot
        if (arr[j] < pivot) {
            i++; // increment index of smaller element
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i + 1], &arr[high]);
    return (i + 1);
}

void quickSort(int arr[], int low, int high) {
    if (low < high) {
        // pi is partitioning index, arr[p] is now at right place
        int pi = partition(arr, low, high);

        // Separately sort elements before partition and after partition
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
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

    // Sort the numbers using quick sort
    quickSort(numbers, 0, numIntegers - 1);

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
