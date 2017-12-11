from solar_sim import row,plant

# Initialize plant
p = plant()
print "#########################"
print "### This is the plant ###"
print p
print "#########################"

# Move everything to East, and move sun to sunrise low angle
p.move_all_rows(-60)
p.move_sun(5)

# Find the leading eastern rows
east_leading_rows = []
for row in p.rows:
	if p.shade[row] == 0:
		east_leading_rows.append(row)
print east_leading_rows

# Determine how many binary digits are required

# We need to know the number of rows the plant has
n_rows = len(p.rows)
# Create a binary string to represent all rows uniquely
max_binary_str = '{0:b}'.format(n_rows)
len_binary_str = len(max_binary_str)