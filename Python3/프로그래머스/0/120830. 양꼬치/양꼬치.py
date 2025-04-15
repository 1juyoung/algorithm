def solution(n, k):
    answer = 0
    price = 0
    
    if n >= 10:
       answer = int(n / 10)
       k -= answer
       price = n * 12000 + k * 2000
    else:
        price = n * 12000 + k * 2000
    return price