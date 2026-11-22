n = int(input())
tree = {}
nums = []
count = 0
for o in range(n):
    nums.append(list(map(int, input().split(" "))))
for k, y in nums:
    if tree.get(k) == None:
        tree[k] = y
        
    if tree.get(k) != y:
        count += 1
        tree[k] = y

print(count)