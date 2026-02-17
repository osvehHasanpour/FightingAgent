import pygame
from fighter import Fighter
import random
from pygame import mixer
import os

mixer.init()
pygame.init()

sc_width= 1000
sc_height= 540

screen=pygame.display.set_mode((sc_width, sc_height))
pygame.display.set_caption("Pixel Warrior")

clock=pygame.time.Clock()
FPS=60

pygame.mixer.music.load("music/bgmusic.mp3")
pygame.mixer.music.set_volume(5)
mixer.music.play(-1)

YELLOW=(255,255,0)
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
WHITE=(255,255,255)
BLACK=(0,0,0)

intro_count=4
last_count=pygame.time.get_ticks()    
score=[0,0]
round_over=False
Round_Over_CoolDown=2000

introsound=pygame.mixer.Sound("music/321fight.mp3")


victory1=pygame.image.load("p1.png").convert_alpha()
victory2=pygame.image.load("p2.png").convert_alpha()


scroll=0
bg_images=[]
i=[3,1,2]
x=random.choice(i)
if(x==1):
    for i in range(4,0,-1):
        bg_image=pygame.image.load(f"Background/paralaxbg1/img {i}.png").convert_alpha()
        bg_images.append(bg_image)
    bg_width=bg_images[0].get_width()
elif(x==2):
    bg_images=[]
    for i in range(4,0,-1):
        bg_image=pygame.image.load(f"Background/paralaxbg2/img {i}.png").convert_alpha()
        bg_images.append(bg_image)
    bg_width=bg_images[0].get_width()
elif(x==3):
    bg_images=[]
    for i in range(7,0,-1):
        bg_image=pygame.image.load(f"Background/paralaxbg3/img {i}.png").convert_alpha()
        bg_images.append(bg_image)
    bg_width=bg_images[0].get_width()

def drawtimer(timer):
    cdimg=pygame.image.load(f"intro/{timer}.png").convert_alpha()
    screen.blit(cdimg,(0,0))

def draw_text(text, font, textcol, x, y):
    txt=font.render(text, True, textcol)
    screen.blit(txt,(x,y))

def drawbg():
    for x in range(len(bg_images)):
        speed_sc=1
        for i in bg_images:
            screen.blit(i,((x*bg_width) - scroll*speed_sc,0))
            speed_sc+=0.2
            



Mcharacter=[1,3,4,2,5]
m=random.choice(Mcharacter)

if(m==1):
    SIZE=180
    SCALE=3
    OFSET=[220,150]
    PROP1=[SIZE,SCALE,OFSET]
    Player1=pygame.image.load("Good Fighter/knight moves.png").convert_alpha()
    p1_anm_steps=[11,8,3,7,7,4,11,3]

elif(m==2):
    SIZE=180
    SCALE=3
    OFSET=[232,150]
    PROP1=[SIZE,SCALE,OFSET]
    Player1=pygame.image.load("Good Fighter/martial 1 moves.png").convert_alpha()
    p1_anm_steps=[8,8,2,6,6,4,6,2]

elif(m==3):
    SIZE=180
    SCALE=3
    OFSET=[220,150]
    PROP1=[SIZE,SCALE,OFSET]
    Player1=pygame.image.load("Good Fighter/martial 2 moves.png").convert_alpha()
    p1_anm_steps=[4,8,2,4,4,3,7,2]

elif(m==4):
    SIZE=180
    SCALE=3
    OFSET=[220,150]
    PROP1=[SIZE,SCALE,OFSET]
    Player1=pygame.image.load("Good Fighter/martial 3 moves.png").convert_alpha()
    p1_anm_steps=[10,8,3,7,9,3,11,3]

elif(m==5):
    SIZE=180
    SCALE=2
    OFSET=[120,129]
    PROP1=[SIZE,SCALE,OFSET,]
    Player1=pygame.image.load("Good Fighter/wiz 2 moves.png").convert_alpha()
    p1_anm_steps=[6,8,2,8,8,5,7,2]


Ncharacter=[5,2,4,1,3]
Ncharacter.remove(m)
n=random.choice(Ncharacter)

if(n==1):
    SIZE=180
    SCALE=3
    OFSET=[220,150]
    PROP2=[SIZE,SCALE,OFSET]
    Player2=pygame.image.load("Good Fighter/knight moves.png").convert_alpha()
    p2_anm_steps=[11,8,3,7,7,4,11,3]

elif(n==2):
    SIZE=180
    SCALE=3
    OFSET=[220,150]
    PROP2=[SIZE,SCALE,OFSET]
    Player2=pygame.image.load("Good Fighter/martial 1 moves.png").convert_alpha()
    p2_anm_steps=[8,8,2,6,6,4,6,2]

elif(n==3):
    SIZE=180
    SCALE=3
    OFSET=[220,150]
    PROP2=[SIZE,SCALE,OFSET]
    Player2=pygame.image.load("Good Fighter/martial 2 moves.png").convert_alpha()
    p2_anm_steps=[4,8,2,4,4,3,7,2]

elif(n==4):
    SIZE=180
    SCALE=3
    OFSET=[220,150]
    PROP2=[SIZE,SCALE,OFSET]
    Player2=pygame.image.load("Good Fighter/martial 3 moves.png").convert_alpha()
    p2_anm_steps=[10,8,3,7,9,3,11,3]

elif(n==5):
    SIZE=180
    SCALE=2
    OFSET=[120,129]
    PROP2=[SIZE,SCALE,OFSET]
    Player2=pygame.image.load("Good Fighter/wiz 2 moves.png").convert_alpha()
    p2_anm_steps=[6,8,2,8,8,5,7,2]


if(m==1 or m==2 or m==3 or m==4):
    p1sound=pygame.mixer.Sound("music/swordattack.wav")
    p1soundmiss=pygame.mixer.Sound("music/swordmissattack.wav")    
else:
    p1sound=pygame.mixer.Sound("music/fireattack.wav")
    p1soundmiss=pygame.mixer.Sound("music/firemissattack.wav")

if(n==1 or n==2 or n==3 or n==4):
    p2sound=pygame.mixer.Sound("music/swordattack.wav")
    p2soundmiss=pygame.mixer.Sound("music/swordmissattack.wav")
else:
    p2sound=pygame.mixer.Sound("music/fireattack.wav")
    p2soundmiss=pygame.mixer.Sound("music/firemissattack.wav")



health=pygame.image.load("health bar.png").convert_alpha()
def healthbar(health,x,y):
    ratio=health/100
    pygame.draw.rect(screen,WHITE, (x, y, 300, 30))
    pygame.draw.rect(screen, RED, (x, y, 300 * ratio, 30))

pixelfont=pygame.font.Font("VCR_OSD_MONO_1.001.ttf",30)


game_mode = "ai_vs_ai" 

agent1_info = {
    'enabled': True,
    'language': 'python', 
    'path': 'agent.py' # فقط اسم فایل بدون os.path.join
}

# agent1_info = {
#     'enabled': True,
#     'language': 'cpp',
#     'path': os.path.join(os.path.dirname(__file__), 'agent_cpp')
# }

agent2_info = {
    'enabled': True,
    'language': 'python', 
    'path': 'random-agent.py'
}

F1 = Fighter(1, 100, 290, False, PROP1, Player1, p1_anm_steps, p1sound, p1soundmiss, agent1_info)
F2 = Fighter(2, 800, 290, True, PROP2, Player2, p2_anm_steps, p2sound, p2soundmiss, agent2_info)

if game_mode == "ai_vs_ai":
    agent1_info['enabled'] = True
    agent2_info['enabled'] = True
    F1.is_ai = True
    F2.is_ai = True
elif game_mode == "player_vs_ai":
    agent2_info['enabled'] = True
    F2.is_ai = True 

font = pygame.font.Font("VCR_OSD_MONO_1.001.ttf", 20)
def draw_mode_text():
    if game_mode == "ai_vs_ai":
        mode_text = f"AI ({agent1_info['language'].upper()}) VS AI ({agent2_info['language'].upper()})"
    elif game_mode == "player_vs_ai":
        mode_text = f"PLAYER VS AI ({agent2_info['language'].upper()})"
    else:
        mode_text = "PLAYER VS PLAYER MODE"
    mode_surface = font.render(mode_text, True, WHITE)
    screen.blit(mode_surface, (sc_width//2 - mode_surface.get_width()//2, 10))

run=True

rem_frames = 3600
flag = True
while run:
    rem_frames -= 1
    if rem_frames == 0:
        if F1.health == F2.health:
            print("Draw")
        elif F1.health > F2.health:
            print("F1 wins" , F1.health , F2.health)
        else:
            print("F2 wins" , F1.health , F2.health)
        break

    clock.tick(FPS)
    drawbg()
    

    draw_mode_text()
    
    if intro_count<=0:
        if flag:
            F1.move(sc_width,sc_height,screen,F2,round_over)
            F2.move(sc_width,sc_height,screen,F1,round_over)
            flag = False
        else:
            F2.move(sc_width,sc_height,screen,F1,round_over)
            F1.move(sc_width,sc_height,screen,F2,round_over)
            flag = True

    else:
        drawtimer(intro_count)       
        if(pygame.time.get_ticks()-last_count)>=1000:
            if(intro_count==4):
                introsound.play()
            intro_count-=1
            last_count=pygame.time.get_ticks()
            print(intro_count)
    
    healthbar(F1.health,70,25)
    healthbar(F2.health,630,25)
    screen.blit(health,(0,0))
    draw_text(str(score[0]),pixelfont,WHITE,7,92)
    draw_text(str(score[1]),pixelfont,WHITE,900,92)


    key=pygame.key.get_pressed()
    if key[pygame.K_a] and scroll>0:
        scroll -=5
    elif key[pygame.K_LEFT] and scroll>0:
        scroll -=5
    if key[pygame.K_d] and scroll<300:
        scroll +=5
    elif key[pygame.K_RIGHT] and scroll<300:
        scroll +=5
    
    F1.update()
    F2.update()


    F1.draw(screen)
    F2.draw(screen)

    if round_over==False:
        if F1.alive==False:
            score[1]+=1
            print(score)
            round_over=True
            roundovertime=pygame.time.get_ticks()
        elif F2.alive==False:
            score[0]+=1            
            print(score)
            round_over=True
            roundovertime=pygame.time.get_ticks()
    else:
    
        if F1.alive==True and F2.alive==False:
            screen.blit(victory1,(0,0))
        elif F2.alive==True and F1.alive==False:
            screen.blit(victory2,(0,0))

        if pygame.time.get_ticks() - roundovertime> Round_Over_CoolDown:
            round_over=False
            intro_count=4
            F1 = Fighter(1, 100, 290, False, PROP1, Player1, p1_anm_steps, p1sound, p1soundmiss, agent1_info)
            F2 = Fighter(2, 800, 290, True, PROP2, Player2, p2_anm_steps, p2sound, p2soundmiss, agent2_info)
            
        
            if game_mode == "ai_vs_ai":
                F1.is_ai = True
                F2.is_ai = True
            elif game_mode == "player_vs_ai":
                F2.is_ai = True

    

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False


    pygame.display.update()

pygame.quit()
