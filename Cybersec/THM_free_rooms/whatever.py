# whatever.py

def reverse_str(s: str):
    new = ""
    for i in range(len(s) - 1, -1, -1):
        new += (s[i])
    return new

def palindrome_in_range(start: int, end: int):
    found: list[int] = []
    for i in range(start, end + 1):
        s = str(i)
        if s == reverse_str(s):
            found.append(i)
    print(found)
    return found

palindrome_in_range(1,879)