import random

f = open("map_file.txt", "a")

x = 200

for i in range(1000):
    x += random.uniform(-10, 10)
    if x > 100 and x < 500:
        f.write(str(int(x)) + " ")

f.close()

f = open("map_file.txt", "r")
print(f.read())