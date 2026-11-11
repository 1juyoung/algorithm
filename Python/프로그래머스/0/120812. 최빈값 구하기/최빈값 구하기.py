def solution(array):
    d = {}
    a = []
    
    for i in array:
        if i in d:
            d[i] += 1
        else:
            d[i] = 1
    
    for j in d.items():
        if j[1] == max(d.values()):
            a.append(j[0])

    
    if len(a) >= 2:
        return -1
    else:
        return a[0]