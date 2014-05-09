# CSV-to-KML

## Purpose of this utility
This utility is not meant to be a general solution to creating KML files.  Geographic data could be represented in just too many ways in a CSV file. Instead, this utility is meant to generate simple KML files of lat/lon points with an arbitrary amount of associated data.

Over the past few years, I have frequently used this utility as a quick sanity check for geographic data. It is convenient because so little formatting is needed in the input file.

This file also serves as an inroductory example of object-oriented programming in Python.

## Input file formatting
The only requirement is that the input CSV file has at least two columns: lat and long. The script is forgiving as to the spelling of these names: Lat, lat, Latitude, Lon, long, Longitude, LongITUdE, et cetera.

As a bonus, this script will make use of the date/time functionality in Google Earth if there is a column labeled "datetime".

