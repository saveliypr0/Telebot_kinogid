sps = [1, 2, 3, 4, 5, 6, 7, 8, 9]
new_sps = list(zip(*[iter(sps)] * 3))
print(new_sps)
