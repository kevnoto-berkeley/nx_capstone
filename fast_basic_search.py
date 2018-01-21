from solar_sim import row,plant,plant_100MW,plant_custom
import numpy as np
import pandas
import sys
import time

def assign_binary(n_t):
    """
    Recursively assign binary number to list of trackers
    Takes in a number of trackers, returns the binary string required to
    uniquely identify it
    """
    r = []
    for i in range(0,n_t):
        if i < n_t // 2:
            r.append('1')
        else:
            r.append('0')
    if n_t > 2:
        return [m+n for m,n in zip(r,assign_binary(n_t//2)+assign_binary(n_t -
                                                                         n_t//2))]
    else:
        return r


def evaluate_crit_shading(p,atype,sun_increment = .01):
    if atype == 'east':
        p.move_sun(0)
    else:
        p.move_sun(90)
    shading_threshold = .2 # % of HALF panel required to trigger shading

    # Create counter to stop overrun
    counter = 1
    # Create dict to store sun_alt: [SPC,KEYS,SHADED]
    shading_events = {}
    # Create empty found list to stop double counting
    found = []
    # Loop until everything isnt shaded
    while len(found) < p.n:
        print_progress(len(found),p.n,prefix="Sun Alt: "+str(p.sun_alt),bar_length=50)
        # print "##### Iteration %s #####" % counter
        # print "Sun altitude is: %s" % p.sun_alt
        # print "Found %s rows" % len(found)
        # Initialize list to store SPC keys
        non_shaded = []
        # Loop through shading results
        if atype == 'east':
            for key in p.shade.keys():
                if key in found: # Check if already found
                    continue
                elif p.shade[key] <= shading_threshold/2:
                    # Add newly non-shaded keys to lists
                    non_shaded.append(key)
                    found.append(key)
                else:
                    pass
        else:
            for key in p.shade.keys():
                if key in found: # Check if already found
                    continue
                elif p.shade[key] >= shading_threshold/2:
                    # Add newly shaded keys to lists
                    non_shaded.append(key)
                    found.append(key)
                else:
                    pass
        # Store the non-shaded to dict
        if len(non_shaded):
            for key in non_shaded:
                shading_events[key] = p.sun_alt
        # print "Found %s rows" % (len(non_shaded))
        # print "Total rows found: %s" % len(found)

        # Move the sun
        p.move_sun(p.sun_alt + sun_increment)

        # Increment counter to prevent runaway
        if counter > 100000 or p.sun_alt > 185:
            print "Counter or sun angle exceeded limit!"
            for row in p.rows:
                if not row in found:
                    found.append(row)
                    shading_events[row] = 0
            break
        counter += 1

    if len(found) == p.n:
        print "Found all rows!"
    # print "Shading Events:"
    # for key in shading_events.keys():
    # 	print "%s; %s" % (key,shading_events[key])
    return shading_events

def get_z(theta1,theta2,p1,p2,r12):
    pass

def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    t = float(str(time.time())[str(time.time()).find('.'):])
    if 0 <= t < .25:
        anim = "/"
    elif .25 <= t < .5:
        anim = "-"
    elif .5 <= t < .75:
        anim = "\\"
    else:
        anim = "-"
    sys.stdout.write('\r%s |%s| %s%% %s %s' % (prefix, bar, percents, suffix, anim)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

if __name__ == '__main__':
    # Initialize plant
    p = plant_100MW()
    p.set_row_distances(value=2)
    # print "#########################"
    # print "### This is the plant ###"
    # print p
    # print "#########################"
    test_angle = -45
    move_angle = -30
    atype = 'east'
    sun_increment = .1


    print "#########################"
    print "### Evaluating initial shading angles ###"
    print "Move all rows to initial test angle: %.2f" % test_angle
    p.move_all_rows(test_angle)
    print "Evaluate shading"
    shading60 = evaluate_crit_shading(p, atype,sun_increment = sun_increment)
    shading_sequence = pandas.DataFrame({'shading60':shading60.values()},
                                        index=shading60.keys())
    leading_rows = []
    for row in shading60:
        if shading60[row] == 0:
            leading_rows.append(row)
    print "Leading Rows: %s" % leading_rows
    print "#########################"
    # We need to know the number of rows the plant has
    print "Determine binary strings"
    n_rows = len(p.rows)
    max_binary = "{0:b}".format(n_rows)
    strfmt = "{0:0%db}" % len(max_binary)
    # Create a list of binary strings to represent all rows uniquely
    # b_list = assign_binary(n_rows)
    # Assign each SPC to a binary string
    spc_move_sequences = {}
    print "Assign strings, create data frame"
    for idx,row in enumerate(p.rows):
        # spc_move_sequences[row] = b_list.pop(0)
        spc_move_sequences[row] = strfmt.format(idx)
    move_sequence_df = pandas.DataFrame({
        'move_sequence':spc_move_sequences.values()},
        index=spc_move_sequences.keys())
    shading_sequence = pandas.concat([shading_sequence,move_sequence_df],
                                     axis=1)

    print "#########################"
    print "Looping through %d moves" % len(max_binary)
    for i in range(0,len(max_binary)):
        print "Iteration: %d" % i
        move = {}
        n = len(spc_move_sequences)
        for row in spc_move_sequences:
            bit = int(spc_move_sequences[row][i])
            if bool(bit):
                move[row] = move_angle
            else:
                move[row] = test_angle
        p.move_rows(move)
        shading_results = evaluate_crit_shading(p,atype='east',
                                                sun_increment=sun_increment)
        shading_df = pandas.DataFrame({'shading_move_%d' %
                                       i:shading_results.values()},
                                      index=shading_results.keys())
        shading_sequence = pandas.concat([shading_sequence, shading_df],
                                         axis=1)
    print "COMPLETE"
    print "#########################"
    print "Solving for interpreted bitstrings"
    delta_unmoved = 1.5 # if you are unmoved, need a shading change of at
    # least 1.5 degrees to indicate the leading row moved
    delta_moved = 2.5 # if you are moved, need a shading change of at least
    # 2.5 FROM REFERENCE UNMOVED STATE to indicate the leading row moved
    read_sequence_dict = {}
    for row_name,row in shading_sequence.iterrows():
        shading_values = []
        shading_ref = row['shading60']
        move_sequence = row['move_sequence']
        for i in range(0,len(max_binary)):
            shading_values.append(row['shading_move_'+str(i)])
        shading_delta = [abs(i-shading_ref) for i in shading_values]
        read_sequence = ''
        for idx,val in enumerate(move_sequence):
            if val == '0':
                if shading_delta[idx] >= delta_unmoved:
                    read_sequence += '1'
                else:
                    read_sequence += '0'
            else:
                if shading_delta[idx] >= delta_moved:
                    read_sequence += '1'
                else:
                    read_sequence += '0'
        read_sequence_dict[row_name] = read_sequence
    read_sequence_df = pandas.DataFrame({
        'read_sequence': read_sequence_dict.values()},
        index=read_sequence_dict.keys())
    shading_sequence = pandas.concat([shading_sequence, read_sequence_df],
                                     axis=1)
    shading_sequence.to_csv('shading_results.csv')
    print "There were %s move strings, read %s unique strings" % (len(
        shading_sequence['move_sequence']),len(set(shading_sequence['read_sequence'])))
    print "#####################"
    print "Recreate rows of trackers"
    # Generate dict showing evaluated row as key , and the row in front of
    # it as the value

    # Very confusing... Makes two dictionaries from 3 values, to relate them
    #  all. The row_name_to_read_string is a dict with key = SPC, and value
    # = the move sequence it READ from the neighboring panel. the
    # move_string_to_row_name dict is a dict with key = the MOVE sequence,
    # and value is the SPC that did this move sequence. With this I know
    # which SPC read which move from which neighboring SPC...

    # 3 list values
    eval_row = shading_sequence.index
    read_bitstring = shading_sequence['read_sequence'].tolist()
    move_sequence = shading_sequence['move_sequence'].tolist()
    # 2 dicts
    row_name_to_read_string = dict(zip(eval_row,read_bitstring))
    move_string_to_row_name = dict(zip(move_sequence,eval_row))

    # Populate the SPC in front of it by looking up values from one dict to
    # the next.
    row_in_front = {}
    for row in row_name_to_read_string:
        if row in leading_rows: continue
        row_in_front[row] = move_string_to_row_name[row_name_to_read_string[
            row]]

    ##### RECREATE PLANT ROWS BASED ON SERIAL NUMBER
    counter = 0
    # seed rows with the leading rows we know
    recreated_rows = [[f] for f in leading_rows]
    has_changed = True
    found = []
    # Loop as long as recreated_rows changes, and counter less than value
    while counter < 1000 and has_changed:
        has_changed = False
        # loop through all the known pairs
        for row in row_in_front:
            # if we already found it, skip it
            if row in found: continue
            left = row
            right = row_in_front[row]
            # Loop through all our known row orders
            for idx,recreated_row in enumerate(recreated_rows):
                # if you find it already in our known order, add it to left or right
                # probably only going to add to the left side, given we start
                # with Easternmost rows...
                if recreated_row[0] == right:
                    recreated_rows[idx] = [left] + recreated_row
                    has_changed = True
                    found.append(row)
                    break
                elif recreated_row[-1] == left:
                    recreated_rows[idx] = recreated_row + [right]
                    has_changed = True
                    found.append(row)
                    break
                else:
                    pass
        counter += 1

    #### GRADING
    flat_rows = []
    max_cols = 0
    for row in recreated_rows:
        flat_rows.append(row)
        max_cols = max(max_cols,len(row))
        # print flat_rows[-1]
    # print "Compare to plant:"
    # print p
    print "Found %s rows, %s cols" % (len(recreated_rows),max_cols)
    print "True rows is of size %s" % p.size

    score = 0
    total = 0
    for field_row in p.true_rows:
        for guess_row in flat_rows:
            if guess_row[0] == field_row[0].serial_number:
                for idx,row in enumerate(field_row):
                    try:
                        if row.serial_number == guess_row[idx]:
                            score += 1
                    except IndexError:
                        print "Lengths of this row were not the same: %s vs " \
                              "%s" % (len(field_row),len(guess_row))
                    total += 1
    print "Out of %s, found %s accurately. %.2f%%" % (total,score,
                                                      score/total*100)
    pass