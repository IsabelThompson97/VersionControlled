## 1.	Box length from first three columns of last line in md3.rst
## 2.	Average volume from md3.mdout
## 3.	Copy md3.rst to md3_NewVolume.rst, replace first three columns of last line with new box length


### ============ MD3, Adjusting the truncated octahedron box length ============ ###

length = 51.0315158

predicted_volume = (1/2)*(4/3)**(3/2)*(length)**3
print("Predicted volume:",predicted_volume)

average_actual_volume = 102563.4482
print("Average volume:",average_actual_volume)

length_3 = average_actual_volume/((1/2)*(4/3)**(3/2))
#print(lenqth_3)

length_new = length_3**(1/3)
print("New length of the box:", length_new)


### ============ Easier, alternative way ============ ###

d = (average_actual_volume/predicted_volume)**(1/3)
#print(d)

l_new = d*length
print("New length of the box:", l_new)