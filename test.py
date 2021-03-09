






file = open("test.txt", "w")
foo = []

for x in range(1000):
    foo.append(f"Line no: '{x}'") 

file.write("\n".join(foo))
