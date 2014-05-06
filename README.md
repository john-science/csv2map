# CSV-to-KML

## Purpose of this utility
This utility is not meant to be a general solution to creating KML files.  You could represent geographic data in a CSV file in many different ways. This utility is only meant to generate simple KML files of lat/lon points with an arbitrary amount of associated data.

Over the past few years, I have frequently used this little utility in day-to-day work to visualize geographic data. It is convenient because so little formatting is needed in the input file.

This file also serves as an inroductory example of object-oriented programming in Python.

## Input file formatting
The only requirement is that the input CSV file has two columns: lat and long. The script is forgiving as to the spelling of these names: Lat, Latitude, Lon, lon LongITUde, etcetera...

As an added bonus, this script will make use of the date/time functionality in Google Earth if there is a column labeled "datetime" in the CSV file.

