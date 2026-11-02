def solution(n):
    answer = 0
    i = 1
    
    # n이 짝수 ->  양의 정수 제곱의 합
    if n % 2 == 0:
        while(i <= n):
            if i % 2 == 0:
                answer += i**2
            i += 1
            
    # n이 홀수 => 양의 정수의 합
    else:
        while(i <= n):
            if i % 2 != 0:
                answer += i
            i += 1
            
    return answer