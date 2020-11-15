"""Problem: Sorting
Input: A sequence of n keys a1,...,an
Output: The permutation of the input sequence such that a'1 <= a'2 <= ... <= a'n

Implementation with  insertion sort algorithm: start  with a
single element and  successively insert the others  in a way
that maintains the result sorted
"""

def insertion_sort(items):
    for i in range(1, len(items)):
        j = i
        while j > 0 and items[j - 1] > items[j]:
            # Swap items[j] and items[j  - 1] as items[j] is
            # lower than items[j -  1] which was supposed to
            # be the lowest
            items[j - 1], items[j] = items[j], items[j - 1]
            j -= 1
    return items



if __name__ == "__main__":
    items = [0, 260, -1, 1]
    assert insertion_sort(items) == [-1, 0, 1, 260]

