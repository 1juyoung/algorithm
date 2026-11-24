from collections import deque
n = int(input())
out = []

for _ in range(n):
    p = input().strip()
    t = int(input())
    s = input().strip()

    l = deque(s[1:-1].split(',')) if t > 0 else deque()
    rev = False  # 지금 뒤집힌 상태인지만 기억
    error = False

    for c in p:
        if c == 'R':
            rev = not rev
        else:
            if not l:
                error = True
                break
            if rev:
                l.pop()  # 뒤집힌 상태면 '앞'은 실제로는 뒤쪽
            else:
                l.popleft()

    if error:
        out.append('error')
    else:
        if rev:
            l.reverse()  # 마지막에 한 번만 실제로 뒤집기
        out.append('[' + ','.join(l) + ']')

print('\n'.join(out))