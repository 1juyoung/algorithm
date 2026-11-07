def solution(code):
    answer = []
    # 시작 했을 때 mode가 0
    mode = '0'
    
    #code가 끝날 때까지 반복
    for i in range(len(code)):
        # mode가 1이면
        if mode == '1':
            if code[i] == '1':
                mode = '0'
            else:
                if i % 2 != 0:
                    answer.append(code[i])
        # mode가 0이면
        else:
            if code[i] == '1':
                mode = '1'
            else:
                if i % 2 == 0:
                    answer.append(code[i])

    # if len(answer) == 0:
    #     return "EMPTY"
    return "".join(answer) or "EMPTY"