import pandas
import numpy
from os.path import join
from os import listdir

def calc_losses():
    mydir = r"C:\Users\kevno\Documents\nx_capstone"
    solar = pandas.read_csv(join(mydir,r"126544_37.85_-122.26_tmy.csv"),header=0,skiprows=2)
    winter_months = [12]+range(1,2)
    spring_months = range(2,6)
    summer_months = range(6,9)
    autumn_months = range(9,12)
    season_months = [winter_months,spring_months,summer_months,autumn_months]
    seasons = ['winter','spring','summer','autumn']
    df = pandas.DataFrame()
    for idx,season in enumerate(seasons):
        sl = solar[solar['Month'].isin(season_months[idx])]
        d = {
            'Season':[season]*24,
            'Hour':[],
            'DHI':[],
            'DNI':[],
            'GHI':[]
        }
        for hour in sl['Hour'].unique():
            sl3 = sl[sl['Hour'] == hour]
            d['Hour'].append(hour)
            for i in ['DHI','DNI','GHI']:
                d[i].append(sl3[i].mean())
        tdf = pandas.DataFrame(d)
        df = df.append(tdf,ignore_index=True)
    df.to_csv('seasonal_irr.csv',index=False)
if __name__ == '__main__':
    calc_losses()