def solution(n, control):
    
    c = {'w': 1, 's': -1, 'd': 10, 'a': -10}
    
    for i in control:
        if i in c: # c에서 i 값이 있으면 실행
            n = n + c[i]
    
    return n