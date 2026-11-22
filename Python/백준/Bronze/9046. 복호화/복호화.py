n = int(input())

for o in range(n):
    tree = {}
    
    word = str(input())
    
    for i in word:
        if i == ' ':
            continue
        tree[i] = tree.get(i, 0) + 1

    nums = list(tree.values())
    maxN = max(tree.values())
    
    if nums.count(maxN) > 1:
        print('?')
        
    else:
        for j, k in tree.items():
            if k == maxN:
                  print(j)