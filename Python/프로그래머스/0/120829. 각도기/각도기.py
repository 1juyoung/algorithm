def solution(angle):
    answer = 0
    
    if angle < 90:
        answer = 1
        return answer
    if angle == 90:
        answer = 2
        return answer
    if 90 < angle < 180:
        answer = 3
        return answer
    else:
        answer = 4
        return answer