def solution(array):
#     d = {}
#     a = []
    
#     for i in array:
#         if i in d:
#             d[i] += 1
#         else:
#             d[i] = 1
    
#     for j in d.items():
#         if j[1] == max(d.values()):
#             a.append(j[0])

    
#     if len(a) >= 2:
#         return -1
#     else:
#         return a[0]

    count = {}
    for n in array:
        count[n] = count.get(n, 0) + 1

    top = max(count.values())
    modes = [k for k, v in count.items() if v == top]

    return modes[0] if len(modes) == 1 else -1