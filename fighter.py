import pygame
from pygame import mixer
import pygame.gfxdraw  
import subprocess
import json
import os
import importlib.util
import platform
#do nothing here


def is_windows():
    return platform.system() == "Windows"

def is_macos():
    return platform.system() == "Darwin"

def is_linux():
    return platform.system() == "Linux"

def get_python_command():
    if is_windows():
        return 'python'
    else:  
        return 'python3'


def validate_move(move_dict):
    valid = True
    required_keys = ['move', 'attack', 'jump', 'dash' , 'debug', 'saved_data']
    
    
    for key in required_keys:
        if key not in move_dict:
            valid = False
            break
    
    
    if move_dict.get('move') not in [None, 'left', 'right']:
        valid = False
    
    
    if move_dict.get('attack') not in [None, 1, 2]:
        valid = False
    
    
    if not isinstance(move_dict.get('jump'), bool):
        valid = False
    
    
    if move_dict.get('dash') not in [None, 'left', 'right']:
        valid = False

    
    
    
    return valid

def load_agent_module(agent_path):
    if not agent_path.endswith('.py'):
        return None
        
    module_name = os.path.basename(agent_path)[:-3]  
    spec = importlib.util.spec_from_file_location(module_name, agent_path)
    if spec is None:
        return None
        
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class Fighter():
    def __init__(self,player,x,y,Flip,data,spritesheet,animationstep,sound,misssound, agent_info=None):
        self.player=player
        self.size=data[0]
        self.img_scale=data[1]
        self.ofset=data[2]
        self.flip=Flip
        self.anm_list=self.loadimage(spritesheet, animationstep)   
        
        self.action=0
        self.frame=0
        self.image=self.anm_list[self.action][self.frame]
        self.update_time=pygame.time.get_ticks()
        self.rect=pygame.Rect(x,y,120,180)
        self.vely=0
        self.running=False
        self.jump=False
        self.attacking=False
        self.attack_type=0
        self.attack_sound = sound
        self.attack_misssound = misssound
        self.attack_cooldown = [0,0]
        self.hit=False
        self.health=100
        self.alive=True
        self.is_ai = False  
        self.dashing = False  
        self.dash_cooldown = 0  
        self.dash_timer = 0  
        self.dash_dir = None
        self.saved_data = {}
        
        
        self.agent_info = agent_info
        self.agent_module = None
        if agent_info and agent_info.get('enabled', False):
            self.is_ai = True
            self.agent_language = agent_info.get('language', 'python')
            self.agent_path = agent_info.get('path', 'agent.py')
            
            
            
            

    def loadimage(self,spritesheet,animationstep):
        anm_list=[]
        for y, animate in enumerate(animationstep):
            temp_img_list=[]
            for x in range(animate):
                temp_img=spritesheet.subsurface(x*self.size,y*self.size,self.size,self.size)
                
                temp_img_list.append(pygame.transform.scale(temp_img,(self.size*self.img_scale,self.size*self.img_scale)))
            anm_list.append(temp_img_list)
        return anm_list

    def call_external_agent(self, fighter_info, opponent_info):

        try:
            
            input_data = json.dumps({
                "fighter": fighter_info,
                "opponent": opponent_info,
                "saved_data": self.saved_data
            })
            
            
            if self.agent_language == 'cpp':
                
                result = subprocess.run(
                    [self.agent_path], 
                    input=input_data.encode(), 
                    capture_output=True, 
                    timeout=0.4
                )
                resultJson = json.loads(result.stdout.decode())
                if resultJson['debug'] is not None:
                    print(resultJson['debug'])
                self.saved_data = resultJson['saved_data']
                return resultJson
            elif self.agent_language == 'python':
                
                python_cmd = get_python_command()
                result = subprocess.run(
                    [python_cmd, self.agent_path], 
                    input=input_data.encode(), 
                    capture_output=True, 
                    timeout=0.4
                )
                resultJson = json.loads(result.stdout.decode())
                if resultJson['debug'] is not None:
                    print(resultJson['debug'])
                self.saved_data = resultJson['saved_data']
                return resultJson
                
            elif self.agent_language == 'java':
                
                class_path = ""
                if is_windows():
                    class_path = '".;json.jar"' 
                else:
                    class_path = '".:json.jar"' 
                class_name = os.path.basename(self.agent_path).replace('.class', '')
                result = subprocess.run(
                    ['java', '-cp', class_path, class_name], 
                    input=input_data.encode(), 
                    capture_output=True,
                    timeout=0.4
                )
                resultJson = json.loads(result.stdout.decode())
                if resultJson['debug'] is not None:
                    print(resultJson['debug'])
                self.saved_data = resultJson['saved_data']
                return resultJson
                
            return {'move': None, 'attack': None, 'jump': False, 'dash': None , 'debug' : None , 'saved_data' : self.saved_data}
        except Exception as e:
            print(f"Error calling external agent: {e}")
            return {'move': None, 'attack': None, 'jump': False, 'dash': None , 'debug' : None , 'saved_data' : self.saved_data}

    def move(self, sc_width, sc_height, surface, target, round_over):
        SPEED = 5
        DASH_SPEED = 30  
        gravity = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        if self.dashing:
            self.dash_timer -= 1
            if self.flip:  
                if self.dash_dir == 'left':
                    self.rect.x -= DASH_SPEED
                else:
                    self.rect.x += DASH_SPEED
            else:  
                if self.dash_dir == 'right':
                    self.rect.x += DASH_SPEED
                else:
                    self.rect.x -= DASH_SPEED
            
            if self.dash_timer <= 0:
                self.dashing = False  
                self.image = self.anm_list[self.action][self.frame]  
            return  

        if self.is_ai and self.attacking == False and self.alive == True and round_over == False:
            
            fighter_info = {
                'x': self.rect.centerx,
                'y': self.rect.centery,
                'health': self.health,
                'attacking': self.attacking,
                'attack_cooldown': [self.attack_cooldown[0], self.attack_cooldown[1]],
                'jump': self.jump,
                'dash_cooldown': self.dash_cooldown
            }
            
            
            opponent_info = {
                'x': target.rect.centerx,
                'y': target.rect.centery,
                'health': target.health,
                'attacking': target.attacking
            }
            
            ai_move = None
            
            
            
            
            

            ai_move = self.call_external_agent(fighter_info, opponent_info)
            
            
            if ai_move and validate_move(ai_move):
                if ai_move['move'] == 'right':
                    dx = SPEED
                    self.running = True
                elif ai_move['move'] == 'left':
                    dx = -SPEED
                    self.running = True
                
                if ai_move['jump'] and not self.jump:
                    self.vely = -30
                    self.jump = True
                
                if ai_move['attack'] is not None:
                    self.attack_type = ai_move['attack']
                    self.attack(target)
                
                if ai_move.get('dash') == 'right' and self.dash_cooldown == 0:
                    self.dashing = True
                    self.dash_cooldown = 50
                    self.dash_timer = 10
                    self.flip = False  
                    self.dash_dir = 'right'
                elif ai_move.get('dash') == 'left' and self.dash_cooldown == 0:
                    self.dashing = True
                    self.dash_cooldown = 50
                    self.dash_timer = 10
                    self.flip = True  
                    self.dash_dir = 'left'
            else:
                print("Invalid move from AI agent:", self.player ,ai_move)
            
            
            if target.rect.centerx > self.rect.centerx:
                self.flip = False
            else:
                self.flip = True
        
        
        elif not self.is_ai:
            key=pygame.key.get_pressed()
            if self.attacking==False and self.alive==True and round_over==False:
                
                if self.player==1:
                    if key[pygame.K_d]:
                        dx=SPEED
                        self.running=True
                        
                    if key[pygame.K_a] and dx<360:
                        dx=-SPEED
                        self.running=True
                    
                    if key[pygame.K_w] and self.jump==False:
                        self.vely=-30
                        self.jump=True

                    
                    if key[pygame.K_q] or key[pygame.K_e]:
                        if key[pygame.K_q]:
                            self.attack_type=1
                        if key[pygame.K_e]:
                            self.attack_type=2
                        self.attack(target)

                    
                    if key[pygame.K_LSHIFT] and key[pygame.K_d] and self.dash_cooldown == 0:
                        self.dashing = True
                        self.dash_cooldown = 50
                        self.dash_timer = 10
                        self.flip = False  
                    elif key[pygame.K_LSHIFT] and key[pygame.K_a] and self.dash_cooldown == 0:
                        self.dashing = True
                        self.dash_cooldown = 50
                        self.dash_timer = 10
                        self.flip = True  

                if self.player==2:
                    if key[pygame.K_RIGHT]:
                        dx=SPEED
                        self.running=True
                    if key[pygame.K_LEFT] and dx<360:
                        dx=-SPEED
                        self.running=True
                    
                    if key[pygame.K_UP] and self.jump==False:
                        self.vely=-30
                        self.jump=True

                    
                    if key[pygame.K_KP1] or key[pygame.K_KP2]:
                        if key[pygame.K_KP1]:
                            self.attack_type=1
                        if key[pygame.K_KP2]:
                            self.attack_type=2
                        self.attack(target)

                    
                    if key[pygame.K_RSHIFT] and key[pygame.K_RIGHT] and self.dash_cooldown == 0:
                        self.dashing = True
                        self.dash_cooldown = 50
                        self.dash_timer = 10
                        self.flip = False  
                    elif key[pygame.K_RSHIFT] and key[pygame.K_LEFT] and self.dash_cooldown == 0:
                        self.dashing = True
                        self.dash_cooldown = 50
                        self.dash_timer = 10
                        self.flip = True  

        self.vely+=gravity
        dy+=self.vely

        if self.rect.left + dx < 0:
            dx=-self.rect.left
        if self.rect.right + dx > sc_width:
            dx= sc_width - self.rect.right
        if self.rect.bottom + dy >sc_height - 70:
            self.vely=0
            self.jump=False
            dy=sc_height - 70 - self.rect.bottom

        
        if not self.dashing:
            if not self.is_ai:
                if self.player == 1 and key[pygame.K_a]:
                    self.flip=True
                elif self.player == 2 and key[pygame.K_LEFT]:
                    self.flip=True
                
                if target.rect.centerx > self.rect.centerx:
                    self.flip=False
                else:
                    self.flip=True
        
        if self.attack_cooldown[0] > 0:
            self.attack_cooldown[0] -= 1        
        if self.attack_cooldown[1] > 0:
            self.attack_cooldown[1] -= 1

        self.rect.x += dx
        self.rect.y +=dy

    def update(self):
        
        if self.health<=0:
            self.health=0
            self.alive=False
            self.update_action(6) 
        elif self.hit==True:
            self.update_action(5)   
        elif self.attacking==True:
            if self.attack_type==1:
                self.update_action(3)
            if self.attack_type==2:
                self.update_action(4)
        elif self.dashing == True:
            self.image = None  
        elif self.jump==True:
            self.update_action(2)
        elif self.running==True:
            self.update_action(1)
        else:
            self.update_action(0)

            
        cooldown=70
        if self.image is not None:  
            self.image=self.anm_list[self.action][self.frame]
            if pygame.time.get_ticks() - self.update_time>cooldown:
                self.frame+=1
                self.update_time=pygame.time.get_ticks()
            if self.frame>=len(self.anm_list[self.action]):
                if self.alive==False:
                    self.frame=len(self.anm_list[self.action])-1
                else:
                    self.frame=0
                    self.attacking=False
                    if self.action==3:
                        self.attack_cooldown[0]=25
                    if self.action==4:
                        self.attack_cooldown[1]=100
                    if self.action==5:
                        self.hit=False
                        self.attack_cooldown[0]=25

    def attack(self,target):
        if (self.attack_cooldown[0] == 0 and self.attack_type == 1) or (self.attack_cooldown[1] == 0 and self.attack_type == 2):
            self.attacking=True
            self.attack_misssound.play()
            
            attack_range_height = self.rect.height
            attack_range_width = self.rect.width
            attack_rect=pygame.Rect(self.rect.centerx - (attack_range_width*self.flip), self.rect.y, attack_range_width, attack_range_height)
            if attack_rect.colliderect(target.rect):
                self.attack_sound.play()
                target.health-= 10 * self.attack_type
                target.hit=True

            
    
    def update_action(self,new_action):
        
        if new_action!=self.action:
            self.action=new_action
            
            self.frame=0
            self.update_time=pygame.time.get_ticks()

    def draw(self, surface):
        if self.dashing:  
            shadow_color = (100, 100, 100, 150)  
            shadow_rect = pygame.Rect(
                self.rect.x + 10,  
                self.rect.y + 10,  
                self.rect.width - 20,  
                self.rect.height - 20  
            )
            pygame.gfxdraw.filled_polygon(
                surface,
                [
                    (shadow_rect.left, shadow_rect.top),
                    (shadow_rect.right, shadow_rect.top),
                    (shadow_rect.right, shadow_rect.bottom),
                    (shadow_rect.left, shadow_rect.bottom),
                ],
                shadow_color,
            )
            pygame.gfxdraw.aapolygon(
                surface,
                [
                    (shadow_rect.left, shadow_rect.top),
                    (shadow_rect.right, shadow_rect.top),
                    (shadow_rect.right, shadow_rect.bottom),
                    (shadow_rect.left, shadow_rect.bottom),
                ],
                shadow_color,
            )
        elif self.image is not None:  
            img = pygame.transform.flip(self.image, self.flip, False)
            
            
            
            
            
            surface.blit(img, (self.rect.x - (self.ofset[0] - self.img_scale), self.rect.y - (self.ofset[1] - self.img_scale)))
