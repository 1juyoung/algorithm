n = int(input())
l = []
for i in range(n):
    l.append(list(map(str, input().split(" "))))

s = []

for i in range(len(l)):
    if l[i][0] == 'push':
        s.append(l[i][1])
    elif l[i][0] == 'pop':
        if len(s) == 0:
            print(-1)
        else:
            print(s.pop())
    elif l[i][0] == 'size':
        print(len(s))
    elif l[i][0] == 'empty':
        if len(s) == 0:
            print(1)
        else:
            print(0)
    else:
        if len(s) == 0:
            print(-1)
        else:
            print(s[-1])