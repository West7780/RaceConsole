# RaceConsole
A python program turns your slot car track into a text art based video game

## Hardware
 - Arduino Uno or similar Arduino compatable board with at least 5 Analog and 13 digital pins
 - Linux computer
 - Keyboard
 - Monitor
 - 2 to 4 Line break sensors
 - 2 to 4 Resistors
 - 10k Potentiometer
 - 16x2 Character Display, compatible with Arduino Liquid Crystal Library
 - 2 momentary push buttons (Preferably Red and Green colored)
 - 2 resistors
 - Appropriate cables to connect everything

## Setup Instructions
You will need to attach a potentiometer and two line break sensors to an 
Arduino and upload the file "RaceConsoleCompanion.ino" to it. See the file to 
get which pins you should attach these to. Optionally you can attach a 16x2
Character Display and two buttons to the Arduino.

Attach the Arduino via USB to a linux computer (Such as a raspberry pi zero w). 
Ensure that it has the latest python 3.8.1 and pip installed.

Copy the entire repository to your home folder. Call the repository with Python3.
Ex: Python3 RaceConsole

## Features
 * RCC Standalone Support for 2 or 4 lanes (RC only supports 2 lanes)
 * Terminal based Text display with dynamically generated text art

## Planned Features
 * User settings menu
 * Tournament mode (Network enabled management of multiple race tracks for large events)
 * Support for any number of lanes
 * Addressable LED control via user interface
 * Enable the use of custom controllers by replacing the Controllers with digital potentiometers
 * Engine sound emulation that responds to the user input
 * Add a player vs Computer Gamemode where an AI drives the second car
 * Online Multiplayer
 * Ability to Record and Replay races (Suggested by u/Koppis on reddit)
