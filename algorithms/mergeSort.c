#include <stdio.h>
#include <stdlib.h>

void merge(int arr[], int l, int m, int r) {
    int i, j, k;
    int n1 = m - l + 1;
    int n2 = r - m;

    // Create temporary arrays
    int L[n1], R[n2];

    // Copy data to temporary arrays L[] and R[]
    for (i = 0; i < n1; i++)
        L[i] = arr[l + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[m + 1 + j];

    // Merge the temporary arrays back into arr[l..r]
    i = 0; // Initial index of first subarray
    j = 0; // Initial index of second subarray
    k = l; // Initial index of merged subarray
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    // Copy the remaining elements of L[], if there are any
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }

    // Copy the remaining elements of R[], if there are any
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
}

void mergeSort(int arr[], int l, int r) {
    if (l < r) {
        // Same as (l+r)/2, but avoids overflow for large l and r
        int m = l + (r - l) / 2;

        // Sort first and second halves
        mergeSort(arr, l, m);
        mergeSort(arr, m + 1, r);

        // Merge the sorted halves
        merge(arr, l, m, r);
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

    // Sort the numbers using merge sort
    mergeSort(numbers, 0, numIntegers - 1);

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
