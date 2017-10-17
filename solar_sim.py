from __future__ import division
import pandas
import random
import numpy
import matplotlib.pyplot as plt

###### Solar shading simulator for nx-capstone #####
# The program is broken into two halves; this first half declares functions
# to use, much like you need to make new .m files for each function in MATLAB
# The second half starts at the "if "__name__" == __main__:" line, which
# is all the code execution.

# You should write your code under the "if "__name__" == __main__:" line
# I have some examples of what you need to do to get the program to work there






class row():
    def __init__(self,sn):
        self.angle = -60.0 # Tilt angle, -East / +West
        self.shade = 0.0 # Shade distance, -From East/ +From West
        self.h = 1.5 # meters. height to rotation point from ground level
        self.p = 1.0 # meters. cord length of panel
        self.serial_number = sn

    def move_to(self,angle):
        self.angle = angle

    def __str__(self):
        return self.serial_number
    def __repr__(self):
        return "<Row: %s @ %02d deg, %.2f shaded>" % (self.serial_number,self.angle,self.shade)

class plant():
    def __init__(self):
        # Make a fake site of dimensions [rows,columns]
        self.__size = [4, 5]
        self.__n = self.__size[0] * self.__size[1]
        # Initialize rows
        self.true_rows = []
        # Create a random order for all SPCs
        self.__random_order = [6, 15, 0, 17, 19, 8, 10, 3, 16, 7, 13, 
            4, 9, 1, 11, 14, 12, 5, 2, 18]
        # Initialize the serial number counter
        count = 0
        # Create all of the rows in proper order and assign serial number
        for i in range(self.__size[0]):
            r = []
            for j in range(self.__size[1]):
                serial_number = "SPC_%02d" % (self.__random_order[count]+1)
                count += 1
                r.append(row(serial_number))
            self.true_rows.append(r)
        # Flatten the true_rows list and create a flat list in random order
        self.__rows = numpy.array([i for sublist in self.true_rows for i in\
             sublist])[self.__random_order]
        self.rows = [i.serial_number for i in self.__rows]
        # Randomize all heights and set random row distances
        self.__randomize_heights()
        self.__set_row_distances()

        # The sun altitude
        self.sun_alt = 5

        # Evaluate current plant shade
        self.evaluate_shade()

    def __repr__(self):
        s = ""
        for row in self.true_rows:
            s += str(row) + "\n"
        return s

    def __set_row_distances(self):
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
        for i in range(self.__size[0]):
            r = []
            for j in range(self.__size[1]-1):
                r.append(row_dists.pop(0))
            self.inter_row_dists.append(r)


    def __randomize_heights(self):
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

        for i in range(self.__size[0]):
            for j in range(self.__size[1]):
                self.true_rows[i][j].h = heights.pop(0)

    def move_rows(self,movements):
        # Takes in a dict of serial numbers with values that are movements
        keys = movements.keys()
        for key in keys:
            for row in self.__rows:
                if row.serial_number == key:
                    row.move_to(movements[key])
        self.evaluate_shade()
        return self.shade

    def move_sun(self,alt):
        # Moves the sun to alt and reevaluates shade
        self.sun_alt = alt
        self.evaluate_shade()
        return self.shade

    def evaluate_shade(self):
        for i in range(0, self.__size[0]):
            last = None
            for j in range(0, self.__size[1]):
                if last is None:
                    pass
                else:
                    r12 = self.inter_row_dists[i][j-1]
                    row1 = last
                    row2 = self.true_rows[i][j]
                    m1 = numpy.tan(numpy.deg2rad(row1.angle))
                    b1 = row1.h

                    m2 = numpy.tan(numpy.deg2rad(self.sun_alt))
                    b2 = row2.h - row2.p/2 \
                        *numpy.sin(numpy.deg2rad(row2.angle))-m2*(r12-row2.p \
                            /2*numpy.cos(numpy.deg2rad(row2.angle)))
                    x_int = (b1-b2)/(m2-m1)
                    y_int = m1*x_int + b1
                    x_end = row1.p/2 * numpy.cos(numpy.deg2rad(row1.angle))
                    y_end = m1*x_end + b1
                    if x_int >= row1.p/2*numpy.cos(numpy.deg2rad(row1.angle)):
                        row1.shade = 0
                    else:
                        shade_dist = numpy.sqrt((x_end-x_int)**2 
                            + (y_end-y_int)**2)
                        row1.shade = 1 if shade_dist > 1 else shade_dist
                        if 0:
                            plt.plot([0,row1.p/2
                                *numpy.cos(numpy.deg2rad(row1.angle))],
                                [row1.h,row1.h+row1.p/2
                                *numpy.sin(numpy.deg2rad(row1.angle))],'b-')
                            plt.plot([r12,r12-row2.p/2
                                *numpy.cos(numpy.deg2rad(row2.angle))],
                                [row2.h,row2.h-row2.p/2
                                *numpy.sin(numpy.deg2rad(row2.angle))],'r-')
                            plt.axis('equal')
                            x = range(0,5)
                            plt.plot(x,m2*numpy.array(x)+b2,'k--')
                            print "Intersection: %s, %s" % (x_int,y_int)
                            plt.show()
                last = self.true_rows[i][j]


        shades = []
        for i in range(0, self.__size[0]):
            s = []
            for j in range(0, self.__size[1]):
                s.append(self.true_rows[i][j].shade)
            shades.append(s)
        shades = numpy.array([i.shade for sublist in self.true_rows for i \
            in sublist])[self.__random_order]

        d = {}
        for idx,row in enumerate(self.__rows):
            d[row.serial_number] = shades[idx]
        self.shade = d
        return self.shade

    def check_guess(self,guess):
        actual = [[j.serial_number for j in i] for i in self.true_rows]
        return numpy.array(actual)== guess


if __name__ == '__main__':
    # First you need to create your plant class. We'll call ours "my_plant"
    my_plant = plant()


    # You can then find out what SPCs are in your plant by calling the .rows
    # attribute, which is just a list of all the serial numbers in no particu-
    # lar order.
    spc_serial_numbers = my_plant.rows
    # Print it out to the console so you can see
    print "Here are your serial numbers!"
    print spc_serial_numbers
    print "\n\n"

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
    for serial_number in spc_serial_numbers:
        d[serial_number] = 0
    # After our dictionary is made, we can use the .move_rows() command and
    # move the rows in our plant.
    my_plant.move_rows(d)


    # Every time you move the rows, the plant will automatically calculate
    # the shading on each panel. We can call .shade again to see how our
    # move affected the plant!
    print "These are the shading values after your move!"
    print my_plant.shade
