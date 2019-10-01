list = ["oneKB.txt", "twoKB.txt", "threeKB.txt", "fourKB.txt", "fiveKB.txt", "sixKB.txt", "sevenKB.txt", "eightKB.txt", "nineKB.txt", "tenKB.txt"]
test = open("test.txt", "w")
for x in range(100):
	a = x % 3
	test.write(list[a] + "\n")
test.close()