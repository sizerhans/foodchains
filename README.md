# foodchains

This is the code for the interactive board game Foodchains. For the rules of Foodchains see here: 

This code has been tested on a Raspberry pi running Linux. 

Before testing the code, make sure you have all the dependencies installed. A folder named 'drivers' has been included as we were struggling to
get the lcd screen to work. This code was from: https://github.com/the-raspberry-pi-guy/lcd 

To use this code you'll need a:
- Raspberry pi
- 16 x 2 LCD screen
- The Foodchains cards located in OpenLab, or NFC stickers which can be rewritten to have the IDs specified in the cards dictionary
- An rfc522 RFID reader 
- 2 buttons connected to the PI's 37 and 38 input (BOARD mode)

if you wish to test the game on the Foodchains board, which can be found in Openlab 1048, already setup with relavant hardware, email w.sizer2@newcastle.ac.uk for instructions.  


Alternatively, we have provided test functions in the code so you can verify the game's functionality without the hardware. 
These test functions are located at the bottom of Game.py and are currently commented out. To use them, comment out the main() function call (line 538), skipping the need to have the relavent hardware, and remove the comments from the test functions. Make sure to run these test functions in the order they are shown in the code. This is because the functions try to simulate a game, so some of the tests are reliant on the turns that have occured in previous tests. 

If you are testing on a Windows machine, it might be necessary to comment out some of the modules imported at the top of the program. This won't affect the results of the tests, as the main() function call (line 538) should be commneted out if you simply wish to use the test functions. 

