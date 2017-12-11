from solar_sim import *
from time import sleep

# Initialize plant
p = plant_100MW()
# determine number of rows
n = len(p.rows)
# Get Y-order of rows
col0 = p.column0_order

##############################################
# Column order
##############################################

# initialize move, initialize counters
move = {}
moved_counter = 0
columns = []
col_counter = 0

# loop while we have not exceeded the number of trackers available
while moved_counter < n:
    # Initialize this column list
    c = []
    # Iterate through all trackers
    for row in p.shade.keys():
        # If the shadow has disappeared, and we did not move it, add it to the column
        if p.shade[row] < .5 and row not in move.keys():
            c.append(row)
            move[row] = 0
            moved_counter += 1
        # If we already moved this row, just make sure the tracker is staying at -60
        elif row in move.keys():
            move[row] = -60
    # After looping through all trackers, add the latest column to columns
    columns.append(c)
    print "Moving column %d" % col_counter
    print "Moved %d rows" % moved_counter
    p.move_rows(move)
    col_counter += 1
# all column order should now be found
print "complete"
print "Found %s columns" % len(columns)


##############################################
# Unique row order
##############################################

# Initialize rows to based on the leading edge order
rows = [[i] for i in col0]
# Add the leading rows to our found list
found = col0

# Initialize counters
counter = 0
found_counter = 1
while_loop = 0
move = {}
# Move the first leading panel to 0
move[col0[0]] = 0
p.move_rows(move)

# Loop while we haven't moved all rows
while found_counter < n:
    # The counter lets us know which row to append the found tracker to
    changed = False
    counter = while_loop-p.size[1]+2 if while_loop-p.size[1]+2 >=0 else 0
    # Because the columns were are in the order of [Easternmost,...,Westernmost]
    # We need to reverse the list, because we are looking for the furthest West 
    # tracker that has been unshaded
    for r_index,column in enumerate(reversed(columns[1:while_loop+2])):
        for row in column:
            # If the tracker is unshaded, add it to the list, behind the tracker
            # that moved and move it to 0
            if p.shade[row] < .5 and row not in found:
                rows[counter].append(row)
                found.append(row)
                found_counter += 1
                move[row] = 0
                changed = True
        counter += 1
    if not changed:
        print "Your last guess was the same"
        break
    while_loop += 1
    # While we havne't moved all of the leading trackers, move the next leading tracker to 0
    if while_loop < len(col0):
        move[col0[while_loop]] = 0
    p.move_rows(move)

print "Guess:"
s = ""
reversed_rows = []
for row in rows:
    r = [i for i in reversed(row)]
    s += str(r) + "\n"
    reversed_rows.append(r)

print s
print "Actual:"
print p

print "Score:"
print "%.2f%%" % (p.check_guess(reversed_rows)*100)

print "Plant has moved %s times" % p.plant_moves

print "Plant has moved %.2f degrees" % p.plant_moves_max_degrees

print "%s individual rows moved" % p.tracker_moves

print "%.2f individual degrees moved" % p.tracker_move_degrees

