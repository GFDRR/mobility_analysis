# Mobility data analysis in Python

mobility4resilience is a library for disaster risk management applications of smartphone location data. It provides functions for:
* loading and cleaning GPS datasets;
* extracting home and work locations;
* point of interest visit analysis;
* analysis of population displacement and recovery rates.

## Background
This library responds to the need for policy insights for preparedness and response to natural disasters, as well as the growing availability of large GPS datasets depicting human movements before, during and after such events.

## Requirements
* **Dependencies.** The library uses the scientific Python stack (numpy, Pandas, Geopandas) and relies on dask for processing large datasets.
* **Data.** Data is assumed to include `lon`, `lat`, `date` and `UserID` columns.

## Usage examples
Add some basic examples here.

## Acknowledgements

The library was developed under a grant from the Spanish Fund for Latin America and the Caribbean (SFLAC) under the Disruptive Technologies for Development (DT4D) initiative at the World Bank. Thanks to Cuebiq Inc, Purdue University and Mind Earth for their collaboration.
