# EEE4022S_Project
Repository for EEE4022S Project titled: Development and Testing of a Simple Road Safety Tool and Algorithm for Communication Between Road Vehicles and the Network

## About this project
This project involves two parts: A graphical user interface for setting up an initialisation file for the simulation parameters, and source files containing the code for the safety algorithms to be implemented within the network simulation of traffic.  

## Setting up of initialisation parameters
In order to access the graphical user interface to set up the initialisation parameters, navigate to Code->GUI->GUI.py. Running this python file will launch the graphical user interface, which will enable the user to set the initialisation parameters. Once the setting of the parameters has been completed, clicking on "Submit" will create an initialisation file named "omnetpp.ini" and will save this file in the same folder as the python file. This file can then be moved to the workspace in which the Network Descriptor (NED) file is located for the simulation. Please also ensure that the name of the network in the NED file matches the name of the network as provided in the GUI. 

## Setting up OMNeT++, SUMO and Veins
In order to simulate traffic vehicles in the network, it is important to have a traffic simulator (SUMO), a network simulator (OMNeT++) and a mediation framework (Veins) all installed. For this project, "Instant Veins" was used, as it contains Veins, OMNeT++ and SUMO - all pre-installed into an OVA file, which can be imported into VirtualBox and loaded up. The link to download the Instant Veins OVA file is as follows: https://veins.car2x.org/download/ 

The Instant Veins OVA file loads up a 64-bit Debian Linux OS virtual machine, containing the aforementioned packages and applications. This repository can be cloned or downloaded into the virtual machine. Once this is done, the OMNeT++ simulator can be loaded by clicking **Activities->OMNeT++ icon (Top icon on the bar of icons on the left)**. This will load up the OMNeT++ interface, and from here the OMNeT++ project can be imported by navigating to the repository directory and then navigating to **Code->RondeboschTest1** and then clicking "Finish". 

Once this has been done, the project must be referenced to the "Veins" project. To do this, right click on the "RondeboschTest1" project folder in the Project Explorer tab, and click on "Properties". In the properties, click on "Project References" tab, and select the "veins" folder. This project will now be able to access the veins folder and therefore the source files located within Veins, some of which will need to be replaced for this project.

## Replacing the base Veins source files with the ones required for this project
In order to use the traffic safety code for this project, the Veins source code folders will have to be edited or replaced to ensure that the vehicles (or "nodes") in the simulation behave in the appropriate ways, transmitting messages at specified times, as well as performing the required acts upon receiving a message. To do this, copy the source files located in this repository by navigating to the repository directory, then navigating to **Code->Source Code Files->RondeboschTest1**. There will be three files, "TraCIDemo11p.h", "TraCIDemo11p.cc" and "TraCIDemo11pMessage.msg". Copy these files, and navigate to the following folder from the home folder in the virtual machine: **src->veins->src->veins->modules->application->traci**, and paste the folders into this subfolder, replacing them with the base files that currently exist within this subfolder. Within OMNeT++, it can be checked whether this was successful or not by right-clicking on the veins project folder and clicking "Build Project". 

## Running the simulation

Once the above has been completed, the simulation can be run by right-clicking the "omnetpp.ini" file in the "RondeboschTest1->simulations" subfolder and selecting "Run As->OMNET++ simulation". This will load up the Qtenv environment, click "Ok" on the initial popup message. Make sure the "veins_launchd" command is running in the background before running the simulation by clicking on **Activities->veins_launchd icon (directly below the OMNeT++ icon)**. This activates the Veins/SUMO launch configuration, allowing Veins to track vehicular information within the simulation. 

The red play button can then be clicked on the Qtenv toolbar, and after a few seconds, the simulation will commence, running until the end of simulation time (200s by default in the omnetpp.ini file).

## Obtaining results
To obtain mobility results of each node, as well as network results, a "results" folder will automatically be created in the "RondeboschTest1" project folder. Within this folder, the file with the ".vec" extension can be opened and saved as an ANF file. Clicking the ANF file, the results can be obtained by clicking on the "Browse Data" tab towards the bottom of the page. This will contain various types of results, both vector and scalar results. Right-clicking on a result and selecting "Plot" will create a line or column chart, representing these results.
