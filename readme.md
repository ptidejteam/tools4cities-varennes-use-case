# Sample Building Model Using Metamodel for Energy Things (MetamEnTh)

This sample project creates a sample building model with dummy data. The building model
is created using an incomplete version of MetamETh and therefore does not contain all 
relevant modules. 

The code to create the building model is in the package `building_structure` which contains a `data`
directory with dummy data for experimental purposes only. The data does not represent realistic data
for the Varannes Library.

Two client programs that use depict how to use the building model are located in the `clients` directory.
They (the client programs) can be executed with the following commands from the main project directory:
`python3 clients/indoor_air_quality.py` and `python3 clients/load_profile_analysis.py`.


For any questions, reach out to *peter.yefi@mail.concordia.ca* or *peteryefi@gmail.com*