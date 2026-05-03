17735_group4_SEAL_PIR
Implementation of SEAL PIR for CMU course 17735 for group 4: Private Information Retrieval for Clinical Data

This cmake project serves as the SEAL PIR implementation for this project. This project largely borrows from the existing SEAL PIR and SEAL libraries in testing capabilities. The goal of the code was to simulate client and server requests to a database, recording the time it took to process a request and generate a response. The main function found in the oldSEAL.cpp file simply checks and outputs the SEAL version used by the project and prints the time results it takes to finish a single query. When built, running the oldSEAL.exe simply runs this main function.

The files present in this implementation are as follows: CMakeLists.txt: Information required to build the project, including the request to use the SEAL library (v3.6.6)

CMakePresets.json: Additional presets required for the building of the project

oldSEAL.cpp: The main function of the project, simulates a client/server conversation using SEAL and SEAL PIR functions

oldSEAL.h: header information for oldSeal.cpp

pir.cpp/hpp: PIR library functions taken from the SEAL PIR library

pir_client.cpp/hpp: PIR client functions that define what a client contains and the functions that a client uses when communicating with a server.

pir_server.cpp/hpp: PIR server functions that define what a server contains and the functions that a server uses when communicating with a client.
