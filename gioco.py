#faccio tutti gli import per eseguire il programma
import random
import sys
import pygame
from pygame.locals import *
import serial, time
import threading, queue
import time

#THREAD MICROBIT
q = queue.Queue()

#classe del thread dove definisco il metodo run
class Read_Microbit(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._running = True
      
    def terminate(self):
        self._running = False
        
    def run(self):
        #definisco la porta con cui comunicare con il microbit
        port = "COM8"
        s = serial.Serial(port)
        s.baudrate = 115200
        while self._running:
            try:
                data = s.readline().decode()
                #faccio uno slicing del dato perché a volte viene passato con il carattere \n in fondo
                data = data[0:-2]
                q.put(data)
            except:
                print("ricevuti dati errati")
            time.sleep(0.01)

#DICHIARAZIONE VARIABILI GLOBALI
#colonna sonora con pygame
pygame.mixer.init()
sound = pygame.mixer.Sound('colonnaSonora.wav')
sound.set_volume(0.75)
sound.play()

game_images = {}
fps = 32

#impostazioni schermo
screen_width = 1600
screen_height = 960
screen = pygame.display.set_mode((screen_width,screen_height))
ground_y = screen_height*0.8

#dichiarazione variabili associate alle immagini
player = 'images/giordan.png'
background = 'images/background.png'
pipe = 'images/pipe.png'
title = 'images/title.png'

#funzione di inizio gioco
def welcomeScreen():
    player_x = int(screen_width/8)
    player_y = int((screen_height - game_images['player'].get_height())/2)
    title_x = int(screen_width *0.35)
    title_y = int(screen_height*0.04)
    base_x = 0

    #ciclo while True che si blocca solo nel caso venga premuto il pulsante "a"
    while True:
        data = q.get()          
            
        if data == "a":
            return
        else:
                #screen.blit per far comparire le immagini
                screen.blit(game_images['background'],(0,0))    
                screen.blit(game_images['player'],(player_x,player_y))
                screen.blit(game_images['base'],(base_x,ground_y))
                screen.blit(game_images['title'],(title_x,title_y))
                pygame.display.update()
                fps_clock.tick(fps)

        #con la pressioen del tasto "b" c'è l'uscita da pygame
        if data == "b":
            pygame.quit()
            sys.exit()   

#funzione di gioco principale
def mainGame():
    score = 0
    player_x = int(screen_width/8)
    player_y = int(screen_height/2)
    base_x = 0
 
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()
    #lista di dizionario per i tubi
    upperPipes = [
        {'x': screen_width+200, 'y': newPipe1[0]['y']},
        {'x': screen_width+200 + (screen_width/2), 'y': newPipe2[0]['y']}
    ]
 
    lowerPipes = [
        {'x': screen_width+200, 'y': newPipe1[1]['y']},
        {'x': screen_width+200 + (screen_width/2), 'y': newPipe2[1]['y']}
    ]
 
    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    playerAccY = 1
    playerFlapVel = -8
    playerFlapped = False
 
    #ciclo while True che permette il movimento del "giordan" nel caso ci sia la pressione del tasto "a"
    while True:
        #colonna sonora in loop
        sound.play()
        #chiamata della q.get() per chiedere in input il valore del bottone
        data = q.get()
        print(data)            
        
        #condizione di confronto tra il dato e "a", se uguale la y del personaggio si sposta
        if data == "a":
            if player_y > 0:
                playerVelY = playerFlapVel 
                playerFlapped = True

        #condizione di confronto tra il dato e "b", se uguale si esce da pygame
        if data == "b":
            pygame.quit()
            sys.exit()

        #test di collisione dove viene chiamata la funzione isCollide()
        crashTest = isCollide(player_x, player_y, upperPipes, lowerPipes)

        if crashTest:
            return
 
        playerMidPos = player_x + game_images['player'].get_width()/2

        #ciclo for per l'aumento dello score
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + game_images['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos + 4:
                score +=1
        #viene aumentata la y al player
        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False
        playerHeight = game_images['player'].get_height()
        player_y = player_y + min(playerVelY, ground_y - player_y - playerHeight)   
 
        #La zip() prende gli iterabili (possono essere zero o più), li aggrega in una tupla e la restituisce.
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x']  += pipeVelX
 
        if 0<upperPipes[0]['x']<5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])   
 
        #se le pipe sono ormai superate vengono rimosse
        if upperPipes[0]['x'] < -game_images['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)   
 
        #viene rifatto un ricarico di tutto
        screen.blit(game_images['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            screen.blit(game_images['pipe'][0], (upperPipe['x'], upperPipe['y']))
            screen.blit(game_images['pipe'][1], (lowerPipe['x'], lowerPipe['y']))
        screen.blit(game_images['base'], (base_x, ground_y))    
        screen.blit(game_images['player'], (player_x, player_y))

        #righe di codice per lo spawn dello score, che mantiene il calcolo di quanti tubi abbiamo sorpassato
 
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += game_images['numbers'][digit].get_width()
        Xoffset = (screen_width - width)/2 
 
        for digit in myDigits:
            screen.blit(game_images['numbers'][digit], (Xoffset, screen_height*0.12))
            Xoffset += game_images['numbers'][digit].get_width()
        pygame.display.update()
        fps_clock.tick(fps)

#funzione di controllo di collisione
def isCollide(player_x, player_y, upperPipes, lowerPipes):
    #condizione se si esce dallo schermo si perde
    if player_y>ground_y or player_y<0:
        return True
 
    #se collide con un tubo superiore si ferma il gioco
    for pipe in upperPipes:
        pipeHeight = game_images['pipe'][0].get_height()
        #la funzione abs() ritorna il valore assoluto
        if (player_y < pipeHeight - 100) and (abs(player_x - pipe['x']) < game_images['pipe'][0].get_width() - 15):
            return True
 
    #se collide con un tubo inferiore si ferma il gioco
    for pipe in lowerPipes:
        if (player_y + game_images['player'].get_height() > pipe['y']) and (abs(player_x - pipe['x']) < game_images['pipe'][0].get_width() - 15):
            return True
 
    return False
 
#funzione per creare in modo randomico dei tubi sullo schermo
def getRandomPipe():
    pipeHeight = game_images['pipe'][0].get_height() #stabilisco l'altezza dei tubi, prendendo quella dell'immagine   
    offset = screen_height/3 #determino lo spazio tra un tubo e l'altro
    y2 = offset + random.randrange(0, int(screen_height - game_images['base'].get_height() - 1.2*offset))
    pipeX = screen_width + 10 #determino la x in modo da farle spawnare nella parte di schermo che non si vede ancora
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},
        {'x': pipeX, 'y': y2}
    ]
    return pipe

if __name__ == "__main__":
    #inizializzo pygame
    pygame.init()

    #lancio il thread
    rm = Read_Microbit()
    rm.start()  

    #fisso un framerate di gioco specifico
    fps_clock = pygame.time.Clock() 

    #faccio il set del nome del gioco
    pygame.display.set_caption('Flappy Giordan')

    #LOAD IMMAGINI
    #uso la funzione convert_alpha per migliorare la prestazione di gioco e utilizzare solo la forma dell'immagine facendo scomparire lo sfondo inutile
    game_images['numbers'] = [
        pygame.image.load('images/zero.png').convert_alpha(),
        pygame.image.load('images/uno.png').convert_alpha(),
        pygame.image.load('images/due.png').convert_alpha(),
        pygame.image.load('images/tre.png').convert_alpha(),
        pygame.image.load('images/quattro.png').convert_alpha(),
        pygame.image.load('images/cinque.png').convert_alpha(),
        pygame.image.load('images/sei.png').convert_alpha(),
        pygame.image.load('images/sette.png').convert_alpha(),
        pygame.image.load('images/otto.png').convert_alpha(),
        pygame.image.load('images/nove.png').convert_alpha()
        ]
    
    for digit in range(len(game_images['numbers'])):
        game_images['numbers'][digit] = pygame.transform.scale(game_images['numbers'][digit], (80, 80))
    
    game_images['base'] = pygame.image.load('images/base.png').convert_alpha()
    game_images['base'] = pygame.transform.scale(game_images['base'], (1800, 200))
    #utilizzo la funzione rotate() che mi consente di ruotare il tubo di 180°
    game_images['pipe'] = [
        pygame.transform.rotate(pygame.image.load(pipe).convert_alpha(), 180),
        pygame.image.load(pipe).convert_alpha()
    ]
    game_images['background'] = pygame.image.load('images/background.png').convert_alpha()
    game_images['background'] = pygame.transform.scale(game_images['background'], (1600, 780))
    game_images['player'] = pygame.image.load('images/giordan.png').convert_alpha()
    game_images['player'] = pygame.transform.scale(game_images['player'], (80, 120))
    game_images['title'] = pygame.image.load('images/title.png').convert_alpha() 
    game_images['title'] = pygame.transform.scale(game_images['title'], (500, 100))
    
    #avvio un ciclo while true dove richiamo le seguenti funzioni
    while True:
        welcomeScreen()
        mainGame()
        data = q.get()
        
        if data == "b":
            break

    rm.terminate()
    rm.join()