def solution(rsp):
    answer = ''
    rspCrt = { '2' : '0', '0' : '5', '5' : '2'}
    for i in rsp:
        answer += rspCrt.get(i)
    return answer