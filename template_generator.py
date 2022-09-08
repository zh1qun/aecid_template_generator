"""This is an implementation of the Equalmerge algorithm for character-based log template generation."""

import warnings
import sys
import timeit
import template_config

sys.setrecursionlimit(5000) # Needed to calculate the LV-distance
t1 = timeit.default_timer()
time_temp = 0

class template:
	def __init__(self, stringlist):
		self.stringlist = stringlist # List of the strings of the template
		self.wildcardends = [0,0] # This list states if there are Wildcards at the beginning or end of the template
		self.stringpos = [] # List of the positions of the strings in the line
		self.update()
		
	# splits the i-th string of the template at the character which is located at pos
	def splitString(self, i, pos, newGap):
		self.updateStringpos()
		if len(self.stringlist) <= i or len(self.stringlist[i]) <= pos:
			warnings.warn("False Input in splitString")
		else:
			self.stringlist.insert(i, self.stringlist[i])
			self.stringlist[i] = self.stringlist[i][0:pos+1]
			self.stringlist[i+1] = self.stringlist[i+1][pos+1:]

	# splits the i-th string and deletes the character which is located at pos
	def splitdelString(self, i, pos, newGap):
		self.updateStringpos()
		if len(self.stringlist) <= i or len(self.stringlist[i]) <= pos:
			warnings.warn("False Input in splitdelString")
		else:
			self.stringlist.insert(i, self.stringlist[i])
			self.stringlist[i] = self.stringlist[i][0:pos]
			self.stringlist[i+1] = self.stringlist[i+1][pos+1:]
	
	# removes the empty strings of the template
	def update(self):
		# checks if the first or last string is empty and saves the information in self.wildcardends
		if len(self.stringlist[0]) == 0:
			self.wildcardends[0] = 1
		if len(self.stringlist[-1]) == 0:
			self.wildcardends[1] = 1

		# removes the empty strings
		for i in range(len(self.stringlist)-1,-1,-1):
			if len(self.stringlist[i]) == 0:
				del self.stringlist[i]
		
		# updates the string positions
		self.stringpos = [0]
		for i in range(1,len(self.stringlist)):
			self.stringpos += [len(self.stringlist[i-1])+self.stringpos[i-1]]
	
	# updates the string positions
	def updateStringpos(self):
		self.stringpos = [0]
		for i in range(1,len(self.stringlist)):
			self.stringpos += [len(self.stringlist[i-1])+self.stringpos[i-1]]

	# returns the euclidean norm of the lengths of the strings in t.stringlist
	def euclen(self):
		tmp = 0
		for string in self.stringlist:
			tmp += (len(string))**2
		
		return tmp**(1/2)
	
	# Deletes all Numbers of the first string in the template
	def deletenumbers(self):
		if self.stringlist != []:
			for i in range(len(self.stringlist[0])-1,-1,-1):
				if self.stringlist[0][i].isdigit():
					self.splitdelString(0,i,1)

	# returns the total number of characters in the template
	def len(self):
		return self.stringpos[-1]+len(self.stringlist[-1])
		
	# prints stringlist, stringpos, and wildcardends
	def printT(self):
		print("template:____________")
		self.updateStringpos()
		print("Stringlist: ", self.stringlist)
		print("Stringpos: ", self.stringpos)
		print("Wildcardends: ", self.wildcardends)


# This function calculates recursively the (x,y)-entry of the Levenshtein-Matrix
def LevenM(M, line1, line2, x, y):
	if x == 0:
		M[x][y] = y
		return M
	if y == 0:
		M[x][y] = x
		return M

	if M[x-1][y] == -1:
		M = LevenM(M,line1, line2,x-1,y)
	if M[x][y-1] == -1:
		M = LevenM(M,line1, line2,x,y-1)
	if M[x-1][y-1] == -1:
		M = LevenM(M,line1, line2,x-1,y-1)
	
	if line1[x-1] == line2[y-1]:
		M[x][y] = min(M[x-1][y]+1,M[x][y-1]+1,M[x-1][y-1])
	else:
		M[x][y] = min(M[x-1][y]+1,M[x][y-1]+1,M[x-1][y-1]+1)
	
	return M

# function that takes a template t and a line and changes the strings in the template to fit the line
def fit(t, line):
	tmp1 = [-1 for i in range(len(t.stringlist))] # list for the positions of the strings of the template in the line
	stringlist_sorted = t.stringlist.copy() # list of the sorted strings, which is used to find the substrings in the line starting with the longest string of the template
	stringlist_sorted.sort(key = len, reverse = True)
	
	# save the positions of the strings of the template in the line and save the position in tmp1
	for string in stringlist_sorted:
		i = -1
		if len(string) < template_config.equal_min_len:
			continue
		while True:
			i = t.stringlist[i+1:].index(string)+i+1
			if tmp1[i] == -1:
				tmp1[i] = line.find(string, max([x+len(l)+1 for x, l in zip(tmp1[:i], t.stringlist[:i])]+[0]), min([x for x in tmp1[i+1:] if x > -1]+[len(line)]))
				break
	
	# checks if the first string of the template is found, but does not appear at the beginning of the line
	if tmp1[0] != -1 and tmp1[0] != 0:
		t.wildcardends[0] = 1
	
	# checks if the last string of the template is found, but does not appear at the beginning of the line
	if tmp1[-1] != -1 and tmp1[-1] + len(t.stringlist[-1]) != len(line):
		t.wildcardends[1] = 1

	# matches the remaining strings of the template, by finding the indices of neighbouring unmatched strings and using fit2
	index_tmp = -1
	for i in range(len(t.stringlist)-1,-1,-1):
		if tmp1[i] == -1:
			if index_tmp == -1:
				index_tmp = i
		else:
			if index_tmp != -1:
				[t,tmp1] = fit2(t,i+1,index_tmp,line,tmp1)
				index_tmp = -1
	if index_tmp != -1:
		[t,tmp1] = fit2(t,0,index_tmp,line,tmp1)

	t.update()
	return t

# merges the i-j-th strings of s and cuts and/or deletes the/ parts of the strings of s to fit the substring
def fit2(t,i,j,line,tmp1):
	# get the indices [l:u], such that t.stringlist[i:j+1] should be matched with [l:u] from the line
	l = 0; u = -1
	if i != 0:
		l = tmp1[i-1]+len(t.stringlist[i-1])
	
	if j != len(tmp1)-1:
		u = tmp1[j+1]
	
	if u == -1: 
		u = len(line)

	# from now on the Levenshtein-distance from t.stringlist[i:j+1] to this shorter substring is calculated and t.stringlist[i:j+1] is changed to fit the line
	substring = line[l:u]

	# merge the strings of the template
	t_string = ""
	indizes_tmp=[0]
	for k in range(i,j+1):
		t_string += t.stringlist[k]
		indizes_tmp.append(len(t.stringlist[k])+indizes_tmp[-1])

	# calculate the LV-distance
	M = [[-1 for y in range(len(substring)+1)] for x in range(len(t_string)+1)]
	M = LevenM(M,t_string,substring,len(t_string),len(substring))
	tmp2=True; tmp3=[]; x = len(t_string); y = len(substring)

	# the constructionpath of M in M2 is followed and the directions are saved in tmp3 for further processing:
	# 0 = diagonal step with equal symbols, 1 = diagonal step without equal symbols, 2 = step in x-direction, 3 = step in y-direction
	while True:
		if x == 0:
			tmp3 += [3 for j in range(y)]
			break
		if y == 0:
			tmp3 += [2 for j in range(x)]
			break
		
		if tmp2 and M[x][y-1]+1 == M[x][y]:
			tmp3 += [3]; y -= 1
		elif not tmp2 and M[x-1][y]+1 == M[x][y]:
			tmp3 += [2]; x -= 1
		elif M[x-1][y-1] == M[x][y] and t_string[x-1] == substring[y-1]:
			tmp3 += [0]; x -= 1; y -= 1
			tmp2 = False
		elif M[x][y-1]+1 == M[x][y]:
			tmp3 += [3]; y -= 1
		elif M[x-1][y]+1 == M[x][y]:
			tmp3 += [2]; x -= 1
		else:
			tmp3 += [1]; x -= 1; y -= 1

	# the strings of t are now cut into the desired pieces
	x = len(t_string)-1
	y = len(substring)-1
	bool_tmp = False
	if len(indizes_tmp) > 1:
		del(indizes_tmp[-1])

	# adapts the template to the new line according to the calculated distance
	for k in range(len(tmp3)):
		# the x-th element in the strings of the template is considered and it is decided if it is kept or cut away
		if x+1 == indizes_tmp[-1]:
			t.update()
			if len(t.stringlist) == len(tmp1):
				tmp1[j] = y+l+1
			else:
				del tmp1[j]
			j -= 1
			del(indizes_tmp[-1])
			bool_tmp = False
		else:
			bool_tmp = True
		if x < 0:
			break
		elif tmp3[k] == 0:
			x -= 1
			y -= 1
		elif tmp3[k] == 1:
			t.splitdelString(j,x-indizes_tmp[-1],1)
			if t.stringlist[j+1] != "" and bool_tmp:
				tmp1.insert(j+1, y+l+1)

			x -= 1
			y -= 1
		elif tmp3[k] == 2:
			t.splitdelString(j,x-indizes_tmp[-1],0)
			if t.stringlist[j+1] != "" and bool_tmp:
				tmp1.insert(j+1, y+l+1)

			x -= 1
		elif tmp3[k] == 3:
			t.splitString(j,x-indizes_tmp[-1],1)
			if t.stringlist[j+1] != "" and bool_tmp:
				tmp1.insert(j+1, y+l+1)
			y -= 1

	t.update()

	if len(t.stringlist) == len(tmp1):
		tmp1[i] = y+l+1
	else:
		del tmp1[i]

	return [t,tmp1]

def mean(v):
	return sum(v) / max(len(v),1)

# printmatrix
def printM(M):
	for i in range(len(M)):
		print(M[i])
	
	return

def getTemplate(t):
        result = ''
        if t.stringlist != []:
                if t.wildcardends[0] == 1:
                        result += "§"
                result += "§".join(t.stringlist)
                if t.wildcardends[1] == 1:
                        result += "§" + "\n"
                else:
                        result += "\n"
        return result

# main program
fobj1 = open(template_config.input_file, "r")
fobj2 = open(template_config.output_file, "w")

t = template([""])
tmp = 0
t2 = 0; t3 = 0 # time
tmp2 = [[],[],[]] # similarity1, similarity2, idle state
tmp3 = 1
len_t = -1
tmp4 = 0 # settle down for idle state
cluster = [] # lines in cluster
first_line = True

for line in fobj1:
	if first_line == True:
		if line.startswith(template_config.new_representative_pretext) == False:
			print("First line did not start with \"" + template_config.new_representative_pretext + "\", make sure to use pre-clustered log data! Aborting...")
			sys.exit()
		first_line = False

	# ignore empty lines and lines which start with substrings of the ignore_line_pretext list
	if line == "\n" or any(line[0:len(template_config.ignore_line_pretext[i])] == template_config.ignore_line_pretext[i] for i in range(len(template_config.ignore_line_pretext))):
		continue

	# initialise a new template
	elif line[0:len(template_config.new_representative_pretext)] == template_config.new_representative_pretext:
		fobj2.write(getTemplate(t)) # write the last template to the file if neccessary

		t2 = timeit.default_timer()
		if tmp != 0:
			print("Cluster", tmp, "finished after:", str(t2-t3)[0:8], "s, total runtime:", str(t2-t1)[0:8], "s")

		if len_t != -1: # add the calculated similarities
			s1 = len("".join(t.stringlist))/(len_t/tmp3)*100
			s2 = t.euclen()/(len_t/tmp3)*100
			idle = (tmp4+1)/tmp3*100
			tmp2[0].append(s1)
			tmp2[1].append(s2)
			tmp2[2].append(idle)
			tmp4 = 0
			if template_config.print_simscores == True:
				fobj2.write("  Sim-Score = " + str(s1)[0:5] + "%, Euclidean-Score = " + str(s2)[0:5] + "%, Stability Reached = " + str(idle)[0:5] + "%\n\n")
		t3 = t2
		tmp += 1
		# if the line is to long initialise the template as "Length of line more than 1850"
		if len(line[len(template_config.new_representative_pretext):-1]) > 1850:
			t = template(["Length of line more than 1850"])
			len_t = -1 # similarity
		# otherwise initialise the template normally
		else:
			t = template([line[len(template_config.new_representative_pretext):-1]])
			if template_config.without_numbers:
				t.deletenumbers()
				t.update()
			len_t = len(line[len(template_config.new_representative_pretext):-1]) # similarity
			tmp3 = 1
			cluster = [line[len(template_config.new_representative_pretext):-1]] # lines in cluster

	# adapt the template to a new line
	else:
		if t.stringlist == ["Length of line more than 1850"]:
			continue
		else:
			if template_config.number_skipped_characters < 1:
				l = line
			else:
				l = line[template_config.number_skipped_characters:-1]
			if l not in cluster:
				cluster.append(l) # lines in cluster
				tmp_str = t.stringlist.copy()
				t = fit(t, l)
				if tmp_str != t.stringlist: # idle state
					tmp4 = tmp3
				len_t += len(l) # similarity
				tmp3 += 1

fobj2.write(getTemplate(t)) # write the last template to the file if neccessary

t2 = timeit.default_timer()

if len_t != -1: # add the calculated similarities
	s1 = len("".join(t.stringlist))/(len_t/tmp3)*100
	s2 = t.euclen()/(len_t/tmp3)*100
	idle = (tmp4+1)/tmp3*100
	tmp2[0].append(s1)
	tmp2[1].append(s2)
	tmp2[2].append(idle)
	tmp4 = 0
	if template_config.print_simscores == True:
		fobj2.write("  Sim-Score = " + str(s1)[0:5] + "%, Euclidean-Score = " + str(s2)[0:5] + "%, Stability Reached = " + str(idle)[0:5] + "%\n")

fobj2.write("\n\nTotal time: "+str(t2-t1)[0:8]+"s\n")
print("Cluster",tmp,"finished after:", str(t2-t3)[0:8], "s, total runtime:", str(t2-t1)[0:8], "s")

# write the calculated similarities
fobj2.write("\nOverall scores:\n")
fobj2.write("Sim-Score: "+str(mean(tmp2[0]))[0:8]+"%\n")
fobj2.write("Euclidean-Score: "+str(mean(tmp2[1]))[0:8]+"%\n")
fobj2.write("Template stable after processing "+str(mean(tmp2[2]))[0:8]+"%\n")
