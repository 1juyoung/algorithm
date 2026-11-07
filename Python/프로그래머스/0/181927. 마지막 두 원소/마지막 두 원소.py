def solution(num_list):
    
    answer = num_list.copy()

    if num_list[-1] > num_list[-2]:
        a = num_list[-1] - num_list[-2]
        answer.append(a)
        
    else:
        a = num_list[-1] * 2
        answer.append(a)
        
    return answer