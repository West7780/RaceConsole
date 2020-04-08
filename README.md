# RaceConsole
A python program turns your slot car track into a text art based video game

## Setup Instructions
You will need to attach a potentiometer and two line break sensors to an 
Arduino and upload the file "RaceConsoleCompanion.ino" to it. See the file to 
get which pins you should attach the sensors to..

Attach the Arduino via USB to a linux computer (Such as a raspberry pi zero w). 
Ensure that it has the latest version of python 3.8 installed. If the Arduino is

Copy the entire repository to your home folder. Call the repository with Python3.

## Features
 * User configurable lap counting gamemode
 * Saves most recently used configuration
 * A simple game loop that supports requesting information from the user dynamically
 * A collection of python classes that are desgined to make future development easier
 

## Planned Features
 * A complete refractoring of the entire project
 * Addressable LED strip control via user interface
 * Enable the use of custom controllers by replacing the Controllers with digital potentiometers
 * Integrate an AI playground that uses a Genetic Algorithm to drive the slot cars
 * Engine sound emulation that responds to the user input
 * Auto finding the usb port that the Arduino is connected to
 * Auto dimming LEDs based on ambient lighting
 * User settings menu
 * Support for multiple lanes
 * Develop a through setup guide, include list of suggested sensors and wiring schematics
 * and much more...
 
 ### A note to those looking to contribute
  Once this project has been refractored and the list of planned features is shorter I will be open to community contributions. Until then if you are looking to impliment this project for use with your own slot car track I encourage you to take what I have and make it your own, think of my code as a jumping off point.
