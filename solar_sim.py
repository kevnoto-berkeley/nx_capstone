from __future__ import division
import pandas
import random
import numpy
import matplotlib.pyplot as plt
np = numpy

###### Solar shading simulator for nx-capstone #####
# The program is broken into two halves; this first half declares functions
# to use, much like you need to make new .m files for each function in MATLAB
# The second half starts at the "if "__name__" == __main__:" line, which
# is all the code execution.

# You should write your code under the "if "__name__" == __main__:" line
# I have some examples of what you need to do to get the program to work there






class row():
    # The row class, holds useful unique information for each row in a plant
    def __init__(self,sn):
        self.angle = -60.0 # Tilt angle, -East / +West
        self.shade = 0.0 # Shade distance, -From East/ +From West
        self.h = 1.5 # meters. height to rotation point from ground level
        self.p = 1.0 # meters. cord length of panel
        self.serial_number = sn # string, typically SPC_XXXX

    def move_to(self,angle):
        # Moves angle to new angle
        self.angle = angle

    def __str__(self):
        # String representation
        return self.serial_number

    def __repr__(self):
        # Print representation, shows row name, angle, and shading value
        return "<Row: %s @ %02d deg, %.2f shaded>" % (self.serial_number,self.angle,self.shade)

class plant():
    def __init__(self):
        # Make a fake site of dimensions [rows,columns]
        self.size = [4, 5]
        self.n = self.size[0] * self.size[1]
        # Initialize rows
        self.true_rows = []
        # Create a dict so we can easily grab the random index
        self.true_rows_dict = {}
        # Initialize logging variables
        self.tracker_moves = 0
        self.tracker_move_degrees = 0
        self.plant_moves = 0
        self.plant_moves_max_degrees = 0
        # Create a random order for all SPCs
        self.random_order = [6, 15, 0, 17, 19, 8, 10, 3, 16, 7, 13, 
            4, 9, 1, 11, 14, 12, 5, 2, 18]
        # Initialize the serial number counter
        count = 0
        # Create all of the rows in proper order and assign serial number
        for i in range(self.size[0]):
            r = []
            for j in range(self.size[1]):
                serial_number = "SPC_%02d" % (self.random_order[count]+1)
                # Add the serial number to the dict of indicies
                self.true_rows_dict[serial_number] = (i,j)
                count += 1
                r.append(row(serial_number))
            self.true_rows.append(r)
        # Flatten the true_rows list and create a flat list in random order
        self.true_rows_list = numpy.array([i for sublist in self.true_rows for i in\
             sublist])[self.random_order]
        self.rows = [i.serial_number for i in self.true_rows_list]
        # Create an attribute to show the first column's order
        self.column0_order = [i.serial_number for sublist in self.true_rows for i in sublist[-1:]]
        # Randomize all heights and set random row distances
        self.randomize_heights()
        self.set_row_distances()

        # The sun altitude
        self.sun_alt = 5

        # Evaluate current plant shade
        self.evaluate_shade()

    def __repr__(self):
        # Print representation of TRUE field, will create new-line at each new row
        # Direction is true to North-South and East-West directions
        s = ""
        for row in self.true_rows:
            s += str(row) + "\n"
        return s

    def set_row_distances(self, value = None):
        # changes the inter-row distances of all rows to the list below
        row_dists = [2.0002996317,
                1.9882354791,
                1.96684390181,
                1.96069514162,
                2.02803445507,
                1.99504888156,
                2.01621945466,
                2.00230869091,
                1.98767105864,
                1.95160802133,
                2.00561340961,
                2.03403038484,
                2.0118066417,
                2.04580375887,
                1.97722309242,
                2.01898009575,]
        self.inter_row_dists = []
        for i in range(self.size[0]):
            r = []
            if value is None:
                for j in range(self.size[1]-1):
                    r.append(row_dists.pop(0))
            else:
                r = [value] * (self.size[1]-1)
            self.inter_row_dists.append(r)


    def randomize_heights(self):
        # changes the heights of all rows to the list below
        heights = [1.57268476517,
                1.47766647019,
                1.50751702603,
                1.56912717664,
                1.49434822186,
                1.58583272025,
                1.52406622356,
                1.40642478742,
                1.41750472147,
                1.42107265238,
                1.5235258482,
                1.58925409889,
                1.56809437096,
                1.52878004193,
                1.47051924057,
                1.587994754,
                1.54181340644,
                1.59659037451,
                1.48319296975,
                1.43860845234,]

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self.true_rows[i][j].h = heights.pop(0)

    def move_rows(self,movements):
        # Takes in a dict of serial numbers with values that are movements, and moves the 
        # corresponding tracker by looking up the SPC serial number

        # Increment plant_moves
        self.plant_moves += 1
        # Generate list of keys to iterate
        keys = movements.keys()
        # Keep track of maximum angle movement for logging
        max_degrees = 0
        # Generate list of keys to check against
        true_rows_keys = self.true_rows_dict.keys()

        # Iterate through all movements and move meatching rows
        for key in keys:
            # Check if the row exists in the plant
            if key not in true_rows_keys:
                raise BaseException("Your SPC could not be found in the Plant. Your Key: %s" % key)

            # Assign the row, and move it if the current angle changes
            row = self.true_rows[self.true_rows_dict[key][0]][self.true_rows_dict[key][1]]
            if row.angle != movements[key]:
                self.tracker_moves += 1
                dist = abs(row.angle - movements[key])
                # Track the movement of each tracker
                self.tracker_move_degrees += dist
                max_degrees = max(max_degrees,dist)
            row.move_to(movements[key])
        # Track the maximum movement of the plant move
        self.plant_moves_max_degrees += max_degrees
        # Re-evaluate the shade
        self.evaluate_shade()
        return self.shade

    def move_all_rows(self,position):
        for r in self.true_rows:
            for row in r:
                row.angle = position
        self.evaluate_shade()
        return self.shade

    def move_sun(self,alt):
        # Moves the sun to alt and reevaluates shade
        self.sun_alt = alt
        self.evaluate_shade()
        return self.shade

    def evaluate_shade(self):
        if self.sun_alt >= 90:
            self.shade = self.evaluate_shade_west()
            return self.shade
            
        # print "Evaluating EAST shading"
        # Use geometry to calculate shading

        # Create dict for storing shading values
        shades = {}

        # Iterate through rows from North to South, and West to East to evaluate shade
        for i in range(0, self.size[0]):
            last = None
            for j in range(0, self.size[1]):
                # Skip the first Western row
                if last is None:
                    pass
                # Calculate shade from row2 onto row1
                else:
                    # Get the inter-row distance
                    r12 = self.inter_row_dists[i][j-1]
                    # Assign rows 1 and 2
                    row1 = last
                    row2 = self.true_rows[i][j]
                    # Create the line of row1's solar panel
                    m1 = numpy.tan(numpy.deg2rad(row1.angle))
                    b1 = row1.h
                    # Create the line of shade originating from row2's tip at the angle of sun_alt
                    m2 = numpy.tan(numpy.deg2rad(self.sun_alt))
                    b2 = row2.h - row2.p/2 \
                        *numpy.sin(numpy.deg2rad(row2.angle))-m2*(r12-row2.p \
                            /2*numpy.cos(numpy.deg2rad(row2.angle)))
                    # Intersect the two lines in cartesian coordinates
                    x_int = (b1-b2)/(m2-m1)
                    y_int = m1*x_int + b1
                    x_end = row1.p/2 * numpy.cos(numpy.deg2rad(row1.angle))
                    y_end = m1*x_end + b1
 
                    # Evaluate the distance from row1's panel's midpoint and check if it shades
                    # if NOT, shade = 0
                    # if YES, shading distance is the 2-norm distance to origin
                    if x_int >= row1.p/2*numpy.cos(numpy.deg2rad(row1.angle)):
                        row1.shade = 0
                    else:
                        # 2-norm to row1's midpoint
                        shade_dist = numpy.sqrt((x_end-x_int)**2 
                            + (y_end-y_int)**2)
                        # Normalize to 1 if larger than 1
                        row1.shade = 1 if shade_dist > 1 else shade_dist
                    # add the new shading value to the shade dict
                    shades[row1.serial_number] = row1.shade
                    self.true_rows[i][j-1].shade = row1.shade
                last = self.true_rows[i][j]
            shades[row2.serial_number] = 0
            self.true_rows[i][j].shade = 0

        # Assign new shading values to dict
        self.shade = shades
        return self.shade

    def evaluate_shade_west(self):
        # print "Calculating WEST Shading"
        # Use geometry to calculate shading

        # Create dict for storing shading values
        shades = {}

        # Iterate through rows from North to South, and West to East to evaluate shade
        for i in range(0, self.size[0]):
            last = None
            for j in reversed(range(0, self.size[1])):
                # Skip the first Western row
                if last is None:
                    pass
                # Calculate shade from row2 onto row1
                else:
                    # Get the inter-row distance
                    r12 = self.inter_row_dists[i][j-1]
                    # Assign rows 1 and 2
                    row1 = last
                    row2 = self.true_rows[i][j]
                    # Create the line of row1's solar panel
                    m1 = numpy.tan(numpy.radians(-row1.angle))
                    b1 = row1.h
                    # Create the line of shade originating from row2's tip at the angle of sun_alt
                    m2 = numpy.tan(numpy.deg2rad(180-self.sun_alt))
                    b2 = row2.h - row2.p/2 \
                        *numpy.sin(numpy.deg2rad(-row2.angle))-m2*(r12-row2.p \
                            /2*numpy.cos(numpy.deg2rad(-row2.angle)))
                    # Intersect the two lines in cartesian coordinates
                    x_int = (b1-b2)/(m2-m1)
                    y_int = m1*x_int + b1
                    x_end = row1.p/2 * numpy.cos(numpy.deg2rad(-row1.angle))
                    y_end = m1*x_end + b1

                    ##########################
                    #### Debug for plotting ###
                    ##########################
                    if False and row1.angle >= 0 and row2.angle >= 0:
                        plt.plot(
                            [r12-row2.p/2*np.cos(np.radians(row2.angle)),r12,r12,0,0,row1.p/2*np.cos(np.radians(row1.angle))],
                            [row2.h-row2.p/2*np.sin(np.radians(-row2.angle)),row2.h,0,0,row1.h,row1.h+row1.p/2*np.sin(np.radians(-row1.angle))]
                            )
                        plt.plot([x_int],[y_int],'ro')
                        plt.plot([0,r12],[b2,m2*r12+b2],'b-')
                        plt.plot([0,r12],[b1,m1*r12+b1],'b-')
                        plt.plot(x_end,y_end,'gx')
                        plt.grid()
                        plt.title('m1=%.2f,m2=%.2f,r1_ang=%.2f,r2_ang=%.2f' % (m1,m2,(row1.angle),(row2.angle)))
                        plt.axis('equal')
                        plt.show()
                    ##########################
                    ### end
                    ##########################

                    # Evaluate the distance from row1's panel's midpoint and check if it shades
                    # if NOT, shade = 0
                    # if YES, shading distance is the 2-norm distance to origin
                    if x_int >= row1.p/2*numpy.cos(numpy.deg2rad(-row1.angle)):
                        row1.shade = 0
                    else:
                        # 2-norm to row1's midpoint
                        shade_dist = numpy.sqrt((x_end-x_int)**2 
                            + (y_end-y_int)**2)
                        # Normalize to 1 if larger than 1
                        row1.shade = 1 if shade_dist > 1 else shade_dist
                    # add the new shading value to the shade dict
                    shades[row1.serial_number] = row1.shade
                    self.true_rows[i][j+1].shade = row1.shade
                last = self.true_rows[i][j]
            shades[row2.serial_number] = 0
            self.true_rows[i][j].shade = 0

        # Assign new shading values to dict
        self.shade = shades
        return self.shade

    def check_guess(self,guess):
        # Check the guess list vs. the actual list.

        # Create a flat-ordered list to check against
        correct = 0
        incorrect = 0
        for i in range(len(guess)):
            for j in range(len(guess[i])):
                if self.true_rows[i][j].serial_number == guess[i][j]:
                    correct += 1
                else:
                    incorrect += 1
        return correct/(correct+incorrect)


class plant_100MW(plant):
    ### 100MW version of plant, this will not be a static-random, it will be truly random every time
    ### Code works very similar to regular plant, just scaled up and with truly random values/order
    def __init__(self):
        # Make a fake site of dimensions [rows,columns]
        self.size = [70, 60]
        self.n = self.size[0] * self.size[1]
        # Initialize rows
        self.true_rows = []
        # Create a random order for all SPCs
        self.random_order = range(0,self.n)
        random.shuffle(self.random_order)
        # Initialize the serial number counter
        count = 0
        self.true_rows = []
        self.true_rows_dict = {}
        self.tracker_moves = 0
        self.tracker_move_degrees = 0
        self.plant_moves = 0
        self.plant_moves_max_degrees = 0
        # Create all of the rows in proper order and assign serial number
        for i in range(self.size[0]):
            r = []
            for j in range(self.size[1]):
                serial_number = "SPC_%04d" % (self.random_order[count]+1)
                self.true_rows_dict[serial_number] = (i,j)
                count += 1
                r.append(row(serial_number))
            self.true_rows.append(r)
        # Flatten the true_rows list and create a flat list in random order
        self.true_rows_list = numpy.array([i for sublist in self.true_rows for i in\
             sublist])[self.random_order]
        self.rows = [i.serial_number for i in self.true_rows_list]
        # Create an attribute to show the first column's order
        self.column0_order = [i.serial_number for sublist in self.true_rows for i in sublist[-1:]]
        # Randomize all heights and set random row distances
        self.randomize_heights()
        self.set_row_distances()

        # The sun altitude
        self.sun_alt = 5

        # Evaluate current plant shade
        self.evaluate_shade()

    def set_row_distances(self, value = None):
        # changes the inter-row distances of all rows to the list below
        row_dists = [random.uniform(1.95,2.05) for i in range(self.n-self.size[0])]
        self.inter_row_dists = []
        for i in range(self.size[0]):
            r = []
            if value is None:
                for j in range(self.size[1]-1):
                    r.append(row_dists.pop(0))
            else:
                r= [value]*(self.size[1]-1)
            self.inter_row_dists.append(r)


    def randomize_heights(self):
        # changes the heights of all rows to the list below
        heights = [random.uniform(1.45,1.55) for i in range(self.n)]

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self.true_rows[i][j].h = heights.pop(0)

class plant_custom(plant_100MW):
    ### 100MW version of plant, this will not be a static-random, it will be truly random every time
    ### Code works very similar to regular plant, just scaled up and with truly random values/order
    def __init__(self,x,y):
        # Make a fake site of dimensions [rows,columns]
        self.size = [x, y]
        self.n = self.size[0] * self.size[1]
        # Initialize rows
        self.true_rows = []
        # Create a random order for all SPCs
        self.random_order = range(0,self.n)
        random.shuffle(self.random_order)
        # Initialize the serial number counter
        count = 0
        self.true_rows = []
        self.true_rows_dict = {}
        self.tracker_moves = 0
        self.tracker_move_degrees = 0
        self.plant_moves = 0
        self.plant_moves_max_degrees = 0
        # Create all of the rows in proper order and assign serial number
        for i in range(self.size[0]):
            r = []
            for j in range(self.size[1]):
                serial_number = "SPC_%04d" % (self.random_order[count]+1)
                self.true_rows_dict[serial_number] = (i,j)
                count += 1
                r.append(row(serial_number))
            self.true_rows.append(r)
        # Flatten the true_rows list and create a flat list in random order
        self.true_rows_list = numpy.array([i for sublist in self.true_rows for i in\
             sublist])[self.random_order]
        self.rows = [i.serial_number for i in self.true_rows_list]
        # Create an attribute to show the first column's order
        self.column0_order = [i.serial_number for sublist in self.true_rows for i in sublist[-1:]]
        # Randomize all heights and set random row distances
        self.randomize_heights()
        self.set_row_distances()

        # The sun altitude
        self.sun_alt = 5

        # Evaluate current plant shade
        self.evaluate_shade()

if __name__ == '__main__':
    # First you need to create your plant class. We'll call ours "my_plant"
    my_plant = plant()

    # If you need to look at the "answer sheet" and figure out what your site
    # looks like right now, you can use the .true_rows attribute to show it
    print "Here is what the actual plant looks like right now"
    print(my_plant)
    print "\n\n"

    # You can then find out what SPCs are in your plant by calling the .rows
    # attribute, which is just a list of all the serial numbers in no particu-
    # lar order.
    spc_serial_numbers = my_plant.rows

    # Print it out to the console so you can see
    print "Here are your serial numbers!"
    print spc_serial_numbers
    print "\n\n"

    # Because we are unable to determine the Y-ordering of the plant, we give 
    # you the first column N-S order the East side for free
    print "First column, East side"
    print my_plant.column0_order

    # You can find out how much each row is shaded by calling the .shade
    # attirbute. It will return a dictionary with the "key" value correspond-
    # ing to the serial number, and the "value" corresponding to the amount
    # of shade on the panel in meters.
    print "Here are the current shading values"
    print my_plant.shade
    print "\n\n"



    # Now let's try to move some rows and change the shade. We'll need a 
    # dictionary for this. We first create an empty dictionary
    d = {}

    # And then iterate through all the SPC serial numbers we got earlier, and
    # assign the "key" value to the serial number, and the "value" to the
    # desired tilt angle
    for serial_number in my_plant.rows:
        d[serial_number] = -45

    # After our dictionary is made, we can use the .move_rows() command and
    # move the rows in our plant.
    my_plant.move_rows(d)


    # Every time you move the rows, the plant will automatically calculate
    # the shading on each panel. We can call .shade again to see how our
    # move affected the plant!
    print "These are the shading values after your move!"
    print my_plant
    print "\n\n"


    # Plants keep track of the moves you send to them. Every time you send a "move_rows"
    # command, the plant will consider it as a plant-wide move
    print "Plant has moved %s times" % my_plant.plant_moves

    # Plants also keep track of the plant-wide moves. It will calculate the maximum
    # travel of your plant-wide move, and use that as the value it increments by
    # This behavior is intended, as if you move all rows only 10 degrees but one
    # row 60 degrees, you're going to want to wait for the 60 degree move to finish
    # before evaluating the shading
    print "Plant has moved %.2f degrees" % my_plant.plant_moves_max_degrees

    # Plants also keep track of the number of individual moves made. Every time a 
    # tracker moves at all, it is counted
    print "%s individual rows moved" % my_plant.tracker_moves

    # Plants will also keep track of the total degrees moved in a plant.
    print "%.2f individual degrees moved" % my_plant.tracker_move_degrees

    # I've added compatibility for West shading. In our simplified model, we can just consider
    # sun coming from the west as an altitude > 90 degrees
    print "Calculating WEST shading"
    my_plant.move_sun(175)
    d = {}
    for serial_number in my_plant.rows:
        d[serial_number] = 45
    my_plant.move_rows(d)
    print my_plant
