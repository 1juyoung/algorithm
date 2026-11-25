def fac(t):
    if t <= 1:
        return 1

    return t * fac(t-1)


n = int(input())
print(fac(n))