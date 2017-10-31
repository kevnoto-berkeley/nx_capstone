from solar_sim import *
from time import sleep

p = plant_100MW()
n = len(p.rows)
col0 = p.column0_order
move = {}
moved_counter = 0
columns = []
col_counter = 0
while moved_counter < n:
    c = []
    for row in p.shade.keys():
        if p.shade[row] < .5 and row not in move.keys():
            c.append(row)
            move[row] = 0
            moved_counter += 1
        elif row in move.keys():
            move[row] = -60

    columns.append(c)
    print "Moving column %d" % col_counter
    print "Moved %d rows" % moved_counter
    p.move_rows(move)
    col_counter += 1
print "complete"
print "Found %s columns" % len(columns)

counter = 0
found_counter = 1
rows = [[i] for i in col0]
found = col0
while_loop = 0
move = {}
move[col0[0]] = 0
p.move_rows(move)
while found_counter < n:
    changed = False
    counter = while_loop-p.size[1]+2 if while_loop-p.size[1]+2 >=0 else 0
    for r_index,column in enumerate(reversed(columns[1:while_loop+2])):
        for row in column:
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

