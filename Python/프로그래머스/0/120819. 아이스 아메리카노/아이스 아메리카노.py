def solution(money):
    answer = []
    a = 0
    
    while money >= 0:
        a = a + 1
        money = money - 5500
    
    answer.append(a-1)
    answer.append(money+5500)
    return answer