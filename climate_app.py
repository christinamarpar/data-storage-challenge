# Now that you have completed your initial analysis, design a Flask api based on the queries that you have just developed.
# Use FLASK to create your routes.
# Hints
# You will need to join the station and measurement tables for some of the analysis queries.
# Use Flask jsonify to convert your api data into a valid json response object.

# Dependencies
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import pandas as pd
from dateutil import parser
import matplotlib.pyplot as plt

#Load engine created in database_engineering
engine = create_engine("sqlite:///hawaii.sqlite")

# Upload the Base 
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Reflect Database into ORM class ===save references
prcp = Base.classes.prcp
tobs = Base.classes.tobs
stations = Base.classes.stations

# Start a session to query the database
session = Session(engine)

#Create app
app = Flask(__name__)

first_date = '2016-08-23'

###########################################################################################
# Routes
###########################################################################################

#Home route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to my 'Home' page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start-date<br/>"
        f"/api/v1.0/start-date/end-date<br/>"
    )

# /api/v1.0/precipitation
# Query for the dates and precipitation observations from the last year.
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the json representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precip():

    print("Server received request for 'precipitation' page...")

    # Select only the date and prcp values.
    prcp_vals = session.query(prcp.date, prcp.prcp).\
    filter(prcp.date > first_date).\
    order_by(prcp.date).all()

    #Load the query results into a Pandas DataFrame and convert to a dict
    prcp_df = pd.DataFrame(prcp_vals)
    prcp_dict = dict(zip(prcp_df.date, prcp_df.prcp))

    #Convert the date column into a datetime
    return jsonify(prcp_dict)

# /api/v1.0/stations
# Return a json list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station():
    print("Server received request for 'stations' page...")

    #Query station info and convert to json
    station_vals = session.query(stations.station, 
                                stations.name, 
                                stations.latitude, 
                                stations.longitude, 
                                stations.elevation).all()
    station_df = pd.DataFrame(station_vals)
    station_dict = station_df.to_dict('records')
    return jsonify(station_dict)

# /api/v1.0/tobs
# Return a json list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def temps():
    print("Server received request for 'tobs' page...")
    
    #Query temp info and convert to json
    temp_vals = session.query(tobs.station, 
                                tobs.date, 
                                tobs.tobs).\
                filter(tobs.date > first_date).\
                all()
    temp_df = pd.DataFrame(temp_vals)
    temp_dict = temp_df.to_dict('records')
    return jsonify(temp_dict)

# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

#min_avg_max1 route
@app.route("/api/v1.0/<start>")
def min_avg_max1(start):
    print("Server received request for weather since 'start' page...")

    """Return a json list of the minimum temperature, 
    the average temperature, and the max temperature
    since the start date"""

    if(start>'2016-08-24' and start<'2017-08-18'):
        temp_vals= session.query(func.min(tobs.tobs), func.avg(tobs.tobs), func.max(tobs.tobs)).\
            filter(tobs.date >= start).all()
        min = temp_vals[0][0]
        avg = temp_vals[0][1]
        max = temp_vals[0][2]
        temp_dict = {'min':min,'avg':avg,'max':max}
        return jsonify(temp_dict)
    return "error: start date must be between 2016-08-24 and 2017-08-18, in the format yyyy-mm-dd", 404

#min_avg_max2 route
@app.route("/api/v1.0/<start>/<end>")
def calc_temps2(start, end):
    print("Server received request for weather between 'start and end' page...")

    """Return a json list of the minimum temperature, 
    the average temperature, and the max temperature
    between the start and end dates"""

    if(start>'2016-08-24' and end<'2017-08-18' and start<end):
        temp_vals= session.query(func.min(tobs.tobs), func.avg(tobs.tobs), func.max(tobs.tobs)).\
            filter(tobs.date >= start).filter(tobs.date <= end).all()
        min = temp_vals[0][0]
        avg = temp_vals[0][1]
        max = temp_vals[0][2]
        temp_dict = {'min':min,'avg':avg,'max':max}
        return jsonify(temp_dict)
    return "error: start and end dates must be between 2016-08-24 and 2017-08-18, in the format yyyy-mm-dd", 404

# Allows you to run the app through python
if __name__ == "__main__":
    app.run(debug=True)