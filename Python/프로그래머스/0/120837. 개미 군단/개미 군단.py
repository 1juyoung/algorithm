def solution(hp):
    answer = 0
    
    answer = hp // 5
    hp = hp % 5
    answer = answer + (hp // 3)
    hp = hp % 3
    if hp == 2:
        return answer + 2
    if hp == 1:
        return answer + 1
    return answer