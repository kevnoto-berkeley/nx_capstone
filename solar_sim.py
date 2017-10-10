from __future__ import division
import pandas
import random
import numpy
import matplotlib.pyplot as plt

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
        return "<Row: %s @ %02d deg>" % (self.serial_number,self.angle)

class plant():
    def __init__(self):
        # Make a fake site of dimensions [rows,columns]
        self.size = [4,5]
        self.n = self.size[0] * self.size[1]
        # Initialize rows
        self.true_rows = []
        # Create a random order for all SPCs
        self.random_order = [6, 15, 0, 17, 19, 8, 10, 3, 16, 7, 13, 4, 9, 1, 11, 14, 12, 5, 2, 18]
        # Initialize the serial number counter
        count = 1
        # Create all of the rows in proper order and assign serial number
        for i in range(self.size[0]):
            r = []
            for j in range(self.size[1]):
                serial_number = "SPC_%02d" % count
                count += 1
                r.append(row(serial_number))
            self.true_rows.append(r)
        # Flatten the true_rows list and create a flat list in the random order
        self.rows = numpy.array([i for sublist in self.true_rows for i in sublist])[self.random_order]

        # Randomize all heights and set random row distances
        self.randomize_heights()
        self.set_row_distances()

        # The sun altitude
        self.sun_alt = 60

        # Evaluate current plant shade
        self.evaluate_shade()
        self.shade = numpy.array([i.shade for sublist in self.true_rows for i in sublist])[self.random_order]

    def set_row_distances(self):
        # changes the inter-row distances of all rows to the list below
        row_dists = [2.1994503310212945,
                 2.1924123054909237,
                 1.8161816117755416,
                 2.1923377393746035,
                 1.8625206513615749,
                 2.198134897781741,
                 1.9331977707061694,
                 1.8919942264237994,
                 2.130484914527256,
                 2.144457928821847,
                 2.113389155769876,
                 1.9527918086500224,
                 2.1237454086150116,
                 2.0368071859041588,
                 2.0476902705924065,
                 2.0477728684289342]
        self.inter_row_dists = []
        for i in range(self.size[0]):
            r = []
            for j in range(self.size[1]-1):
                r.append(row_dists.pop(0))
            self.inter_row_dists.append(r)


    def randomize_heights(self):
        # changes the heights of all rows to the list below
        heights = [1.6586108485739648,
                 1.470899241827537,
                 1.674723415789511,
                 1.6580235111869928,
                 1.3561008099657383,
                 1.3492250312176315,
                 1.6086498117358556,
                 1.6218726536245842,
                 1.5177241997076782,
                 1.4951958701141719,
                 1.5245310014528954,
                 1.568371310768304,
                 1.530625748600197,
                 1.4126487981847198,
                 1.5826075743727372,
                 1.6288214372154493,
                 1.3531280949096058,
                 1.6045129502693565,
                 1.361206179419099,
                 1.3482560751896173]

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self.true_rows[i][j].h = heights.pop(0)

    def move_rows(self,movements):
        # takes in a list of floats, movements, and casts them to the randomized order of SPCs, moving the rows
        if len(movements) != self.n:
            raise ValueError('Length of moves must be equal to number of rows, %s!' % self.n)
        else:
            for idx,row in enumerate(self.rows):
                row.angle = movements[idx]
        self.evaluate_shade()

    def move_sun(self,alt):
        # Moves the sun to alt and reevaluates shade
        self.sun_alt = alt
        self.evaluate_shade()

    def evaluate_shade(self):
        for i in range(0,self.size[0]):
            last = None
            for j in range(0,self.size[1]):
                if last is None:
                    pass
                else:
                    r12 = self.inter_row_dists[i][j-1]
                    row1 = last
                    row2 = self.true_rows[i][j]
                    m1 = numpy.tan(numpy.deg2rad(row1.angle))
                    b1 = row1.h

                    m2 = numpy.tan(numpy.deg2rad(self.sun_alt))
                    b2 = row2.h - row2.p/2*numpy.sin(numpy.deg2rad(row2.angle))-m2*(r12-row2.p/2*numpy.cos(numpy.deg2rad(row2.angle)))
                    x_int = (b1-b2)/(m2-m1)
                    y_int = m1*x_int + b1
                    x_end = row1.p/2 * numpy.cos(numpy.deg2rad(row1.angle))
                    y_end = m1*x_end + b1
                    if x_int >= row1.p/2 * numpy.cos(numpy.deg2rad(row1.angle)):
                        row1.shade = 0
                    else:
                        row1.shade = numpy.sqrt((x_end-x_int)**2 + (y_end-y_int)**2)
                        if 0:
                            plt.plot([0,row1.p/2*numpy.cos(numpy.deg2rad(row1.angle))],[row1.h,row1.h+row1.p/2*numpy.sin(numpy.deg2rad(row1.angle))],'b-')
                            plt.plot([r12,r12-row2.p/2*numpy.cos(numpy.deg2rad(row2.angle))],[row2.h,row2.h-row2.p/2*numpy.sin(numpy.deg2rad(row2.angle))],'r-')
                            plt.axis('equal')
                            x = range(0,5)
                            plt.plot(x,m2*numpy.array(x)+b2,'k--')
                            print "Intersection: %s, %s" % (x_int,y_int)
                            plt.show()
                last = self.true_rows[i][j]


        shades = []
        for i in range(0,self.size[0]):
            s = []
            for j in range(0,self.size[1]):
                s.append(self.true_rows[i][j].shade)
            shades.append(s)
        self.shade = numpy.array([i.shade for sublist in self.true_rows for i in sublist])[self.random_order]
        return self.shade


if __name__ == '__main__':
    plant = plant()
    # print plant.rows
    plant.move_sun(5)
    print plant.evaluate_shade()
    plant.move_rows([0]*20)
    # print plant.true_rows
    plant.move_sun(60)
    print plant.evaluate_shade()
