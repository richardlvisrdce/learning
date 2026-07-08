import os
"""

I'm not actually sure i like this formatting. 

"""
# Example usage
manual_entry = ""
if len(manual_entry) > 0:
    filename = manual_entry
else:
    filename = str(input("Enter the filename: "))

def replace_lines_in_file(filename):
    directory = "Cybersec/"
    path = os.path.join(directory, filename)
    new_lines = []
    
    with open(path, "r") as f:
        for line in f.readlines():
            if line.strip().startswith("-") and not line.strip().startswith("->"):
                new_lines.append(line.replace("-", "->"))
            else:
                new_lines.append(line)

    with open(path, "w") as f:
        for line in new_lines:
            f.write(line)

def reverse_replacement_lines(filename):
    # reverse the replacement of "->" back to "-"
    directory = "Cybersec/"
    path = os.path.join(directory, filename)
    new_lines = []
    
    with open(path, "r") as f:
        for line in f.readlines():
            if line.strip().startswith("->"):
                new_lines.append(line.replace("->", "-"))
            else:
                new_lines.append(line)

    with open(path, "w") as f:
        for line in new_lines:
            f.write(line)

replace_lines_in_file(filename)
print("done")


# reverse_replacement_lines(filename)
# print("done :)