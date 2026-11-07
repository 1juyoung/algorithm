def solution(arr, queries):
    for i, j in queries:
        a = arr[i]
        arr[i] = arr[j]
        arr [j] = a
    return arr