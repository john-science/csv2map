# CSV-to-KML

## Purpose of this utility
This utility is not meant to be a general solution to creating KML files.  You could represent geographic data in a CSV file in many different ways.

However, over the past few years I have found this script helpful.  It is meant to take in point data, where each row in a CSV file represents one point.

## Input file formatting
The input CSV file needs two columns: lat and long. The script should be forgiving in terms of capitalization and spelling of these columns: Lat, Latitude, Lon, lon LongITUde, etcetera.

As an added bonus, this script will make use of the date/time functionality in Google Earth if there is a column labeled "datetime" in the CSV file.

