# CSV-to-KML

## Purpose of this utility
This utility is not meant to be a general solution to creating KML files. Instead, it is a simple tool to create a bunch of point locations in Google Earth.

This tool has grown out of the need to occasionally look at geographic point data. There are obviously many ways to do that, but I found this script to be the fastest.

To the student, this file will also serve as an inroductory example of object-oriented programming in Python.

## Input file formatting
The only thing absolutely required by this script is that the input CSV file has at least two columns: lat and long. The script is forgiving as to the spelling of these names: Lat, lat, Latitude, Lon, long, Longitude, LongITUdE, et cetera.

As a bonus, this script will make use of the time slider in Google Earth if there is a column labeled "datetime".

