def solution(age):
    answer = ''
    eng = 'abcdefghijklmnopqrstuvwxyz'
    changeAge = str(age)
    for i in changeAge:
        j = int(i)
        answer += eng[j]
    return answer