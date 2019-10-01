test = open("test.txt", "w+")
files = ["oneKB.txt", "twoKB.txt", "threeKB.txt", "fourKB.txt", "fiveKB.txt", "sixKB.txt", "sevenKB.txt", "eightKB.txt", "nineKB.txt", "tenKB.txt"]
for x in range(200):
	a = x % len(files) 
	test.write(files[a] +"\n")
