import math

def solution(array):
    center = math.floor(len(array) / 2)
    array.sort()
    return array[center]