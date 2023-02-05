# ================================================================================================================= #
# This program retreive glycemic datas from MongoDB DataBase
# ================================================================================================================= #

from pymongo import MongoClient
from datetime import datetime, date, timedelta
import sqlite3
from DataBase_class import DataBase_class
import matplotlib.pyplot as plt
from matplotlib import dates

###
# This function returns a dictionnary whose the key are the moment when the glycemic data has been sent.
# While the value is the glycemia at this moment.
###
def GlycTimeSerieFromMongoDB():
    # connection to my account of MongoDB service 
    cluster = MongoClient("mongodb+srv://nightscout:<password>@cluster0.hpdzk88.mongodb.net/?retryWrites=true&w=majority")

    # selection of the dataBase
    mydb = cluster["BaseDonneesDiabete"]

    # selection of the collection 
    mycol = mydb["entries"]

    # returns the first element of the collection ( the most ancient )
    # first_written_glycemia = mycol.find_one()

    # retreive all element 
    glycemia_dict = dict()
    for message in mycol.find():

        # get the date in string 
        dateString = message.get('dateString')
        utcoffset = timedelta(minutes = message.get('utcOffset'))

        # conversion of the date in actuel python date type
        date_datetime = datetime.strptime(dateString, '%Y-%m-%dT%H:%M:%S.%fZ')
        date_datetime = date_datetime + utcoffset

        # get the glycemia in int
        glycemia = message.get('sgv')

        glycemia_dict[date_datetime] = glycemia

    
    return glycemia_dict



def DisplayDailyGraph(glycemia_dict):

    fig, ax = plt.subplots()
    t = [key for key in glycemia_dict ]
    g = [value for (key,value) in glycemia_dict.items()]
    ax.plot_date(t,g,'-' ,xdate=True)
    ax.set_xlabel("time")
    ax.set_ylabel("glycemia (mg/dl) ")
    ax.set_title(f'Glycemia of {t[0].date().isoformat()}')
    plt.show(block = True)






def main():

    diabete_DB = DataBase_class()

    # retrieve all the glycemia from the MongoDB
    glycemia_dict = GlycTimeSerieFromMongoDB()

    # Fill the days table of the SQLite db with the new days for which we have records
    diabete_DB.UpdateDaysTable(glycemia_dict)

    # Fill the glycemia table of the SQLite db with the new glycemic records
    diabete_DB.UpdateGlycemiaTable(glycemia_dict)

    selected_day = date(2023,2,2)
    glycemia_dict = diabete_DB.GetDayRecords(selected_day)

    DisplayDailyGraph(glycemia_dict)

    

if __name__ == '__main__':
    main()
    