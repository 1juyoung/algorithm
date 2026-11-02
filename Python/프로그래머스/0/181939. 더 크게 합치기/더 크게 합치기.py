def solution(a, b):
    answer = 0
    strA = str(a)
    strB = str(b)
    
    AtoB = strA + strB
    BtoA = strB + strA
    
    a = int(AtoB)
    b = int(BtoA)
    
    answer = b if a < b else a
    return answer
    