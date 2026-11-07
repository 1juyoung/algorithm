def solution(a, b, c):
    if a == b:
        if b == c:
            return (a + b + c) * (a**2 + b**2 + c**2) * (a**3 + b**3 + c**3)
        else:
            return (a + b + c) * (a**2 + b**2 + c**2)
    elif b == c:
        if a == b:
            return (a + b + c) * (a**2 + b**2 + c**2) * (a**3 + b**3 + c**3)
        else:
            return (a + b + c) * (a**2 + b**2 + c**2)
    elif a == b:
        if b == c:
            return (a + b + c) * (a**2 + b**2 + c**2) * (a**3 + b**3 + c**3)
        else:
            return (a + b + c) * (a**2 + b**2 + c**2)
        
    elif a != b and b != c:
        if a  == c:
            return (a + b + c) * (a**2 + b**2 + c**2)
        else:
            return a + b + c