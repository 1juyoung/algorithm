def solution(num_list):
    answer = 0
    
    h = ''
    j = ''
    
    for i in num_list:
        if i % 2 == 0:
            j = j + str(i)
        else:
            h = h + str(i)

    return int(h) + int(j)