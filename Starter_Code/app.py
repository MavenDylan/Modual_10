# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, abort
from datetime import datetime, timedelta
#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(autoload_with=engine)
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d")
one_year_ago = most_recent_date - timedelta(days=365)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Welcome to the homepage. These are all the avaliable routes you can take!"""
    return (
        f"Available Routes:"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def first():
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    most_recent_date = datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - timedelta(days=365)
    query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()


    dict = []
    for measurement.date, measurement.prcp in query:
        passenger_dict = {}
        passenger_dict["date"] = measurement.date
        passenger_dict["prcp"] = measurement.prcp
        
        dict.append(passenger_dict)

    return jsonify(dict)

@app.route("/api/v1.0/stations")
def stations():
    active_stations = session.query(measurement.station, func.count().label("count")).group_by(measurement.station).order_by(func.count().desc()).all()

    station_list = []
    for station, count in active_stations:
        station_list.append({"station": station, "count": count})

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station_id = "USC00519281"
    last_12_months_data = session.query(measurement.tobs).filter(
    measurement.station == most_active_station_id,
    measurement.date >= one_year_ago,
    measurement.date <= most_recent_date
).all()
    return jsonify(last_12_months_data)

@app.route('/api/v1.0/<start>', methods=['GET'])
def get_temperature_start(start):
    
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Use YYYY-MM-DD.")

    session = Session()
    

    temperature_stats = session.query(
        func.min(measurement.tobs).label("min_temp"),
        func.max(measurement.tobs).label("max_temp"),
        func.avg(measurement.tobs).label("avg_temp")
    ).filter(measurement.date >= start_date).one_or_none()
    if temperature_stats is None:
        abort(404, description="No data found for the specified start date.")

    return jsonify({
        'start_date': start,
        'min_temp': temperature_stats.min_temp,
        'max_temp': temperature_stats.max_temp,
        'avg_temp': temperature_stats.avg_temp
    })

@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def get_temperature_range(start, end):
    
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Use YYYY-MM-DD.")

    session = Session()
    

    temperature_stats = session.query(
        func.min(measurement.tobs).label("min_temp"),
        func.max(measurement.tobs).label("max_temp"),
        func.avg(measurement.tobs).label("avg_temp")
    ).filter(measurement.date >= start_date, measurement.date <= end_date).one_or_none()


    if temperature_stats is None:
        abort(404, description="No data found for the specified date range.")

    return jsonify({
        'start_date': start,
        'end_date': end,
        'min_temp': temperature_stats.min_temp,
        'max_temp': temperature_stats.max_temp,
        'avg_temp': temperature_stats.avg_temp
    })