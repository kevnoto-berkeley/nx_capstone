import numpy as np
from solar_sim import row,plant
import matplotlib.pyplot as plt

def est_z(row1,row2,shading1,shading2):
    # row1 is a row instance of row 1's parameters
    # row2 is a row instance of row 2's parameters
    # shading 1 is a 3 element list with row1's tilt angle, row2's tilt angle, and the sun altitude for the event
    # shading 2 is the same as shading 1 but for new angles
    shading_threshold = .2 # % of HALF panel required to trigger shading
    panel1 = row1.p # Abstracted so we can change their values later to add shading offset
    panel2 = row2.p
    theta11 = shading1[0] # row1's tilt angle for shading event 1
    theta12 = shading2[0] # row1's tilt angle for shading event 2
    theta21 = shading1[1]
    theta22 = shading2[1]
    alt1 = shading1[2]
    alt2 = shading2[2]

    # Line intercept, create point of origin and vector for line for both shading events
    p1 = np.array([(panel1/2*(1-shading_threshold))*np.cos(-theta11) + (panel2/2)*np.cos(-theta21),(panel1*(1-shading_threshold)/2)*np.sin(theta11) - (panel2/2)*np.sin(-theta21)])
    l1 = np.array([np.cos(alt1),np.sin(alt1)])
    p2 = np.array([(panel1/2*(1-shading_threshold))*np.cos(-theta12) + (panel2/2)*np.cos(-theta22),(panel1*(1-shading_threshold)/2)*np.sin(theta12) - (panel2/2)*np.sin(-theta22)])
    l2 = np.array([np.cos(alt2),np.sin(alt2)])
    # print "p1: %s" % p1
    # print "l1: %s" % l1
    # print "p2: %s" % p2
    # print "l2: %s" % l2

    # Create matrix for A\b solution
    b = p1-p2
    A = np.array([[-l1[0],l2[0]],[-l1[1],l2[1]]])
    # print "A: %s" % A
    # print "b: %s" % b

    # Compute "time" for intercept point
    [t1,t2] = np.linalg.solve(A,b)
    # print "t1: %s" % t1
    # print "t2: %s" % t2

    # Compute intercept point
    int1 = p1+l1*t1
    int2 = p2+l2*t2

    if False:
        plt.plot([panel1/2*np.cos(theta11),0,0,int1[0],int1[0],int1[0]-panel2/2*np.cos(theta21)],[row1.h+panel1/2*np.sin(theta11),row1.h,0,0,row2.h,row2.h-panel2/2*np.sin(theta21)])
        plt.plot([int1[0]],[int1[1]+row1.h],'ro')
        plt.grid()
        plt.show()
    if all(int1==int2):
        # Intercept found. Delta X and Delta Z
        return int1
    else:
        # print "Intercepts did not match..."
        # print "Error is: %s" % (int2-int1)
        return int1



def main():
    r1 = row(1)
    r2 = row(2)
    s1 = [np.radians(-60),np.radians(-60),np.arctan2(np.sin(np.radians(60)),(2-np.cos(np.radians(-60))))]
    s2 = [np.radians(-45),np.radians(-45),np.arctan2(np.sin(np.radians(45)),(2-np.cos(np.radians(-45))))]
    est_z(r1,r2,s1,s2)

def evaluate_2_point_shading(p,test_angles,atype):
    if atype == 'east':
        p.move_sun(0)
    else:
        p.move_sun(90)
    test_angle_1 = test_angles[0]
    test_angle_2 = test_angles[1]
    shading_threshold = .2 # % of HALF panel required to trigger shading

    p.move_all_rows(test_angle_1)
    # Create counter to stop overrun
    counter = 1
    # Create dict to store sun_alt: [SPC,KEYS,SHADED]
    shading_events = {}
    # Create empty found list to stop double counting
    found = []
    # Loop until everything isnt shaded
    print "First test angle: %s" % test_angle_1
    while len(found) < p.n:
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
        p.move_sun(p.sun_alt + .001)

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
    shading_60 = shading_events

    # Move all rows to 45 degrees East
    p.move_all_rows(test_angle_2)

    # Create counter to stop overrun
    counter = 1
    # Create dict to store sun_alt: [SPC,KEYS,SHADED]
    shading_events = {}
    # Create empty found list to stop double counting
    found = []
    # Loop until everything isnt shaded
    if atype == 'east':
        p.move_sun(0)
    else:
        p.move_sun(90)
    print "Test angle 2: %s" % test_angle_2
    while len(found) < p.n:
        # print "##### Iteration %s #####" % counter
        # print "Sun altitude is: %s" % p.sun_alt
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
                    # Add newly non-shaded keys to lists
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
        p.move_sun(p.sun_alt + .001)

        # Increment counter to prevent runaway
        if counter > 100000 or p.sun_alt > 185:
            print "Counter or sun altitude exceeded!"
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
    shading_45 = shading_events

    ##########################################################
    ##### Debug section for z-height estimation
    ##########################################################
    # print "60 Shading: %s" % shading_60['SPC_18']
    # print "45 Shading: %s" % shading_45['SPC_18']

    # if True:
    # 	theta11 = np.radians(-60)
    # 	theta21 = np.radians(-60)
    # 	theta12 = np.radians(-45)
    # 	theta22 = np.radians(-45)
    # 	plt.plot([p.true_rows[0][3].p/2*np.cos(theta11),0,0,p.inter_row_dists[0][3],p.inter_row_dists[0][3],p.inter_row_dists[0][3]-p.true_rows[0][4].p/2*np.cos(theta21)],
    # 		[p.true_rows[0][3].h+p.true_rows[0][3].p/2*np.sin(theta11),p.true_rows[0][3].h,0,0,p.true_rows[0][4].h,p.true_rows[0][4].h-p.true_rows[0][4].p/2*np.sin(theta21)])
    # 	plt.plot([p.true_rows[0][3].p/2*(1-shading_threshold)*np.cos(theta11),p.true_rows[0][3].p/2*(1-shading_threshold)*np.cos(theta11)+2*np.cos(np.radians(shading_60['SPC_18']))],[p.true_rows[0][3].p/2*(1-shading_threshold)*np.sin(theta11)+p.true_rows[0][3].h,p.true_rows[0][3].p/2*(1-shading_threshold)*np.sin(theta11)+p.true_rows[0][3].h+2*np.sin(np.radians(shading_60['SPC_18']))],'r-')
    # 	plt.axis('equal')
    # 	plt.grid()
    # 	plt.show()
    # est = est_z(p.true_rows[0][3],p.true_rows[0][4],[np.radians(-60),np.radians(-60),np.radians(shading_60['SPC_18'])],[np.radians(-45),np.radians(-45),np.radians(shading_45['SPC_18'])])
    # print "Looking at SPC_18"
    # print p.true_rows[0][3]
    # print p.true_rows[0][4].h - p.true_rows[0][3].h
    # print p.inter_row_dists[0][3]
    # print "Estimated distance: %s" % est
    ##########################################################
    ##### END
    ##########################################################

    # Iterate through all available SPCs and create z height estimations for RHS
    # Initialize empty dict for storing height and distance estimations
    height_est = {}
    # Dummy row, only used for the panel length!
    dummy_row = p.true_rows[0][0]
    # use the two shading angles from earlier
    theta1 = np.radians(test_angle_1)
    theta2 = np.radians(test_angle_2)
    # iterate through all rows
    for row in p.rows:
        # create estimation vector
        if shading_60[row] == 0 or shading_45[row] == 0:
            # print "Non-shaded row"
            continue
        est = est_z(dummy_row,dummy_row,[theta1,theta1,np.radians(shading_60[row])],[theta2,theta2,np.radians(shading_45[row])])
        height_est[row] = est[1]#{'inter_row_dist': est[0],'delta_z':est[1]}
    return height_est

if __name__ == '__main__':
    # Create plant
    p = plant()
    print p

    # Run the Eastern/sunrise shading evaluation
    estimations_east = evaluate_2_point_shading(p,[-60,-45],'east')
    # Run the Western/sunset shading evaluation
    estimations_west = evaluate_2_point_shading(p,[60,45],'west')

    # Find leading rows:
    p.move_all_rows(60)
    p.move_sun(175)
    west_leading = []

    for row in p.rows:
        if p.shade[row] == 0:
            west_leading.append([row])
    print west_leading

    # Evaluate the guesses, initialize a dict

    guesses = {}
    guess_tuples = []
    for key in estimations_east.keys():
        east_dz = estimations_east[key]
        nearest_west_dz_idx = min(range(len(estimations_west.values())),key=lambda x:abs(estimations_west.values()[x]-east_dz))
        nearest_west_dz = estimations_west[estimations_west.keys()[nearest_west_dz_idx]]
        nearest_west_spc =estimations_west.keys()[nearest_west_dz_idx]
        guesses[key] = {'east_dz':east_dz,'west_dz':nearest_west_dz,'east_spc':nearest_west_spc}
        guess_tuples.append((key,nearest_west_spc))
    print guesses

    counter = 1
    while len(guesses) > 0:
        if counter > 100000:
            print "Counter exceeded!"
            break
        if len(guesses) == 0:
            print "Found all rows"
            break
        for idx,row in enumerate(west_leading):
            if not row[-1] in guesses.keys():
                continue
            else:
                found_key = row[-1]
                west_leading[idx].append(guesses[found_key]['east_spc'])
                guesses.pop(found_key)
        counter += 1
    print west_leading
    if len(guesses):
        print guesses