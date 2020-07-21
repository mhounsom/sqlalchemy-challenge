import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>(enter as yyyy-mm-dd) <br/>"
        f"/api/v1.0/<start><end>(enter as yyyy-mm-dd/yyyy-mm-dd) <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """precipitation query results from past year"""
    
    #from original query, we know that the last date in database is 2017-08-23

    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    data_and_precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()

    precip_norm = list(np.ravel(data_and_precip))


    return jsonify(precip_norm)


@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """list of stations"""
    
    stations = session.query(Station.station).all()

    session.close()

    station_norm = list(np.ravel(stations))

    return jsonify(station_norm)


@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """temperature observations of the most active station in the past year"""

    top_active_stations = session.query(Measurement.station, func.count(Measurement.date)).group_by(Measurement.station).order_by(func.count(Measurement.date).desc()).all()

    top_place = (top_active_stations[0])
    top_place = (top_place[0])

    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    most_temp_obvs = session.query(Measurement.tobs).filter(Measurement.station == top_place).filter(Measurement.date >= one_year_ago).all()

    session.close()

    tobs_norm = list(np.ravel(most_temp_obvs))

    return jsonify(tobs_norm)


@app.route("/api/v1.0/<start>")
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """TMIN, TAVG, TMAX for start Date Only"""

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    session.close()

    start_date_list = []
    for result in results:
        start_only = {}
        start_only["TMIN"] = result[0]
        start_only["TAVG"] = result[1]
        start_only["TMAX"] = result[2]
        start_date_list.append(start_only)

    return jsonify(start_date_list)


@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """TMIN, TAVG, TMAX"""

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    start_end_list = []
    for result in results:
        start_end = {}
        start_end["TMIN"] = result[0]
        start_end["TAVG"] = result[1]
        start_end["TMAX"] = result[2]
        start_end_list.append(start_end)

    return jsonify(start_end_list)


if __name__ == '__main__':
    app.run(debug=True)