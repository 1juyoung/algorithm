import math

def solution(array):
    answer = 0
    center = math.floor(len(array) / 2)
    array.sort()
    print(center)
    return array[center]