import RPi.GPIO as GPIO
import sys
sys.path.insert(0, './drivers') #code used for writing to lcd display, not my own
from time import sleep
from mfrc522 import SimpleMFRC522
import drivers 

display = drivers.Lcd()
reader = SimpleMFRC522()

#Dictionary for card values, used to save time writing all the values to NFC stickers
cards = {
    'Red Fox': [584183583123, 9, 'native', 'predator'],
    'Little Owl': [584190199800, 8, 'native', 'predator'],
    'Grass Snake': [584199175817, 7, 'native', 'predator'],
    'Seven-spot Ladybird': [584188168159, 1, 'native', 'plant'],
    'Meadow Grasshopper': [584198321812, 2, 'native', 'plant'],
    'Oxeye Daisy': [584183643772, 1, 'native', 'plant'],
    'Stag Beetle': [584194389451, 3, 'native', 'plant'],
    'Primrose': [584188493611, 1, 'native', 'plant'],
    'Bumblebee': [584192165658, 2, 'native', 'plant'],
    'Peacock Butterfly': [584194000678, 1, 'native', 'plant'],
    'Lily in the Valley': [584186527561, 3, 'native', 'plant'],
    'Mountain Hare': [584182860166, 6, 'native', 'prey'],
    'Mute Swan': [584183445360, 6, 'native', 'prey'],
    'Robin': [584198321559, 4, 'native', 'prey'],
    'Common Frog': [584198454657, 4, 'native', 'prey'],
    'European Hedgehog': [584184495976, 5, 'native', 'prey'],
    'Red Squirrel': [584196421032, 5, 'native', 'prey'],
    'Asian Hornet': [3584195898808, 4, 'invasive', 'plant'],
    'Japanese Knotweed': [584195770444, 2, 'invasive', 'plant'],
    'Oak Processionary Moth': [584197736546, 1, 'invasive', 'plant'],
    'Grey Squirrel': [584193804334, 5, 'invasive', 'prey'],
    'American Bullfrog': [584197143981, 4, 'invasive', 'prey'],
    'Raccoon': [584185083743, 9, 'invasive', 'predator'],
    'Drought': [584185680307, 0, 'weather'],
    'Flood': [584187711952, 0, 'weather'],
    'Meteoroid': [584196224692, 0, 'weather']
}



#the turn buttons
player1Button = 31
player2Button = 32
resetButton = 12
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(player1Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(player2Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#reset button not currently on the board
#GPIO.setup(resetButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Keeps track of game state
notStarted = True
currentTurn = 0
cardsPlayedOnTurn = 0
player1HasPassed = False
player2HasPassed = False


# Board states
player1PlantTrack = set()
player1PreyTrack = set()
player1PredatorTrack = set()

player2PlantTrack = set()
player2PreyTrack = set()
player2PredatorTrack = set()

cardsChainedPlayer1 = set()
cardsChainedPlayer2 = set()

cardsInPlayer1 = set()
cardsInPlayer2 = set()

#scores
player1Score = 0
player2Score = 0

player1Lives = 2
player2Lives = 2


def main():
    
    while notStarted:
        #Begins the game
        setUp()
        sleep(2)

    global cardsPlayedOnTurn
    try:
        while True:
            #writes score of game and current turn to game display 
            writeToScreen("Turn: " + str(currentTurn), "P1:" + str(player1Score) + " P2:" + str(player2Score))
            #Listen for cards until current player hits their input
            id = reader.read_id()
            #Goes through the cards list and handles the card played
            for card in enumerate(cards.items()):
                #checks if id of card matches a card in the dictionary
                if card[1][1][0] == id:
                    cardPlayed = card[1]
                    type = card[1][1][2]
                    #if a player has played a card, they have not passed their go
                    cardsPlayedOnTurn += 1
                    if type == "native":
                        print(cardPlayed)
                        handleNativeCard(cardPlayed)
                    elif type == "weather":
                        handleWeatherCard(cardPlayed)
                        print(cardPlayed)
                    elif type == "invasive":
                        handleInvasiveCard(cardPlayed)
                        print(cardPlayed)
                    else:
                        #handling invalid card types
                        print(cardPlayed)
                        print(" is an invalid card")

    except KeyboardInterrupt:
        GPIO.cleanup()
        display.lcd_clear()

#runs when game starts
def setUp():
    writeToScreen("Foodchains!", "P1 Go First")
    global notStarted
    notStarted = False
    global currentTurn
    #determines who goes first
    currentTurn = 1

#runs when either of the turn buttons are pressed
def button_pressed(channel):
    global currentTurn
    global cardsPlayedOnTurn
    nextTurn = 0

    global player1HasPassed
    global player2HasPassed

    if notStarted == False:
        #handle correct button has been pressed
        if currentTurn == 1:
            if channel != player1Button:
                return()
            nextTurn = 2
        elif currentTurn == 2:
            if channel != player2Button:
                return()
            nextTurn = 1
        #turn changes
        currentTurn = nextTurn
        #updates lcd with new current turn
        writeToScreen("Turn: " + str(currentTurn), "P1:" + str(player1Score) + " P2:" + str(player2Score) )
        #check if the player has passed
        if cardsPlayedOnTurn == 0 and currentTurn == 1:
            player1HasPassed = True
        elif cardsPlayedOnTurn == 0 and currentTurn == 2:
            player2HasPassed = True
        #checks if both players have passed, trigger a new round
        if player1HasPassed == True and player2HasPassed == True:
            nextRound()
        #resets the cards played counter for the new turn
        cardsPlayedOnTurn =0

#used to write to the lcd screen
def writeToScreen(message1, message2):
    display.lcd_clear()
    display.lcd_display_string(message1, 1)
    display.lcd_display_string(message2, 2)

#called when a weather card is played
def handleWeatherCard(card):
    currentTrack = set()
    effectedPlantTrack = set()
    effectedPreyTrack = set()
    effectedPlantTrack = set()
    scoreToDecrease = 0
    global player1Score
    global player2Score

    #weather cards are played on the opponent's track
    if currentTurn == 1:
        #get appropriate player tracks
        effectedPlantTrack = player2PlantTrack 
        effectedPreyTrack = player2PreyTrack
        effectedPredatorTrack = player2PredatorTrack
        scoreToDecrease = player2Score
    elif currentTurn == 2:
        #get appropriate player tracks
        effectedPlantTrack = player1PlantTrack
        effectedPreyTrack = player1PreyTrack
        effectedPredatorTrack = player1PredatorTrack
        scoreToDecrease = player1Score
    else: print("issue with turn management")

    nameOfCard = card[0]

    #gives the correct track that the card will effect
    if nameOfCard == "Flood":
        currentTrack = effectedPreyTrack
    elif nameOfCard == "Drought":
        currentTrack = effectedPlantTrack
    elif nameOfCard == "Meteoroid":
        currentTrack = effectedPredatorTrack
    else: currentTrack = []
 
    cardsToRemoveFromTrack = []
    #checks for any cards in the effected track and removes them from the score
    for cardID in currentTrack:
        for card in enumerate(cards.items()):
            if card[1][1][0] == cardID:
                scoreToDecrease = scoreToDecrease - card[1][1][1]
                cardsToRemoveFromTrack.append(cardID)

    #removes effected cards from the track
    for card in cardsToRemoveFromTrack:
        currentTrack.remove(card)

    #updates scores
    if currentTurn == 1:
        player2Score = scoreToDecrease 
    elif currentTurn == 2:
        player1Score = scoreToDecrease 

#called when invasive cards are played
def handleInvasiveCard(card):
    global player1Score
    global player2Score
    #invasive cards are played onto the opponent's track
    scoreToChange = 0 
    if currentTurn == 1:
        scoreToChange = player2Score
    elif currentTurn == 2:
        scoreToChange = player1Score
    scoreToChange -= card[1][1]
    #decreases score by the power of the card
    if currentTurn == 2:
        player1Score = scoreToChange 
    elif currentTurn == 1:
        player2Score = scoreToChange
    else: print("turn management has gone wrong")

def handleNativeCard(card):

    global player1Score
    global player2Score
    cardsInPlay = set()
    cardsChained = set()
    cardTrack = set()

    cardTrackPrey = set()
    cardTrackPredator = set()
    cardTrackPlant = set()

    if currentTurn == 1:
        #updates the score of current player
        player1Score += card[1][1]
        #gets the appropriate data
        cardsChained = cardsChainedPlayer1       
        if card[1][3] == "predator":
            cardTrack = player1PredatorTrack
        elif card[1][3] == "prey":
            cardTrack = player1PreyTrack
        elif card[1][3] == "plant":
            cardTrack = player1PlantTrack
        else: print("invalid track")
        #used to check if a chain has been formed later
        cardTrackPrey = player1PreyTrack
        cardTrackPredator = player1PredatorTrack
        cardTrackPlant = player1PlantTrack
        cardsInPlay = cardsInPlayer1
    elif currentTurn == 2:
        #updates the score of current player
        player2Score += card[1][1]
        #gets the appropriate data
        cardsChained = cardsChainedPlayer2
        if card[1][3] == "predator":
            cardTrack = player2PredatorTrack
        elif card[1][3] == "prey":
            cardTrack = player2PreyTrack
        elif card[1][3] == "plant":
            cardTrack = player2PlantTrack
        else: print("invalid track")
        #used to check if a chain has been formed later
        cardTrackPrey = player2PreyTrack
        cardTrackPredator = player2PredatorTrack
        cardTrackPlant = player2PlantTrack
        cardsInPlay = cardsInPlayer2
    else: print("invalid player state")

    length = len(cardsInPlay)
    cardTrack.add(card[1][0])
    cardsInPlay.add(card[1][0])
    #Checks if card has already been played, which would only happen in case of chain
    if checkForChain(cardsInPlay, length):
        cardsChained.add(card[1][0])
        #Checks if chain has been formed
        if len(cardsChained) % 3 == 0 and len(cardsChained) > 2:
            cardToRemovePredator = ""
            cardToRemovePrey = ""
            cardToRemovePlant = ""
            #check every track and then remove it, so it can't be effected by weather cards
            for card in cardsChained:
                for preyCard in cardTrackPrey:
                    if preyCard == card:
                        cardToRemovePrey = preyCard
                for predatorCard in cardTrackPredator:
                    if predatorCard == card:
                        cardToRemovePredator = predatorCard

                for plantCard in cardTrackPlant:
                    if plantCard == card:
                        cardToRemovePlant = plantCard


            #removes cards from the track when chained so they are not affected by weather
            if(cardToRemovePrey != ""):
                    cardTrackPrey.remove(cardToRemovePrey)
            if(cardToRemovePredator != ""):
                    cardTrackPredator.remove(cardToRemovePredator)
            if(cardToRemovePlant != ""):
                    cardTrackPlant.remove(cardToRemovePlant)

            

#Checks if any card has been played previously, which would only happen in case of chain
def checkForChain(cardsToCheck,length):
    if length == len(cardsToCheck):
        return True
    else:
        return False


def nextRound():
    #resets scores
    global player1Score
    global player2Score
    global player1HasPassed
    global player2HasPassed

    

    global player1PreyTrack
    global player1PlantTrack
    global player1PredatorTrack
    global cardsChainedPlayer1

    global player2PreyTrack
    global player2PlantTrack
    global player2PredatorTrack
    global cardsChainedPlayer2

    #empties data structures for next round
    player1PreyTrack.clear()
    player1PlantTrack.clear()
    player1PredatorTrack.clear()
    cardsChainedPlayer1.clear()

    player2PreyTrack.clear()
    player2PlantTrack.clear()
    player2PredatorTrack.clear()
    cardsChainedPlayer2.clear()


    global player1Lives
    global player2Lives

    player1HasPassed = False
    player2HasPassed = False

    #determiens who wins rounds/game
    if player1Score > player2Score:
        writeToScreen("P1 Wins Round", "Next Round...")
        sleep(3)
        player2Lives -= 1
        if player2Lives == 0:
            gameWon("player1")
    elif player2Score > player1Score:
        writeToScreen("P2 Wins Round", "Next Round...")
        sleep(3)
        player1Lives -= 1
        if player1Lives == 0:
            gameWon("player2")
    elif player2Score == player1Score:
        writeToScreen("Round Draw", "Next Round...")
        sleep(3)
        player1Lives -=1
        player2Lives -=1
        if player1Lives == 0 and player2Lives == 0:
            gameWon("draw")
        elif player1Lives == 0:
            gameWon("player2")
        elif player2Lives == 0:
            gameWon("player1")
    #resets score for next round
    player1Score = 0
    player2Score = 0
    #resets lcd screen
    writeToScreen("Turn: " + str(currentTurn), "P1:" + str(player1Score) + " P2:" + str(player2Score))
            

def gameWon(player):
    if player == "player1":
        writeToScreen("Congratulations", "Player 1 Has Won" )
        sleep(10)
        reset_game(12)
        
    elif player == "player2":
        writeToScreen("Congratulations", "Player 2 Has Won" )
        sleep(10)
        reset_game(12)
        
    elif player == "draw":
        writeToScreen("Congratulations", "You have Tied" )
        sleep(10)
        reset_game(12)
        
#used to reset game, was linked to a button, but this was not put on the board. Currently used for testing
def reset_game():
    global player1Score
    global player2Score
    global player1HasPassed
    global player2HasPassed
    global notStarted
    

    global player1PreyTrack
    global player1PlantTrack
    global player1PredatorTrack
    global cardsChainedPlayer1

    global player2PreyTrack
    global player2PlantTrack
    global player2PredatorTrack
    global cardsChainedPlayer2

    player1PreyTrack.clear()
    player1PlantTrack.clear()
    player1PredatorTrack.clear()
    cardsChainedPlayer1.clear()

    player2PreyTrack.clear()
    player2PlantTrack.clear()
    player2PredatorTrack.clear()
    cardsChainedPlayer2.clear()

    player1Score = 0
    player2Score = 0
    notStarted = True

#triggers button pressed function when player 1 turn button pressed
GPIO.add_event_detect(player1Button,  GPIO.FALLING, callback=button_pressed, bouncetime=1000)
#triggers button pressed function when player 2 turn button pressed
GPIO.add_event_detect(player2Button, GPIO.FALLING, callback=button_pressed, bouncetime=1000)
#reset button not on the board
#GPIO.add_event_detect(resetButton, GPIO.FALLING, callback=reset_game, bouncetime=1000) 


#tests cards are added to the correct score and the correct game track
def testAddCardToScore():
    global currentTurn
    currentTurn = 1
    #mimicks the way cards are read on the reader
    for card in enumerate(cards.items()):
        #gets the first card in the dictionary
        if card[1][0] == 'Red Fox':
            cardToTest = card[1]
    handleNativeCard(cardToTest)

    #checks the red fox has been added to the score, if not it will throw an assertion error
    assert player1Score == 9, "Incorrect Score"
    #checks the red fox has been added to the predator track
    assert len(player1PredatorTrack) == 1, "Failed to add to track"

#Tests if weather cards remove cards from the correct track and updates scores
def testingWeatherCards():
    #weather cards affect the other player, so we will remove the fox played in the test above 
    global currentTurn
    currentTurn = 2
    assert len(player1PredatorTrack) > 0, "No cards in play"
    for card in enumerate(cards.items()):
        if card[1][0] == "Meteoroid":
            weatherCard = card[1]
    #the meterioid card will remove the fox from player 1's predator track
    handleWeatherCard(weatherCard)

    #checks if the fox has been removed, making the track empty
    assert len(player1PredatorTrack) == 0, "Card has not been remove"
    #checks if the fox's score has been removed
    assert player1Score == 0, "Score has not been updated"

#Tests if chains are formed when the same 3 cards are played onto the board
def testingChains():
    global currentTurn
    for card in enumerate(cards.items()):
        if card[1][0] == "Red Fox":
            predCard = card[1]
        elif card[1][0] == 'Meadow Grasshopper':
            plantCard = card[1]
        elif card[1][0] == "Mountain Hare":
            preyCard = card[1]
        elif card[1][0] == "Flood":
            cardToTestChain = card[1]
    handleNativeCard(predCard)
    handleNativeCard(plantCard)
    handleNativeCard(preyCard)
    handleNativeCard(predCard)
    handleNativeCard(plantCard)
    #when this card is played, chain is formed
    handleNativeCard(preyCard)

    #Chained cards should all be in this set
    assert len(cardsChainedPlayer2) == 3, "Chain has not been formed"
    #Chained cards are removed from the tracks of the board
    assert len(player2PlantTrack) == 0 and len(player2PreyTrack) == 0 and len(player2PredatorTrack) == 0, "Cards have not been removed from tracks, therefore are vulnerable to weather cards"

    currentTurn = 1
    #tests if chain is protected from weather cards
    handleWeatherCard(cardToTestChain)
    assert player2Score == 34


#Tests if invasive cards reduce the score of the other player
def testingInvasiveCards():
    print(currentTurn)
    for card in enumerate(cards.items()):
        if card[1][0] == "Grey Squirrel":
            invasiveCard = card[1]
    handleInvasiveCard(invasiveCard)
    #the squirrel has a power of 5, and player 1 has played the card
    # so it should reduce the score from 34 (as a result of the test above) to 29
    assert player2Score == 29



main()

#Testing functions. use independently of game e.g. to run comment out calling main function and remove
#the comments from the test functions. Run functions in the order specified below, as they mimick a 
# game being played i.e the game state changes which the following function will verify.  

#testAddCardToScore()
#testingWeatherCards()
#testingChains()
#testingInvasiveCards()