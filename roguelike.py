#!/usr/bin/python
#
# libtcod python tutorial
#

import libtcodpy as libtcod
import math
import textwrap
import shelve
import random
import itertools
from collections import OrderedDict
import copy
import time
import sys
import os
from datetime import date,datetime


#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 43

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
CHARACTER_SCREEN_WIDTH = 30
LEVEL_SCREEN_WIDTH = 40

#spell values
HEAL_AMOUNT = 40
LIGHTNING_DAMAGE = 40
LIGHTNING_RANGE = 5
CONFUSE_RANGE = 8
CONFUSE_NUM_TURNS = 10
FIREBALL_RADIUS = 3
FIREBALL_DAMAGE = 25

FULL_STOMACK=2000
FOOD_CALORIES=1300

LIMIT_FPS = 20  #20 frames-per-second maximum

AMULET_LEVEL = 26
#AMULET_LEVEL = 2#test

def hsv(h,s,v):
    c = libtcod.Color()
    libtcod.color_set_hsv(c,h,s,v)
    return c

color_dark_wall = hsv(240,0.8,0.7)
color_dark_ground = hsv(240,0.8,0.5)
color_light_wall = hsv(0,0,0.7)
color_light_ground = hsv(0,0,0.25)

color_monster = hsv(160,1,1)
color_gold = hsv(45,0.5,1)
color_food = hsv(0,0,1)
color_potion = hsv(190,1,1)
color_armor = hsv(30,1,1)
color_weapon = hsv(180,1,1)
color_scroll = hsv(315,0.5,1)
color_ring = hsv(60,0.5,1)
color_stick = hsv(30,1,1)
color_trap = hsv(0,0,1)
color_amulet = hsv(0,0,1)

def get_user_name():
    for v in ('username','user','USERNAME','USER'):
        name = os.getenv(v)
        if name:
            return name
    return 'Anonimous'

def rest_in_peace():
    msgbox(
'       ____________\n'+
'      /            \\\n'+
'     /    REST      \\\n'+
'    /      IN        \\\n'+
'   /      PEACE       \\\n'+
'  /                    \\\n'+
'  |'+user_name.center(20)+'|\n'+
'  |                    |\n'+
'  |                    |\n'+
'  |    killed by a     |\n'+
'  |'+killer_monster_name.center(20)+'|\n'+
'  |'+end_date.strftime('%Y-%m-%d').center(20)+'|\n'+
'  |   *      *      *  |\n'+
'__WWVWWW__V____WW_VV_WW__\n'+
'                         \n'+
'--Press ESC to continue--\n'
,25)
    clear_menu()
    show_score()

def price(obj):
    if obj.type == 'food':
        return 2
    if obj.type == 'weapon':
        return weapon_dict[obj.name].gold * (1 + 10*(obj.equipment.hit_plus+obj.equipment.dmg_plus))
    if obj.type == 'armor':
        return armor_dict[obj.name].gold * (1 + 10*(armor_dict[obj.name].ac - obj.equipment.ac))
    if obj.type == 'ring':
        worth = ring_dict[obj.name].gold
        if obj.name == 'protection':
            worth += obj.equipment.ac > 0 and obj.equipment.ac * 20 or 50
        if obj.name=='add strength':
            worth += obj.equipment.st > 0 and obj.equipment.st * 20 or 50
        if obj.name=='dexterity':
            worth += obj.equipment.hit_plus > 0 and obj.equipment.hit_plus * 20 or 50
        if obj.name=='increase damage':
            worth += obj.equipment.dmg_plus > 0 and obj.equipment.dmg_plus * 20 or 50
        return worth
    if obj.type == 'potion':
        return potion_dict[obj.name].gold
    if obj.type in ('wand','staff','stick'):
        return stick_dict[obj.name].gold
    if obj.type == 'scroll':
        return scroll_dict[obj.name].gold
    if obj.type == 'amulet':
        return 1000
    return 0

def you_made_it():
    msgbox(
'                                                        \n'+
'  @  @              @   @                   @@@      @  \n'+           
'  @  @  @@@  @   @  @@ @@  @@@      @  @@@   @   @   @  \n'+        
'  @@@@ @   @ @   @  @ @ @ @   @  @@@@ @@@@@  @  @@@  @  \n'+         
'     @ @   @ @  @@  @   @ @  @@ @   @ @      @   @      \n'+     
'  @@@   @@@   @@ @  @   @  @@ @  @@@@  @@@  @@@  @@  @  \n'+
'                                                        \n'+
' Congratulations, you have made it to the light of day! \n'+
'                                                        \n'+
'   You have joined the elite ranks of those who have    \n'+ 
' escaped the Dungeons of Doom alive.  You journey home  \n'+
'    and sell all your loot at a great profit and are    \n'+
'            admitted to the fighters guild.             \n'+
'                                                        \n'+
'               --Press ESC to continue--                \n'
,56)
    clear_menu()

    types = ['food','weapon','armor','ring','potion','scroll','wand','staff','stick','amulet']
    type_order = dict(zip(types,range(0,len(types))))
    def k(x):
        return type_order[x.type],x.name
    property_list = []
    for k, g in itertools.groupby(sorted(inventory,key=k),key=k):
        group = list(g)
        property_list.append('%10dG %s'%(sum([o.gold for o in group]),display_name(group[0])))
    total = sum([o.gold for o in inventory])
    property_list.append('%10dG Gold Peices'%(purse-total))
    property_list.append('-'*INVENTORY_WIDTH)
    property_list.append('%10dG Total'%(purse))
    msgbox('%11s %s\n'%('Price','Item')+'\n'.join(property_list),INVENTORY_WIDTH)
    clear_menu()
    show_score()

class Score:
    def __init__(self,score,name,level,reason,date):
        self.score,self.name,self.level,self.reason,self.date = score,name,level,reason,date


def save_score(reason=None):
    file = shelve.open('score', 'c')
    #top_ten = file.has_key('top_ten') and file['top_ten'] or []
    top_ten = 'top_ten' in file and file['top_ten'] or []
    level = reason == 'A total winner' and max_dungeon_level or dungeon_level
    top_ten.append(Score(purse,user_name,level,reason,end_date.strftime('%Y-%m-%d %H:%M')))
    top_ten.sort(key=lambda s:s.score,reverse=True)
    top_ten = top_ten[0:10]
    file['top_ten'] = top_ten
    file.close()    

def show_score():
    file = shelve.open('score', 'r')
    top_ten = file['top_ten']
    file.close()    
    top_ten_list = ['Top Ten Adventurers:']
    #top_ten_list.append('Rank: Score: Name: Date:')
    for i,s in enumerate(top_ten):
        top_ten_list.append('Rank:%2d Score:%d Name:%s Date:%s '%(i+1,s.score,s.name,s.date))
        top_ten_list.append('        %s on level %d'%(s.reason,s.level))
    msgbox('\n'.join(top_ten_list),min(SCREEN_WIDTH,max([len(s) for s in top_ten_list])))

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #all tiles start unexplored
        self.explored = False

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

        self.dark = False # dark tiles are used in a dark room


class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, ch, name, color, type=None, blocks=0, always_visible=False, fighter=None, ai=None, item=None, equipment=None, trap=None,gold=None,active=True):
        self.x = x
        self.y = y
        self.ch = ch
        self.name = name
        self.color = color
        self.type = type
        self.blocks = blocks #0:not blocks,1:blocks both the player and monsters,2:blocks only monsters
        self.always_visible = always_visible
        self.fighter = fighter
        if self.fighter:  #let the fighter component know who owns it
            self.fighter.owner = self
            if type ==  'player':
                self.is_blocked = is_blocked
            else: # for monsters
                self.is_blocked = is_blocked_monsters

        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.owner = self

        self.equipment = equipment
        if self.equipment:  #let the Equipment component know who owns it
            self.equipment.owner = self

        self.gold = gold
        if self.gold:  #let the Gold component know who owns it
            self.gold.owner = self

        self.trap = trap
        if self.trap:  #let the Trap component know who owns it
            self.trap.owner = self

        self.active = active

    def move(self, dx, dy): #only fighters move
        #move by the given amount, if the destination is not blocked
        if not self.is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y): #only fighters move
        try:
            x0,y0 = xy(self)
            #(memo)if this object is a monster then is_blocked() is assigned to is_blocked_monsters()
            d,x,y = min([(manhattan_distance(x,y,target_x,target_y),x,y) for (x,y) in neighborhood(x0,y0) if not self.is_blocked(x,y)])
            self.move(x-x0,y-y0)
        except ValueError:
            pass

    def distance_to(self, other):
        #return the distance to another object
        return distance(*(xy(self)+xy(other)))

    def distance(self, x, y):
        #return the distance to some coordinates
        return distance(*(xy(self)+(x,y)))

    def send_to_back(self):
        #make this object be drawn first, so all others appear 
        #above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):
        #only show if it's visible to the player; or 
        #it's set to "always visible" and on an explored tile; or 
        #other conditions
        if map_is_in_fov(self.x, self.y) or \
                (self.always_visible and map[self.x][self.y].explored) or \
                (player.fighter.sense_monsters and self.fighter) or \
                (player.fighter.sense_magics and is_magic(self)):
            #set the color and then draw the character that 
            #represents this object at its position
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.ch, 
                                        libtcod.BKGND_NONE)

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

def is_magic(obj):
    if obj.type in ('potion','scroll','stick','ring','amulet'):
        return True
    if obj.type == 'armor' and obj.equipment.ac != armor_dict[obj.name].ac:
        return True
    if obj.type == 'weapon' and \
                (obj.equipment.hit_plus != 0 or obj.equipment.dmg_plus != 0):
        return True
    return False

def noop(*args):
    pass

class Fighter(object):
    #combat-related properties
    def __init__(self, hp, ac, st, xp, lvl, dmg, actions, special_attack=noop,carry=None):
        self.max_hp = hp # max hit point
        self.hp = hp # hit point
        self.ac = ac # armor class
        self._st = st # strength
        self.biggest_st = st # the biggest strength ever
        self.xp = xp # experience
        self.lvl = lvl # level
        self.dmg = dmg # damage
        self.actions = actions # a composite of fighter's actions delegating
        self.special_attack = special_attack
        self.carry = carry
        self.calories_left = FOOD_CALORIES
        self.hunger = 0 # 0:not,1:hungry,2:weak,3:fainting
        self.confusion_timer = 0
        self.blind_timer = 0
        self.cansee_timer = 0 #the player can see invisible stalkers
        self.held_timer = 0 #the player can't move
        self.sense_monsters = False #the ability of sensing monsters
        self.sense_magics = False #the ability of sensing magic items
        self.haste_timer = 0 #the player can move at double speed
        self.haste = False #a monster is in haste or not
        self.slow = False #a monster is slow or not
        self.cancel = False #a monster is forbidden to use special abilities or not
        self.canhuh = False #the player can confuse a monster

    @property
    def st(self):
        return self._st

    @st.setter
    def st(self,st):
        self._st = st
        if self._st > self.biggest_st:
            self.biggest_st = self._st

    def attack_by_slashing(self,target,weapon):
        getattr(self.actions,'attack_by_slashing',noop)(self.owner,target,weapon)

    def attack(self,target):
        getattr(self.actions,'attack',noop)(self.owner,target)
        
    def take_damage(self,damage,opponent):
        getattr(self.actions,'take_damage',noop)(self.owner,damage,opponent)

    def death(self,opponent):
        getattr(self.actions,'death',noop)(opponent)

    def heal(self,amount):
        getattr(self.actions,'heal',noop)(self.owner,amount)

    def attack_by_throwing(self,target,weapon,projectile):
        getattr(self.actions,'attack_by_throwing',noop)(self.owner,target,weapon,projectile)

    def throw(self,projectile,dx,dy):
        getattr(self.actions,'throw',noop)(self.owner,projectile,dx,dy)

    def use_calories(self):
        getattr(self.actions,'use_calories',noop)(self.owner)

# the hit bonus and the damage bonus to the player's strength
#        (st) 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,18,19,20,21
st_hit_plus=[-7,-6,-5,-4,-3,-2,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 2, 3]
st_dmg_plus=[-7,-6,-5,-4,-3,-2,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 4, 6]


def mimic_check(monster):
    if monster.type == 'monster' and (monster.ch < 'A' or monster.ch > 'Z'):
        message('Wait! that\'s a mimic!')
        monster.active = True
        return True
    return False

class PlayerActions: # Player Fighter's actions
    @staticmethod
    def attack_by_slashing(player,monster,weapon):
        if mimic_check(monster):
            return
        # judge if the swing hits
        hit = random.randint(1,20) + get_hit_plus(weapon)
        need = (21 - player.fighter.lvl) - monster.fighter.ac
        if hit < need:
            msg = random
            message('You' + 
                    random.choice([' attack and miss ',' barely miss ',' don\'t hit ']) + 
                    monster.name)
            return
        damage = max(0,roll(get_dmg(weapon)) + get_dmg_plus(weapon))
        message('You attack ' + monster.name + ' for ' + str(damage) + ' hit points.')
        if player.fighter.canhuh:
            player.fighter.canhuh = False
            #replace the monster's AI with a "confused" one; 
            #after some turns it will restore the old AI
            old_ai = monster.ai
            monster.ai = ConfusedMonster(0.8,old_ai)
            monster.ai.owner = monster  #tell the new component who owns it
            message('Your hands stop glowing red.',color_scroll)
            message('The eyes of the ' + monster.name + 
                    ' look vacant, as he starts to stumble around!',color_scroll)
        monster.fighter.take_damage(damage,player)

    @staticmethod
    def attack(player,monster):  # the player slashes a monster
        global peace
        peace = False
        PlayerActions.attack_by_slashing(player,monster,get_current_weapon())

    @staticmethod
    def take_damage(player,damage,monster): # the player takes damage
        global peace
        peace = False
        #damage=0 #test
        player.fighter.hp -= damage
        if player.fighter.hp > 0:
            return
        PlayerActions.death(monster)

    @staticmethod
    def death(monster): # the player died
        global game_state,user_name,killer_monster_name,end_date
        game_state = 'you died'
        message('You died!', libtcod.red)
        user_name = get_user_name()
        killer_monster_name = monster.name
        end_date = datetime.now()
        save_game()
        save_score('Killed by a '+ monster.name)

    @staticmethod
    def heal(player,amount): # the player heals
        #heal the player by the given amount, not exceed the maximum
        player.fighter.hp = min(player.fighter.hp + amount, player.fighter.max_hp)

    @staticmethod
    def attack_by_throwing(player,monster,weapon,projectile):
        mimic_check(monster)
        # judge if the projectile hits a monster
        hit = random.randint(1,20) + get_throwing_hit_plus(weapon,projectile)
        need = (21 - player.fighter.lvl) - monster.fighter.ac
        if hit < need:
            message('The '+display_name(projectile.owner)+' misses '+monster.name)
            return
        damage = max(0,roll(get_throwing_dmg(weapon,projectile)) + 
                        get_throwing_dmg_plus(weapon,projectile))
        message('The '+display_name(projectile.owner) + ' hits ' + monster.name + 
                ' for ' + str(damage) + ' hit points.')
        monster.fighter.take_damage(damage,player)

    @staticmethod
    def throw(player,projectile,dx,dy): # the player throws a weapon
        global peace
        peace = False
        if projectile.is_equipped and not projectile.dequip():
            return
        #move the projectile to the direction of dx,dy
        x,y = projectile_motion(projectile.owner,dx,dy)
        objects.append(projectile.owner)
        inventory.remove(projectile.owner)
        projectile.owner.send_to_back()
        monster = monster_at(x,y)
        if monster == None:
            message('You threw away a ' + display_name(projectile.owner) + '.')
            return
        projectile.owner.x = x
        projectile.owner.y = y
        PlayerActions.attack_by_throwing(player,monster,get_current_weapon(),projectile)

    @staticmethod
    def use_calories(player): # the player uses calories
        global no_command
        if player.fighter.calories_left <= 0:
            if no_command or random.randint(1,5) > 1:
                return
            no_command = generate_no_command(random.randint(4,12))
            message('You feel too weak from lack of food.')
            player.fighter.hunger = 3
            return

        ring_eat = 0
        for r in get_current_rings():
            if r.owner.name == 'sustain strength':
                ring_eat += 1
            if r.owner.name == 'searching' and random.randint(1,3)==1:
                ring_eat += 1
            if r.owner.name == 'regeneration':
                ring_eat += 2
            if r.owner.name == 'slow digestion' and random.randint(1,2)==1:
                ring_eat -= 1
        old = player.fighter.calories_left
        player.fighter.calories_left -= 1 - (1 if have_amulet() else 0) + ring_eat
        if player.fighter.calories_left <= 150:
            if old > 150:
                message('You are starting to feel weak.')
            player.fighter.hunger = 2
            return

        if player.fighter.calories_left <= 300:
            if old > 300:
                message('You are starting to get hungry.')
            player.fighter.hunger = 1
            return

fungi_hit = 0

class MonsterActions: # Monster Fighter's actions
    @staticmethod
    def attack(monster,player): # a monster attacks the player
        def attack_once(dmg):
            global fungi_hit
            hit = random.randint(1,20) + st_hit_plus[monster.fighter.st]
            need = 21 - monster.fighter.lvl
            need -= get_player_ac()
            if hit <= need: # judge the swing
                message(monster.name.capitalize() + ' attacks ' + 
                        player.name + ' but it has no effect!', color_monster)
                if monster.name == 'violet fungi':
                    player.fighter.take_damage(fungi_hit,monster)
                return
            if monster.name == 'violet fungi':
                fungi_hit += 1
            damage=roll(dmg)+st_dmg_plus[monster.fighter.st]
            if damage > 0:
                message(monster.name.capitalize() + ' attacks ' + 
                        player.name + ' for ' + str(damage) + ' hit points.',color_monster)
                player.fighter.take_damage(damage,monster)
            else:
                message(monster.name.capitalize() + ' attacks ' + 
                        player.name + ' but it has no effect!',color_monster)
            if not monster.fighter.cancel:
                monster.fighter.special_attack(monster)

        for dmg in monster.fighter.dmg.split('/'):
            if monster.name == 'violet fungi' and fungi_hit:
                dmg = str(fungi_hit) + 'D1'
            attack_once(dmg)
        if monster.name in ('troll','vampire') and random.randint(1,3)==1:
            monster.fighter.hp += 1 #regeneration
            message(monster.name.capitalize()+ ' recovered a hit point.', color_monster)

    @staticmethod
    def take_damage(monster, damage, player): # a monster takes damage
        global fungi_hit, no_command
        monster.active = True
        monster.fighter.hp -= damage
        if monster.fighter.hp > 0:
            return
        #the monster is dead.
        message('The ' + monster.name + ' is dead! You gain ' + 
                str(monster.fighter.xp) + ' experience points.', libtcod.orange)
        player.fighter.xp += monster.fighter.xp
        if monster.name == 'violet fungi':
            fungi_hit = 0
            player.fighter.held_timer = 0
        if monster.fighter.carry:
            adjacent = [(x,y) for (x,y) in neighborhood(*xy(monster)) if not is_blocked(x,y)]
            if adjacent:
                x,y = random.choice(adjacent)
                monster.fighter.carry.x = x
                monster.fighter.carry.y = y
                objects.append(monster.fighter.carry)
                monster.fighter.carry.send_to_back()
            else:
                message('Your '+monster.fighter.carry.name+' vanishes as it hits the ground.')
            monster.fighter.carry=None
        #the corpse disappears to somewhere
        monster.clear()
        objects.remove(monster)

def get_player_ac():
    armor = get_current_armor()
    ac = armor and armor.ac or player.fighter.ac
    for r in get_current_rings():
        ac -= r.ac
    return ac

def get_player_st():
    st = player.fighter.st
    for r in get_current_rings():
        st += r.st
    return min(21,st)

def get_hit_plus(weapon):
    hit_plus = st_hit_plus[get_player_st()]
    if weapon != None:
        hit_plus += weapon.hit_plus
    hit_plus += sum([ring.hit_plus for ring in get_current_rings()])
    #hit_plus=100#test
    return hit_plus

def get_throwing_hit_plus(weapon,projectile):
    hit_plus = st_hit_plus[get_player_st()]
    hit_plus += projectile.hit_plus
    if weapon and weapon.owner.name == projectile.launcher:
        hit_plus += weapon.hit_plus
    hit_plus += sum([ring.hit_plus for ring in get_current_rings()])
    return hit_plus

def get_dmg(weapon):
    if weapon != None:
        return weapon.dmg
    return player.fighter.dmg

def get_throwing_dmg(weapon,projectile):
    dmg = projectile.hurl_dmg
    if not (weapon or projectile.launcher) or \
            (weapon and weapon.owner.name == projectile.launcher):
        dmg = projectile.launch_dmg
    return dmg

def get_dmg_plus(weapon):
    dmg_plus = st_dmg_plus[get_player_st()]
    if weapon != None:
        dmg_plus += weapon.dmg_plus
    dmg_plus += sum([ring.dmg_plus for ring in get_current_rings()])
    #dmg_plus=100#test
    return dmg_plus

def get_throwing_dmg_plus(weapon,projectile):
    dmg_plus = st_dmg_plus[get_player_st()]
    dmg_plus += projectile.dmg_plus
    if weapon and weapon.owner.name == projectile.launcher:
        dmg_plus += weapon.dmg_plus
    dmg_plus += sum([ring.dmg_plus for ring in get_current_rings()])
    return dmg_plus

def roll(dice):
    # dice: (ex)'1D4'
    i = dice.find('D')
    number = int(dice[:i])
    sides = int(dice[i+1:])
    return sum([random.randint(1,sides) for n in range(number)]) 

def xy(o):
    return o.x,o.y

def distance(sx,sy,ex,ey):
    #Chebyshev distance
    dx = abs(ex - sx)
    dy = abs(ey - sy)
    return max(dx,dy)

def manhattan_distance(sx,sy,ex,ey):
    #Manhattan distance
    dx = abs(ex - sx)
    dy = abs(ey - sy)
    return dx+dy

def chase_player(monster):
    rm = room_at(*xy(monster))
    rp = room_at(*xy(player))
    if rm != rp and rm != None:
        #move towards the nearest door to the player
        doors = get_doors(rm)
        if len(doors) > 0:
            d,x,y = min((player.distance(x,y),x,y) for x,y in doors)
            monster.move_towards(x,y)
        return
    monster.move_towards(*xy(player))

class BasicMonster: #AI for a basic monster.
    def take_turn(self):
        monster = self.owner
        if not monster.active and monster.distance_to(player)==1:
            monster.active = True
        if not monster.active:
            return
        # attack the player
        if monster.distance_to(player)==1:
            monster.fighter.attack(player)
            return
        # chase the player
        chase_player(monster)

def mean_monster_activation(monster):
    # if the player sees a mean monster, 
    # then it starts chasing the player
    if monster.active:
        return
    if monster.distance_to(player)==1:
        monster.active = True
        return
    x,y=xy(monster)
    rm = room_at(x,y)
    if rm == None or rm != room_at(*xy(player)):
        return
    if next((r for r in get_current_rings() if r.owner.name == 'stealth'),None):
        return
    if map[x][y].dark:
        if monster.distance_to(player)<=2:
            monster.active = True
        return
    if random.randint(0,99) > 33:
        monster.active = True
        return

class MeanMonster: #AI for a mean monster
    def take_turn(self):
        monster = self.owner
        mean_monster_activation(monster)
        if not monster.active:
            return
        # attack the player
        if monster.distance_to(player)==1:
            monster.fighter.attack(player)
            return
        # chase the player
        chase_player(monster)

class ConfusedMonster: #AI for a confused monster
    def __init__(self, rate, old_ai=None):
        self.rate = rate # rate of confusion (ex) 0.2
        self.old_ai = old_ai

    def take_turn(self):
        monster = self.owner
        if self.old_ai != None:
            if random.randint(1,1000) < 50:
                monster.ai =  self.old_ai
                return
        if not monster.active and monster.distance_to(player)==1:
            monster.active = True
        if not monster.active:
            return
        # random move
        if random.random() < self.rate:
            monster.move(random.choice((0,-1,1)),random.choice((0,-1,1)))
            return
        # attack the player
        if monster.distance_to(player)==1:
            monster.fighter.attack(player)
            return
        # chase the player
        chase_player(monster)

class InvisibleStalker(object): #AI for a invisible stalker
    def __init__(self):
        self.base_ai = ConfusedMonster(0.2)
        self._owner=None

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self,owner):
        self._owner = owner
        self.base_ai.owner = owner

    def take_turn(self):
        self.base_ai.take_turn()
        if player.fighter.cansee_timer == 0 and not self.owner.fighter.cancel \
                and random.randint(1,10) > 1:
            self.owner.color = color_light_ground
        else:
            self.owner.color = color_monster

class Mimic: #AI for a mimic
    def take_turn(self):
        monster = self.owner
        if not monster.active:
            return
        if monster.ch != 'M':
            monster.ch = 'M'
            monster.name = 'mimic'
            monster.color = color_monster
        # attack the player
        if monster.distance_to(player)==1:
            monster.fighter.attack(player)
            return
        # chase the player
        chase_player(monster)

class HeldMonster: #AI for a held monster
    def take_turn(self):
        monster = self.owner
        if monster.active == True:
            monster.ai = copy.copy(monster_dict[monster.ch].ai)
            monster.ai.owner = monster

class Item:
    #an item that can be picked up and used.
    def __init__(self, charges=0,type=None,use_function=None,true_name=None):
        self.charges = charges 
        self.type = type
        self.use_function = use_function
        self.true_name = true_name

    def pick_up(self):
        #add to the player's inventory and remove from the map
        if not space_in_inventory(self.owner.name,self.owner.type):
            message('Your inventory is full, cannot pick up ' + 
                    display_name(self.owner) + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            self.owner.clear()
            objects.remove(self.owner)
            message('You picked up a ' + display_name(self.owner) + '!', libtcod.light_green)

    def drop(self):
        #special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment and self.owner.equipment.is_equipped \
            and not self.owner.equipment.dequip():#cursed equipments can't be dequipped
            return

        #add the item to the map and remove it from the player's inventory 
        #and place it at the player's current position
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + display_name(self.owner) + '.', libtcod.yellow)

    def use(self):
        #special case: if the object has a Equipment component, 
        #              the "use" command does equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        #just call the "use_function" if it is defined
        if not self.use_function:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() == 'canceled':
                return 'canceled'
            if self.owner.type == 'stick':
                self.charges -= 1
                self.charges == 0 and inventory.remove(self.owner)
            else:
                inventory.remove(self.owner)  #destroy after use, unless it has been canceled

class Equipment:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self, dmg=None, hurl_dmg=None, launch_dmg=None, launcher=None, hit_plus=0, dmg_plus=0, ac=0, st=0, cursed=False,equip_function=None,dequip_function=None):
        self.slot = None
        self.dmg = dmg # (ex) '1D4'
        self.hurl_dmg = hurl_dmg # (ex) 1D2
        self.launch_dmg = launch_dmg #(ex) 1D5
        self.launcher = launcher #(ex) 'bow'
        self.hit_plus = hit_plus 
        self.dmg_plus = dmg_plus
        self.ac = ac #armor class
        self.st = st #strength
        self.cursed = cursed
        self.equip_function = equip_function
        self.dequip_function = dequip_function

        self.is_equipped = False

    def toggle_equip(self):  #toggle equipment/dequipment status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        def after():
            self.is_equipped = True
            message('Equipped ' + display_name(self.owner) + ' on ' + self.slot + '.', libtcod.light_green)

        def equip_weapon():
            hand = get_equipped_in_slot('hand')
            if hand and not hand.dequip():
                return
            self.slot = 'hand'
            after()
            
        def equip_armor():
            body = get_equipped_in_slot('body')
            if body and not body.dequip():
                return
            self.slot = 'body'
            after()
        
        def equip_ring():
            left = get_equipped_in_slot('left')
            right = get_equipped_in_slot('right')
            if left and right:
                message('You already have a ring on each hand.', libtcod.light_green)
                return
            self.slot = not left and 'left' or 'right'
            if self.equip_function:
                self.equip_function()
            after()

        if self.owner.type == 'weapon':
            equip_weapon()
        elif self.owner.type == 'armor':
            equip_armor()
        elif self.owner.type == 'ring':
            equip_ring()

    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped:
            return False
        if self.cursed:
            message("You can't. It appears to be cursed.")
            return False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)
        self.slot = None
        self.is_equipped = False

        if self.owner.type == 'ring' and self.dequip_function:
            self.dequip_function()

        return True

def get_equipped_in_slot(slot):  #returns the equipment in a slot, or None if empty
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def get_current_weapon():
    obj = next((obj for obj in inventory if obj.type=='weapon' and obj.equipment.is_equipped),None)
    if obj:
        return obj.equipment
    return None

def get_current_armor():
    obj = next((obj for obj in inventory if obj.type=='armor' and obj.equipment.is_equipped),None)
    if obj:
        return obj.equipment
    return None

def get_current_rings():
    return [obj.equipment for obj in inventory if obj.type=='ring' and obj.equipment.is_equipped]

def have_amulet():
    return next((i for i in inventory if i.type == 'amulet'),None)

display_titles ={
'scroll':'scroll of ',
'potion':'potion of ',
'wand' :'wand of ',
'staff' :'staff of ',
'ring'  :'ring of '}

def display_name(obj):
    type = obj.type=='stick' and obj.item.type or obj.type 
    return display_titles.get(type,'')+obj.name

class Gold:
    def __init__(self):
        self.value = random.randint(2,52+dungeon_level*10)

    def pick_up(self):
        global purse
        purse += self.value
        self.owner.clear()
        objects.remove(self.owner)
        message('You found '+ str(self.value) +' gold pieces.', libtcod.green)

class Trap:
    def __init__(self,trap_type=None):
        self.trap_type = trap_type


def is_blank(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return False

    #now check for existing of objects
    if next((o for o in objects if o.x == x and o.y == y),None):
        return False

    return True

def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True

    #now check for any blocking objects
    if next((o for o in objects if o.x == x and o.y == y and o.blocks == 1),None):
        return True

    return False

def is_blocked_monsters(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True

    #now check for any blocking objects
    if next((o for o in objects if o.x == x and o.y == y and o.blocks >= 1),None):
        return True

    return False

def create_room(room):
    #go through the tiles in the rectangle and make them passable
    for x, y in region(room.x1+1,room.y1+1,room.x2-1,room.y2-1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def dark_room(room,dark=True):
    for x, y in region(room.x1,room.y1,room.x2,room.y2):
        map[x][y].dark = dark

def undark_room(room):
    dark_room(room,False)

def create_h_tunnel(x1, x2, y): # make a horizontal tunnel between rooms
    if x1>x2:
        x1,x2=x2,x1
    #horizontal tunnel
    for x,y in region(x1,y,x2,y):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x): # make a virtical tunnel between rooms
    if y1>y2:
        y1,y2=y2,y1
    #vertical tunnel
    for x,y in region(x,y1,x,y2):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def get_doors(rm):
    wall = [(x,rm.y1) for x in range(rm.x1,rm.x2+1)]+ \
           [(x,rm.y2) for x in range(rm.x1,rm.x2+1)]+ \
           [(rm.x1,y) for y in range(rm.y1+1,rm.y2)]+ \
           [(rm.x2,y) for y in range(rm.y1+1,rm.y2)]
    return [(x,y) for (x,y) in wall if map[x][y].blocked == False]

#the table of a binomial probability mass function, given n=9,p=0.35
binom_pmf = [
0.020711912837890634,0.10037311606054677,0.21618824997656225,
0.27162113458593728,0.21938630101171847,0.11813108516015607,
0.042406030570312447,0.0097860070546874831,0.001317347103515622,7.8815638671874823e-05]

def make_map():
    global map, objects, stairs, rooms, not_gone_rooms, fungi_hit

    #the list of objects with just the player
    objects = [player]

    #fill map with "blocked" tiles
    map = [[ Tile(True)
             for y in range(MAP_HEIGHT) ]
           for x in range(MAP_WIDTH) ]

    rooms = []

    map_width_one_third = int(MAP_WIDTH/3)
    map_height_one_third = int(MAP_HEIGHT/3)

    room_max_size_x = map_width_one_third - 2 # shorten to prevent rooms from touching each other
    room_max_size_y = map_height_one_third - 2 # shorten to prevent rooms from touching each other
    room_min_size = 3 # common for x,y

    room_ids = range(9)
    for i in room_ids:
        #random width and height
        w = random.randint(int(room_min_size),int(room_max_size_x))
        h = random.randint(int(room_min_size),int(room_max_size_y))
        #random position without going out of the boundaries of the map
        x = map_width_one_third*(i%3) + random.randint(1,int(map_width_one_third - w))
        y = map_height_one_third*int(i/3) + random.randint(1,int(map_height_one_third - h))
        #"Rect" class makes rectangles easier to work with
        #finally, append the new room to the list
        rooms.append(Rect(x, y, w, h))

    #be some rooms gone
    gone_ids = random.sample(room_ids,random.randint(0,3))
    for i in gone_ids:
        rooms[i] = Rect(rooms[i].x1,rooms[i].y1,2,2)
    not_gone_rooms = [rooms[i] for i in set(room_ids) - set(gone_ids)]

    #"paint" rooms to the map's tiles
    for r in rooms:
        create_room(r)
        if random.randint(1,10) < dungeon_level:
            dark_room(r)

    #set traps
    if random.randint(0,9) < dungeon_level:
        max_traps = min(10,random.randint(0,int(dungeon_level/4))+1)
        #distribute the traps into the rooms
        i = 0
        while (i < max_traps):
            i += place_object(random.choice(not_gone_rooms),'trap')

    #test for trap
    #for _ in range(20):
    #    place_object(random.choice(not_gone_rooms),'trap')

    #you don't have an amulet or you have reached to the deeper ever
    if not have_amulet() or dungeon_level > max_dungeon_level: 
        #put the gold in
        for r in not_gone_rooms:
            place_gold(r)

        #maximum number of items at the level
        max_items = weighted_random_choice(range(len(binom_pmf)),binom_pmf)
        #max_items=20#test max_items

        #distribute the items into the rooms
        i = 0
        while (i < max_items):
            type = weighted_random_choice(list(item_dict.keys()),list(item_dict.values()))
            i += place_object(random.choice(not_gone_rooms),type)

    if not have_amulet() and dungeon_level >= AMULET_LEVEL:
        #place an amulet
        while True:
            if place_object(random.choice(not_gone_rooms),'amulet'):
                break

    fungi_hit = 0

    #add monsters to the rooms
    for r in not_gone_rooms:
        place_monsters(r)

    #connect rooms
    connection_candidates = [[0,1],[0,3],[1,2],[1,4],[2,5],[3,4],[3,6],[4,5],[4,7],[5,8],[6,7],[7,8]]
    connections = []
    connected_rooms = set()
    room = random.choice(room_ids)
    try:
        #check that (i,j) is a pair of the room and a not connected room 
        def check(i,j):
            if room not in (i,j):
                return False
            if i==room:
                i=j
            return i not in connected_rooms
        while True:
            for c in [c for c in connection_candidates if check(*c)]:
                connections.append(c)
                connected_rooms.update(c)
                if len(connections) == 8:
                    raise StopIteration
            room = random.choice(list(connected_rooms))
    except StopIteration:
        pass

    # make additional connections
    connections.extend(random.sample([c for c in connection_candidates if c not in connections],random.randint(0,4)))

    # dig tunnels
    for (i,j) in connections:
        if i+1==j: #the connection is from left to right
            sx = rooms[i].x2
            sy = random.choice(range(rooms[i].y1+1,rooms[i].y2))
            ex = rooms[j].x1
            ey = random.choice(range(rooms[j].y1+1,rooms[j].y2))
            turn_spot = random.choice(range(sx+1,max(sx+2,ex-1)))
            create_h_tunnel(sx,turn_spot,sy)
            create_v_tunnel(min(sy,ey),max(sy,ey),turn_spot)
            create_h_tunnel(turn_spot,ex,ey)
        else: #the connection is from up to down
            sx = random.choice(range(rooms[i].x1+1,rooms[i].x2))
            sy = rooms[i].y2
            ex = random.choice(range(rooms[j].x1+1,rooms[j].x2))
            ey = rooms[j].y1
            turn_spot = random.choice(range(sy+1,max(sy+2,ey-1)))
            create_v_tunnel(sy,turn_spot,sx)
            create_h_tunnel(min(sx,ex),max(sx,ex),turn_spot)
            create_v_tunnel(turn_spot,ey,ex)

    def get_blank_pos():
        while True:
            x,y=get_random_pos(random.choice(not_gone_rooms))
            if is_blank(x,y):
                return x,y

    #create stairs
    new_x,new_y = get_blank_pos()
    stairs = Object(new_x, new_y, '%', 'stairs', libtcod.white, always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()  #so it's drawn below the monsters

    # the player's initial position
    player.x,player.y = get_blank_pos()

    #create secret doors
    for rm in not_gone_rooms:
        for x,y in get_doors(rm):
            if random.randint(1,10) < dungeon_level and random.randint(1,5) == 1:
                secret_door = Object(x, y, ' ', 'secret door', libtcod.white, blocks=1)
                objects.append(secret_door)
                map[x][y].blocked = True
                map[x][y].block_sight = True

def place_gold(room): #place gold in the room
    if random.randint(0,1):
        return
    #choose random spot for this gold
    for i in range(20): # try 20 times
        x,y=get_random_pos(room)
        if not is_blocked(x, y):
            break
    else:
        return #failed to get a free spot for gold

    #create a gold
    obj = create_object('gold',x,y)
    objects.append(obj)
    obj.send_to_back()
    obj.always_visible = True

def weighted_random_choice(lst,chances):
    assert(abs(1.0 - sum(chances)) <= len(chances) * sys.float_info.epsilon)
    assert(len(lst)==len(chances))
    r = random.random()
    cum = 0
    for l,c in zip(lst,chances):
        cum += c
        if r <= cum:
            return l
    return lst[-1] # for the case sum(chances) is less than 1.0 by the numerical error

item_dict = OrderedDict([
#type:chance
('potion',0.25),
('scroll',0.25),
('food',0.22),
('weapon',0.09),
('armor',0.09),
('ring',0.05),
('stick',0.05)])

trap_dict = OrderedDict([
#type:chance
('trap door',0.167),
('arrow trap',0.167),
('sleeping gas trap',0.167),
('beartrap',0.167),
('teleport trap',0.166),
('dart trap',0.166)])

def create_object(type,x=0,y=0):
    if type == 'potion':
        name = weighted_random_choice(list(potion_dict.keys()),[a.chance for a in potion_dict.values()])
        return generate_potion(name,x,y)
    elif type == 'scroll':
        name = weighted_random_choice(list(scroll_dict.keys()),[a.chance for a in scroll_dict.values()])
        return generate_scroll(name,x,y)
    elif type == 'weapon':
        name = random.choice(list(weapon_dict.keys()))
        if name == 'arrow':
            return [generate_weapon(name,x,y) for _ in range(random.randint(8,15))]
        return generate_weapon(name,x,y)
    elif type == 'armor':
        name = weighted_random_choice(list(armor_dict.keys()),[a.chance for a in armor_dict.values()])
        return generate_armor(name,x,y)
    elif type == 'food':
        return generate_food(x,y)
    elif type == 'ring':
        name = weighted_random_choice(list(ring_dict.keys()),[a.chance for a in ring_dict.values()])
        return generate_ring(name,x,y)
    elif type == 'stick':
        name = weighted_random_choice(list(stick_dict.keys()),[a.chance for a in stick_dict.values()])
        return generate_stick(name,x,y)
    elif type == 'amulet':
        return Object(x, y, ',', 'The Amulet of Yendor', color_amulet, type='amulet', item=Item())
    elif type == 'trap':
        trap_type = weighted_random_choice(list(trap_dict.keys()),list(trap_dict.values()))
        return Object(x, y, ' ', '', color_trap, type='trap',trap=Trap(trap_type))
    elif type == 'gold':
        return Object(x, y, '*', 'gold', color_gold, type='gold', gold=Gold())

def get_random_pos(room):
    x = random.randint(int(room.x1+1), int(room.x2-1))
    y = random.randint(int(room.y1+1), int(room.y2-1))
    return x,y

def place_object(room,type):
    #find a random and not blocked spot for this item
    x,y = get_random_pos(room)
    if is_blocked(x, y):
        return 0 # failed to find a spot

    thing = create_object(type,x,y)
    if not thing:
        return None

    def regist(obj):
        objects.append(obj)
        obj.send_to_back()  #appear below other objects
        obj.always_visible = True  #being visible even out-of-FOV, if in an explored area

    if hasattr(thing, '__iter__'):
        for obj in thing:
            regist(obj)
    else:
        regist(thing)

    return 1

class WeaponInfo:
    def __init__(self,dmg,hurl_dmg,launch_dmg,launcher,gold):
        self.dmg,self.hurl_dmg,self.launch_dmg,self.launcher,self.gold = dmg,hurl_dmg,launch_dmg,launcher,gold

weapon_dict = OrderedDict([(i[0],WeaponInfo(*i[1:])) for i in [
#[name,dmg,hurl_dmg,launch_dmg,launcher,gold]
# the lanuncher is None means bare hands
['mace','2D4','1D3','1D3',None,8],
['long sword','1D10','1D2','1D2',None,15],
['bow','1D1','1D1','1D1',None,75],
['arrow','1D1','1D1','1D6','bow',1],
['dagger','1D6','1D4','1D6',None,2],
['rock','1D2','1D2','1D4','sling',1],
['two handed sword','1D6','1D2','1D2',None,30],
['sling','0D0','0D0','0D0',None,1],
['dart','1D1','1D1','1D3',None,1],
['crossbow','1D1','1D1','1D1',None,15],
['crossbow bolt','1D2','1D2','1D10','crossbow',1],
['spear','1D8','1D6','1D8',None,2]]])

def generate_weapon(name,x=0,y=0):
    hplus = 0
    if random.randint(1,10) < 2:
        hplus -= random.randint(1,3)
    if random.randint(1,20) < 4:
        hplus += random.randint(1,3)
    weapon = weapon_dict[name]
    equipment_component = Equipment(dmg=weapon.dmg, hurl_dmg=weapon.hurl_dmg,
                                    launch_dmg=weapon.launch_dmg, launcher=weapon.launcher, hit_plus=hplus)
    if random.randint(1,10) < 2:
        equipment_component.cursed = True
    return Object(x, y, ')', name, color_weapon, type='weapon', equipment=equipment_component, item=Item())

class ArmorInfo:
    def __init__(self,ac,chance,gold):
        self.ac,self.chance,self.gold = ac,chance,gold

armor_dict = OrderedDict([(i[0],ArmorInfo(*i[1:])) for i in [
#[name,ac,chance,gold]
['leather armor',8,0.2,5],
['ring mail',7,0.15,30],
['studded leather armor',7,0.15,15],
['scale mail',6,0.13,3],
['chain mail',5,0.12,75],
['splint mail',4,0.1,80],
['bandid mail',4,0.1,90],
['plate mail',3,0.05,400]]])

def generate_armor(name,x=0,y=0):
    #create an armor
    ac = armor_dict[name].ac
    if random.randint(1,5) < 2:
        ac += random.randint(1,3)
    if random.randint(1,10) < 4:
        ac -= random.randint(1,3)
    equipment_component = Equipment(ac=ac)
    if random.randint(1,5) < 2:
        equipment_component.cursed = True
    return Object(x, y, ']', name, color_armor, type='armor', equipment=equipment_component,item=Item())

def generate_food(x=0,y=0):
    #create a food
    yummy = random.randint(0,9)==0
    item_component = Item(use_function=Eat(yummy))
    return Object(x, y, ':', 'food', color_food, type='food', blocks=0, item=item_component)

class Eat:
    #only the player can eat
    def __init__(self,yummy):
        self.yummy = yummy
    def __call__(self):
        if self.yummy:
            message('My, that was a yummy slime.')
        else:
            if random.randint(1,3)==1:
                message('Yuk,this food tastes awful.')
                player.fighter.xp += 1
            else:
                message('Yum,that tasted good.')

        player.fighter.calories_left += min(FULL_STOMACK,FOOD_CALORIES + random.randint(-200,200))
        player.fighter.hunger = 0

def use_scroll_confuse():
    #ask the player for a target to confuse
    message('Your hands begin to glow red.', color_scroll)
    player.fighter.canhuh = True

def use_scroll_map():
    global fov_recompute
    fov_recompute = True
    for o in [o for o in objects if o.name=='secret door']:
        map[o.x][o.y].blocked = False
        map[o.x][o.y].block_sight = False
        o.clear()
        objects.remove(o)
    for x,y in region(0,0,MAP_WIDTH-1,MAP_HEIGHT-1):
        if map[x][y].blocked == False:
            map[x][y].explored = True
    message('Oh, now this scroll has a map on it.', color_scroll)

def use_scroll_light():
    global fov_recompute
    fov_recompute = True
    r = room_at(*xy(player))
    if r == None:
        message('The corridor glows and then fades.', color_scroll)
        return
    undark_room(r)
    message('The room is lit by a shimmering blue light.', color_scroll)

def use_scroll_hold():
    x,y = xy(player)
    for i,j in region(max(0,x-2),max(0,y-2),min(x+2,MAP_WIDTH-1),min(y+2,MAP_HEIGHT-1)):
        monster = monster_at(i,j)
        if monster != None:
            monster.active = False
            monster.ai = HeldMonster()
            monster.ai.owner = monster
    message('Nearby monsters are paralyzed and can\'t move.', color_scroll)

no_command = None
no_command_turn_left = 0

def generate_no_command(turn):
    global no_command, no_command_turn_left
    for no_command_turn_left in reversed(range(turn)):
        start = time.time()
        while True:
            end = time.time()
            if end - start > 1.0: # 1 second elapsed
                yield None # None means the player takes a turn but does nothing
                break
            yield 'didnt-take-turn'
    no_command = None
    yield 'didnt-take-turn'

def use_scroll_sleep():
    global no_command
    no_command = generate_no_command(random.randint(4,8))
    message('You fall a sleep.', color_scroll)

def use_scroll_armor():
    armor = get_current_armor()
    if armor == None:
        return
    armor.cursed = False
    armor.ac -= 1
    message('Your armor glows faintly for a moment.', color_scroll)

def use_scroll_ident():
    message('Select an item you want to identify.', color_scroll)
    draw_gui() #show the message
    clear_menu() #clear previous menu
    chosen_item = inventory_menu('Press the key next to an item to identify, or any other to cancel.\n')
    if chosen_item:
        if chosen_item.owner.type in magic_types:
            reveal_magic_item_name(chosen_item.true_name,chosen_item.owner.type)
        message(display_name(chosen_item.owner), color_scroll)

def use_scroll_scare():
    #reading a scroll of scare monster is a mistake
    #and produces laughter at the poor rogue's boo boo.
    message('You hear maniacal laughter in the distance.', color_scroll)

def use_scroll_gfind():
    gold  = [obj for obj in objects if obj.gold]
    if gold == []:
        message('You begin to feel a pull downward.', color_scroll)
        return
    message('You begin to feel greedy and you sense gold.', color_scroll)
    for g in gold:
        map[g.x][g.y].explored = True

def teleport():
    global fov_recompute, no_command
    fov_recompute = True
    no_command = None
    while True:
        x,y = get_random_pos(random.choice(not_gone_rooms))
        if not is_blocked(x, y):
            break
    player.move(x-player.x,y-player.y)

def use_scroll_telep():
    teleport()

def use_scroll_weapon():
    weapon = get_current_weapon()
    if weapon == None:
        message('You feel a strange sense of loss.', color_scroll)
        return
    weapon.cursed = False
    if random.randint(0,1):
        weapon.hit_plus += 1
    else:
        weapon.dmg_plus += 1
    message('Your '+weapon.owner.name+' glows blue for a moment.', color_scroll)
    
def use_scroll_create():
    adjacent = [(x,y) for (x,y) in neighborhood(*xy(player)) if not is_blocked_monsters(x,y)]
    if len(adjacent) > 0 and random.randint(0,2) < 2:
        x,y = random.choice(adjacent)
        objects.append(generate_monster(random_select_monster(),x,y))
        return
    message('You hear a faint cry of anguish in the distance.', color_scroll)

def use_scroll_remove():
    armor = get_current_armor()
    if armor:
        armor.cursed = False
    weapon = get_current_weapon()
    if weapon:
        weapon.cursed = False
    for r in get_current_rings():
        r.cursed = False
    message('You feel as if somebody is watching over you.', color_scroll)

def use_scroll_aggr():
    message('You hear a high pitched humming noise.', color_scroll)
    for o in objects:
        if o != player and o.fighter:
            o.active = True

def use_scroll_nop():
    message('This scroll seems to be blank.', color_scroll)

def use_scroll_genocide():
    message('You have been granted the boon of genocide.', color_scroll)
    header = 'Which monster do you wish to wipe out?'
    monsters = ["'"+k + "' " + m.name for k,m in monster_dict.items()]
    index = menu(header, monsters, INVENTORY_WIDTH)
    if index:
        ch = list(monster_dict.keys())[index]
        for o in [o for o in objects if o.ch == ch]:
            o.fighter.take_damage(9999,player)

def use_potion_confusion():
    message("Wait, what's going on here, Huh? What? Who?", libtcod.sky) 
    player.fighter.confusion_timer += random.randint(20,27)

def use_potion_paralysis():
    global no_command
    message("You can't move.", libtcod.sky)
    no_command = generate_no_command(20)

def use_potion_poison():
    message('You feel very sick now.', libtcod.sky)
    player.fighter.st = max(3,player.fighter.st - random.randint(1,3))

def use_potion_gain_strength():
    message('You feel stronger, now. What building muscles!', libtcod.sky)
    player.fighter.st = min(21, player.fighter.st + 1)

def cancel_blind():
    global fov_recompute
    if player.fighter.blind_timer > 0:
        fov_recompute = True
        player.fighter.blind_timer = 0
        message('The veil of darkness lifts.', libtcod.sky)

def use_potion_see_invisible():
    message('This potion taste like slime juice.', libtcod.sky)
    player.fighter.cansee_timer = 850
    cancel_blind()

def use_potion_healing():
    message('You begin to feel better.', libtcod.sky)
    heal_plus = roll(str(player.fighter.lvl)+'D4')
    if player.fighter.hp + heal_plus > player.fighter.max_hp: 
        player.fighter.max_hp += 1 
    player.fighter.heal(heal_plus)
    cancel_blind()

def use_potion_monster_detection():
    global fov_recompute
    fov_recompute = True
    message('You begin to sense the presence of monsters.', libtcod.sky)
    player.fighter.sense_monsters = True

def use_potion_magic_detection():
    global fov_recompute
    fov_recompute = True
    message('You sense the presence of magic on the level.', libtcod.sky)
    player.fighter.sense_magics = True

def use_potion_raise_level():
    message('You feel suddenly feel much more skillful.', libtcod.sky)
    player.fighter.xp = lvl_to_xp(player.fighter.lvl+1) + 1
    check_level_up()

def use_potion_extra_healing():
    message('You begin to feel much better.', libtcod.sky)
    heal_plus = roll(str(player.fighter.lvl)+'D8')
    if player.fighter.hp + heal_plus > player.fighter.max_hp: 
        player.fighter.max_hp += 1 
    player.fighter.heal(heal_plus)
    cancel_blind()

def use_potion_haste_self():
    message('You feel yourself moving much faster.', libtcod.sky)
    player.fighter.haste_timer += 100

def use_potion_restore_strength():
    message('Hey, this tastes great. It make you feel warm all over.', libtcod.sky)
    player.fighter.st = player.fighter.biggest_st

def use_potion_blindness():
    global fov_recompute
    fov_recompute = True
    message('A cloak of darkness falls around you.', libtcod.sky)
    player.fighter.blind_timer += 200

def use_potion_nop():
    message('This potion tastes extreamly dull.', libtcod.sky)

def equip_ring_see_invisible():
    global fov_recompute
    fov_recompute = True
    player.fighter.cansee_timer = 850
    player.fighter.blind_timer = 0
    r = room_at(*xy(player))
    if r:
        undark_room(r)

def dequip_ring_see_invisible():
    global fov_recompute
    fov_recompute = True
    player.fighter.cansee_timer = 0
    r = room_at(*xy(player))
    if r:
        undark_room(r)

def equip_ring_aggravate_monster():
    for o in objects:
        if o != player and o.fighter:
            o.active = True

def use_stick_light():
    global fov_recompute
    fov_recompute = True
    r = room_at(*xy(player))
    if r == None:
        message('The corridor glows and then fades.', color_stick)
        return
    undark_room(r)
    message('The room is lit by a shimmering blue light.', color_stick)

def use_stick_striking():
    message('Which direction? or ESC to cancel.',color_stick)
    dx,dy = target_direction()
    if dx is None:
        message("Canceled",color_stick)
        return 'canceled'
    x,y = player.x+dx,player.y+dy
    monster = monster_at(x,y)
    if not monster:
        message("Missed swing",color_stick)
        return
    if random.randint(1,20)==1:
        dmg,dplus = '3D8',9
    else:
        dmg,dplus = '1D8',3
    weapon=Equipment(dmg=dmg,dmg_plus=dplus)
    Object(0,0,'','',libtcod.white,item=Item(),equipment=weapon)
    player.fighter.attack_by_slashing(monster,weapon)

def use_stick_hit(name):
    message('Which direction? or ESC to cancel.',color_stick)
    dx,dy = target_direction()
    if dx is None:
        message("Canceled",color_stick)
        return 'canceled'
    projectile=Equipment(hurl_dmg='6D6',launch_dmg='6D6',dmg_plus=100)
    obj = Object(0,0,'/',name,color_stick,item=Item(),equipment=projectile)
    x,y = projectile_motion(obj,dx,dy)
    obj.clear()
    monster = monster_at(x,y)
    if not monster:
        message("You missed the target.",color_stick)
        return
    if mimic_check(monster):
        message('The '+name+' whizzes past the mimic.',color_stick)
        monster.active = True
        return
    if roll('1D20') > 17 - monster.fighter.lvl / 2:
        message('The '+ name +' whizzes past the '+monster.name+'.', color_stick)
        return
    player.fighter.attack_by_throwing(monster,None,projectile)

def use_stick_lightning():
    return use_stick_hit('bolt')

def use_stick_fire():
    return use_stick_hit('fire')

def use_stick_cold():
    return use_stick_hit('ice')

def use_stick_polymorph():
    message('Which direction? or ESC to cancel.',color_stick)
    dx,dy = target_direction()
    if dx is None:
        message("Canceled",color_stick)
        return 'canceled'
    obj = Object(0,0,'/','',color_stick)
    x,y = projectile_motion(obj,dx,dy)
    obj.clear()
    monster = monster_at(x,y)
    if not monster:
        message("You missed the target.",color_stick)
        return
    new_monster = generate_monster(random_select_monster(),*xy(monster))
    new_monster.active = True
    message(monster.name + ' is polymorphed to '+new_monster.name, color_stick)
    objects.append(new_monster)
    monster.clear()
    objects.remove(monster)

def use_stick_magic_missile():
    message('Which direction? or ESC to cancel.',color_stick)
    dx,dy = target_direction()
    if dx is None:
        message("Canceled",color_stick)
        return 'canceled'
    projectile = Equipment(hurl_dmg='1D4',launch_dmg='1D4',dmg_plus=100)
    obj = Object(0,0,'*','missile',color_stick,item=Item(),equipment=projectile)
    x,y = projectile_motion(obj,dx,dy)
    obj.clear()
    monster = monster_at(x,y)
    if not monster:
        message("You missed the target.",color_stick)
        return
    if roll('1D20') > 17 - monster.fighter.lvl / 2:
        message('The missile vanishes with a puff of smoke.',color_stick)
        return
    player.fighter.attack_by_throwing(monster,None,projectile)

def use_stick_haste_monster():
    message('Which direction? or ESC to cancel.',color_stick)
    dx,dy = target_direction()
    if dx is None:
        message("Canceled",color_stick)
        return 'canceled'
    obj = Object(0,0,'/','',color_stick)
    x,y = projectile_motion(obj,dx,dy)
    obj.clear()
    monster = monster_at(x,y)
    if not monster:
        message("You missed the target.",color_stick)
        return
    monster.fighter.slow = False
    monster.fighter.haste = True
    monster.active = True
    message(monster.name + ' is made haste.', color_stick)

def use_stick_slow_monster():
    message('Which direction? or ESC to cancel.',color_stick)
    dx,dy = target_direction()
    if dx is None:
        message("Canceled",color_stick)
        return 'canceled'
    obj = Object(0,0,'/','',color_stick)
    x,y = projectile_motion(obj,dx,dy)
    obj.clear()
    monster = monster_at(x,y)
    if not monster:
        message("You missed the target.",color_stick)
        return
    monster.fighter.slow = True
    monster.fighter.haste = False
    monster.active = True
    message(monster.name + ' is made slow.', color_stick)

def use_stick_drain_life():
    if player.fighter.hp <= 2:
        message('You are too weak to use it.', color_stick)
        return 'canceled'
    rp = room_at(*xy(player))
    area = rp and region(rp.x1,rp.y1,rp.x2,rp.y2) or neighborhood(*xy(player))
    monsters = [o for o in objects if o != player and o.fighter and xy(o) in area]
    if not len(monsters):
        message('You have a tingling feeling.', color_stick)
        return 'canceled'
    player.fighter.take_damage(player.fighter.hp/2,monsters[0])
    damage = int(math.ceil(player.fighter.hp / float(len(monsters))))
    for m in monsters:
        m.fighter.take_damage(damage,player)

def use_stick_nothing():
    message('Nothing happens.', color_stick)

def use_stick_teleport_away():
    message('Which direction? or ESC to cancel.',color_stick)
    dx,dy = target_direction()
    if dx is None:
        message("Canceled",color_stick)
        return 'canceled'
    obj = Object(0,0,'/','',color_stick)
    x,y = projectile_motion(obj,dx,dy)
    obj.clear()
    monster = monster_at(x,y)
    if not monster:
        message("You missed the target.",color_stick)
        return
    monster.active = True
    while True:
        x,y = get_random_pos(random.choice(not_gone_rooms))
        if not is_blocked(x, y):
            break
    monster.clear()
    monster.move(x-monster.x,y-monster.y)
    message(monster.name + ' is teleported away.', color_stick)

def use_stick_teleport_to():
    message('Which direction? or ESC to cancel.',color_stick)
    dx,dy = target_direction()
    if dx is None:
        message("Canceled",color_stick)
        return 'canceled'
    obj = Object(0,0,'/','',color_stick)
    x,y = projectile_motion(obj,dx,dy)
    obj.clear()
    monster = monster_at(x,y)
    if not monster:
        message("You missed the target.",color_stick)
        return
    x,y = next(((x,y) for (x,y) in neighborhood(*xy(player)) if not is_blocked_monsters(x,y)),(None,None))
    if not x:
        message(monster.name + ' couldn\'t get close to you.', color_stick)
        return
    monster.active = True
    monster.clear()
    monster.move(x-monster.x,y-monster.y)
    message(monster.name + ' gets next to you.', color_stick)

def use_stick_cancellation():
    message('Which direction? or ESC to cancel.',color_stick)
    dx,dy = target_direction()
    if dx is None:
        message("Canceled",color_stick)
        return 'canceled'
    obj = Object(0,0,'/','',color_stick)
    x,y = projectile_motion(obj,dx,dy)
    obj.clear()
    monster = monster_at(x,y)
    if not monster:
        message("You missed the target.",color_stick)
        return
    monster.fighter.cancel = True
    message(monster.name + ' losts its special abilities.', color_stick)

def reveal_magic_item_name(name,type):
    magic_item = magic_item_dict[type][name]
    if magic_item.fake_name != None:
        for o in itertools.chain(objects,inventory):
            if o.name == magic_item.fake_name and o.type == type:
                o.name = name
        magic_item.fake_name = None

class MagicItemUseFunction:
    def __init__(self,name,type,use_function):
        self.name=name
        self.type=type
        self.use_function = use_function
    def __call__(self):
        #using a magic item, its real name shows
        reveal_magic_item_name(self.name,self.type)
        #use it
        return self.use_function()

class MagicItemInfo:
    def __init__(self,type,name,chance,gold,use_function):
        self.type=type
        self.chance=chance
        self.gold=gold
        self.use_function = MagicItemUseFunction(name,type,use_function)
        self.fake_name = None

scroll_dict = OrderedDict([(i[0],MagicItemInfo('scroll',*i)) for i in [
#[name,chance,gold,use_function]
['monster confusion',0.08,170,use_scroll_confuse],
['magic mapping',0.05,180,use_scroll_map],
['light',0.10,100,use_scroll_light],
['hold monster',0.02,200,use_scroll_hold],
['sleep',0.05,50,use_scroll_sleep],
['enchant armor',0.08,130,use_scroll_armor],
['identify',0.21,100,use_scroll_ident],
['scare monster',0.04,180,use_scroll_scare],
['gold detection',0.04,110,use_scroll_gfind],
['teleportation',0.07,175,use_scroll_telep],
['enchant weapon',0.10,150,use_scroll_weapon],
['create monster',0.05,75,use_scroll_create],
['remove curse',0.08,105,use_scroll_remove],
['aggravate monsters',0.01,60,use_scroll_aggr],
['blank paper',0.01,50,use_scroll_nop],
['genocide',0.01,200,use_scroll_genocide]]])

potion_dict = OrderedDict([(i[0],MagicItemInfo('potion',*i)) for i in [
#[name,chance,gold,use_function]
['confusion',0.08,50,use_potion_confusion],
['paralysis',0.1,50,use_potion_paralysis],
['poison',0.08,50,use_potion_poison],
['gain strength',0.15,150,use_potion_gain_strength],
['see invisible',0.02,170,use_potion_see_invisible],
['healing',0.15,130,use_potion_healing],
['monster detection',0.06,120,use_potion_monster_detection],
['magic detection',0.06,105,use_potion_magic_detection],
['raise level',0.02,220,use_potion_raise_level],
['extra healing',0.05,180,use_potion_extra_healing],
['haste self',0.04,200,use_potion_haste_self],
['restore strength',0.14,120,use_potion_restore_strength],
['blindness',0.04,50,use_potion_blindness],
['thirst quenching',0.01,50,use_potion_nop]]])

class RingInfo:
    def __init__(self,name,chance,gold,equip_function,dequip_function):
        self.type='ring'
        self.chance=chance
        self.gold=gold
        self.equip_function = MagicItemUseFunction(name,self.type,equip_function)
        self.dequip_function = dequip_function
        self.fake_name = None

ring_dict = OrderedDict([(i[0],RingInfo(*i)) for i in [
#[name,chance,equip_function,dequip_function]
['protection', 0.09,200,noop,noop],
['add strength', 0.09,200,noop,noop],
['sustain strength', 0.05,180,noop,noop],
['searching', 0.10,200,noop,noop],
['see invisible', 0.10,175,equip_ring_see_invisible,dequip_ring_see_invisible],
['adornment', 0.01,100,noop,noop],
['aggravate monster', 0.11,100,equip_ring_aggravate_monster,noop],
['dexterity', 0.08,220,noop,noop],
['increase damage', 0.08,220,noop,noop],
['regeneration', 0.04,260,noop,noop],
['slow digestion', 0.09,240,noop,noop],
['teleportation', 0.09,100,noop,noop],
['stealth', 0.07,100,noop,noop]]])

stick_dict = OrderedDict([(i[0],MagicItemInfo('stick',*i)) for i in [
#[name,chance,use_function]
['light',0.12,120,use_stick_light],
['striking',0.09,115,use_stick_striking],
['lightning',0.03,200,use_stick_lightning],
['fire',0.03,200,use_stick_fire],
['cold',0.03,200,use_stick_cold],
['polymorph',0.15,210,use_stick_polymorph],
['magic missile',0.10,170,use_stick_magic_missile],
['haste monster',0.09,50,use_stick_haste_monster],
['slow monster',0.11,220,use_stick_slow_monster],
['drain life',0.09,210,use_stick_drain_life],
['nothing',0.01,70,use_stick_nothing],
['teleport away',0.05,140,use_stick_teleport_away],
['teleport to',0.05,60,use_stick_teleport_to],
['cancellation',0.05,190,use_stick_cancellation]]])

magic_item_dict = {
'scroll':scroll_dict,
'potion':potion_dict,
'stick':stick_dict,
'ring':ring_dict}

magic_types = list(magic_item_dict.keys())

def generate_scroll(name,x=0,y=0):
    #name='monster confusion'#test
    #create a scroll
    scroll = scroll_dict[name]
    item_component = Item(use_function=scroll.use_function,true_name=name)
    blocks = 0
    if name == 'scare monster':
        blocks = 2
    return Object(x, y, '?', scroll.fake_name or name, color_scroll, type='scroll', blocks=blocks, item=item_component)

def generate_potion(name,x=0,y=0):
    #name='paralysis'#test
    #create a potion
    potion = potion_dict[name]
    item_component = Item(use_function=potion.use_function,true_name=name)
    return Object(x, y, '!', potion.fake_name or name, color_potion, type='potion', item=item_component)

def generate_ring(name,x=0,y=0):
    #name='teleportation'#test
    cursed = False
    ac = 0
    if name=='protection':
        ac = random.choice([-1,1,2])
        cursed = (ac == -1)
    st = 0
    if name=='add strength':
        st = random.choice([-1,1,2])
        cursed = (st == -1)
    if name=='aggravate monster':
        cursed = True
    hplus=0
    if name=='dexterity':
        hplus = random.choice([-1,1,2])
        cursed = (hplus == -1)
    dplus=0
    if name=='increase damage':
        dplus = random.choice([-1,1,2])
        cursed = (dplus == -1)
    if name=='teleportation':
        cursed = True
    ring = ring_dict[name]
    item = Item(true_name=name)
    equipment = Equipment(ac=ac,st=st,hit_plus=hplus,dmg_plus=dplus,cursed=cursed,
                            equip_function=ring.equip_function,
                            dequip_function=ring.dequip_function)
    return Object(x, y, '=', ring.fake_name, color_ring, type='ring', equipment=equipment,item=item)

def generate_stick(name,x=0,y=0):
    #name='lightning'#test
    stick = stick_dict[name]
    charges = random.randint(3,7)
    if name == 'light':
        charges = random.randint(10,19)
    item = Item(charges=charges,type=stick.type,
                use_function=stick.use_function,true_name=name)            
    return Object(x, y, '/', stick.fake_name or name, color_stick, type='stick', item=item)

def crypt_name(name):
    nnn = name + ''.join(random.sample(ascii_lower,random.randint(2,5)))
    return ''.join(random.sample(nnn,len(nnn))).strip()

def set_magic_items_fake_names():
    for type in magic_types:
        for name,item in magic_item_dict[type].items():
            item.fake_name = crypt_name(name)

def set_stick_type():
    for stick in stick_dict.values():
        stick.type = random.randint(1,2)==1 and 'wand' or 'staff'


def special_attack_rust_monster(monster):
    armor = get_current_armor()
    if armor and armor.ac < 9:
        armor.ac += 1
        message('Your armor appears to be weaker now. Oh my!')

def special_attack_floating_eye(monster):
    global no_command
    if player.fighter.blind_timer > 0:
        return
    no_command = generate_no_command(random.randint(0,10))
    message('You are transfixed by the gaze of the floating eye.',color_monster)
    
def special_attack_giant_ant(monster):
    if roll('1D20') >= 14 - player.fighter.lvl / 2:
        return
    if next((r for r in get_current_rings() if r.owner.name == 'sustain strength'),None):
        message('A sting momentarily weakens you.',color_monster)
        return
    player.fighter.st = max(3,player.fighter.st - 1)
    message('You feel a sting in your arm and now feel weaker.',color_monster)

def special_attack_wraith(monster):
    if random.randint(1,100) > 15:
        return
    if player.fighter.xp == 0:
        player.fighter.death(monster)
        return
    message('You suddenly feel weaker.',color_monster)
    player.fighter.lvl -= 1
    if player.fighter.lvl < 1:
        player.fighter.lvl = 1
        player.fighter.xp = 0
    else:
        player.fighter.xp = lvl_to_xp(player.fighter.lvl) + 1
    damage = roll('1D10')
    player.fighter.hp -= damage
    player.fighter.max_hp -= damage
    if player.fighter.hp < 1:
        player.fighter.hp = 1
    if player.fighter.max_hp < 1:
        player.fighter.death(monster)

def special_attack_violet_fungi(monster):
    player.fighter.held_timer = 30

def special_attack_leprechaun(monster):
    global purse
    if purse == 0:
        return
    purse -= random.randint(2,52+dungeon_level*10)
    if roll('1D20') < 17 - player.fighter.lvl / 2:
        for _ in range(4):
            purse -= random.randint(2,52+dungeon_level*10)
    purse = max(0,purse)
    message('You purse feels lighter.',color_monster)
    #a leprechaun escapes
    monster.clear()
    objects.remove(monster)

def special_attack_nymph(monster):
    if roll('1D20') >= 17 - player.fighter.lvl / 2:
        return
    magic_items = [obj for obj in inventory if is_magic(obj) and 
                   (not obj.equipment or not obj.equipment.is_equipped)]
    if len(magic_items) == 0:
        return
    target = random.choice(magic_items)
    #steal an item from inventory
    message('She stole '+target.name+'.',color_monster)
    inventory.remove(target)
    #she escapes
    monster.clear()
    objects.remove(monster)



class MonsterInfo:
    def __init__(self,name,xp,lvl,ac,dmg,carry,ai,special_attack):
        self.name,self.xp,self.lvl,self.ac,self.dmg,self.carry,self.ai,self.special_attack = name,xp,lvl,ac,dmg,carry,ai,special_attack

monster_dict = OrderedDict([(i[0],MonsterInfo(*i[1:])) for i in [
#[ch,name,xp,lvl,ac,dmg,carry,ai,special_attack]
['A','giant ant',10,2,3,'1D6',0,MeanMonster,special_attack_giant_ant],
['B','bat',1,1,3,'1D2',0,lambda: ConfusedMonster(0.5),noop],
['C','centaur',15,4,4,'1D6/1D6',0.15,BasicMonster,noop],
['D','dragon',9000,10,-1,'1D8/1D8/3D10',1,BasicMonster,noop],
['E','floating eye',5,1,9,'0D0',0,BasicMonster,special_attack_floating_eye],
['F','violet fungi',85,8,3,'0D0',0,MeanMonster,special_attack_violet_fungi],
['G','gnome',8,1,5,'1D6',0.1,BasicMonster,noop],
['H','hobgoblin',3,1,5,'1D8',0,MeanMonster,noop],
['I','invisible stalker',2,1,7,'1D2',0,InvisibleStalker,noop],
['J','jackal',2,1,7,'1D2',0,MeanMonster,noop],
['K','kobold',1,1,7,'1D4',0,MeanMonster,noop],
['L','leprechaun',10,3,8,'1D1',0,BasicMonster,special_attack_leprechaun],
['M','mimic',140,7,7,'3D4',0.3,Mimic,noop],
['N','nymph',40,3,9,'0D0',1,BasicMonster,special_attack_nymph],
['O','orc',5,1,6,'1D8',0.15,BasicMonster,noop],
['P','purple worm',7000,15,6,'2D12/2D4',0.7,BasicMonster,noop],
['Q','quasit',35,3,2,'1D2/1D2/1D4',0.3,MeanMonster,noop],
['R','rust monster',25,5,2,'0D0/0D0',0,MeanMonster,special_attack_rust_monster],
['S','snake',3,1,5,'1D3',0,MeanMonster,noop],
['T','troll',55,6,4,'1D8/1D8/2D6',0.5,MeanMonster,noop],
['U','umber hulk',130,8,2,'3D4/3D4/2D5',0.4,MeanMonster,noop],
['V','vampire',380,8,1,'1D10',0.2,MeanMonster,noop],
['W','wraith',55,5,4,'1D6',0,BasicMonster,special_attack_wraith],
['X','xorn',120,7,-2,'1D3/1D3/1D3/4d6',0,MeanMonster,noop],
['Y','yeti',50,4,6,'1D6/1D6',0.3,BasicMonster,noop],
['Z','zombie',7,2,8,'1D8',0,MeanMonster,noop]]])

mimic_types=['gold','food','potion','scroll','weapon','armor','ring','stick','amulet']

def generate_monster(ch,x=0,y=0):
    #ch = 'T'#test
    active = False
    if next((r for r in get_current_rings() if r.owner.name == 'aggravate monster'),None):
        active = True
    monster = monster_dict[ch]
    carry = None
    if random.random() < monster.carry:
        carry = create_object(weighted_random_choice(list(item_dict.keys()),list(item_dict.values())))
    fighter = Fighter(hp=roll(str(monster.lvl)+'D8'), ac=monster.ac, st=10, 
                                xp=monster.xp, lvl=monster.lvl, dmg=monster.dmg,
                                actions=MonsterActions,
                                special_attack=monster.special_attack,
                                carry=carry)
    color = color_monster
    name = monster.name
    if ch=='M':
        if carry and carry.ch in mimic_types:
            ch,color,name=carry.ch,carry.color,carry.name
        else:
            obj = create_object(random.choice(mimic_types[:dungeon_level<(AMULET_LEVEL-1) and -1 or None]))
            if hasattr(obj, '__iter__'):
                obj = obj[0]
            ch,color,name = obj.ch,obj.color,display_name(obj)
    return Object(x, y, ch, name, color, type='monster',blocks=1, fighter=fighter, 
                    ai=monster.ai(), active=active)

monster_fatalness = 'KJBSHEAOZGLCRQNYTWFIXUMVDP'

def random_select_monster():
    fatalness = dungeon_level + random.randint(-5,4)
    if fatalness < 0:
        fatalness = random.randint(0,4)
    if fatalness > 25:
        fatalness = random.randint(21,25)
    return monster_fatalness[fatalness]

def place_monsters(room): #place a level monster
    if random.randint(0,100) < 80:
        #choose random spot for this monster
        for i in range(20): # try 20 times
            x,y=get_random_pos(room)
            if not is_blocked_monsters(x, y):
                break
        else:
            return # failed to find a free spot for the monster
        #create a monster
        objects.append(generate_monster(random_select_monster(),x,y))

wandering_monsters = 'KJBSHAOZGCRQYWIXUV'

def generate_wandering_monster():
    while True:
        a = int(math.log(1.0-random.random())/math.log(5.0/6.0)) # do sampling from a geometric distribution
        for i in range(70+a):
            yield
        rp = room_at(*xy(player))
        r = random.choice([r for r in not_gone_rooms if r != rp])
        x,y = random.choice([p for p in region(r.x1+1,r.y1+1,r.x2-1,r.y2-1) if not is_blocked_monsters(*p)])
        #select a wondering monster
        while True:
            ch = random_select_monster()
            if ch in wandering_monsters:
                break
        #create a monster
        monster = generate_monster(ch,x,y)
        monster.active = True
        objects.append(monster)
        yield

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + int(total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                                 name + ': ' + str(value) + '/' + str(maximum))

def get_names_under_mouse():
    global mouse
    #return a string with the names of all objects under the mouse

    (x, y) = (mouse.cx, mouse.cy)

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [display_name(obj) for obj in objects
             if obj.x == x and obj.y == y and map_is_in_fov(obj.x, obj.y)]

    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute

    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        map_compute_fov(player.x, player.y)

        #go through all tiles, and set their background color according to the FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = map_is_in_fov(x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if map[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET )
                    #since it's visible, explore it
                    map[x][y].explored = True

    #draw all objects in the list, except the player. we want it to
    #always appear over all other objects! so it's drawn later.
    for object in objects:
        if object != player:
            object.draw()
    player.draw()

    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

    #GUI
    draw_gui()


def draw_gui():
    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT,line)
        y += 1

    #show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)

    libtcod.console_print_ex(panel, 1, 2, libtcod.BKGND_NONE, libtcod.LEFT, 
        'STR: '+str(get_player_st())+' AC: '+str(get_player_ac()))
    libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 
        'LVL/EXP: '+str(player.fighter.lvl)+'/'+str(player.fighter.xp))
    libtcod.console_print_ex(panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT, 
        'Gold: '+str(purse))
    libtcod.console_print_ex(panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))

    hunger = ['','Hungry','Weak','Fainting'][player.fighter.hunger]
    libtcod.console_print_ex(panel, 1, 6, libtcod.BKGND_NONE, libtcod.LEFT, hunger)

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    libtcod.console_print_ex(panel, 10, 10, libtcod.BKGND_NONE, libtcod.LEFT, "abcdef")
    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)


def message(new_msg, color = libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, removethe first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )


def player_move_or_attack(dx, dy):
    global fov_recompute
    if player.fighter.confusion_timer > 0:
        if random.randint(1,5) > 1:
            dx,dy=random.choice((-1,1)),random.choice((-1,1))

    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy

    #try to find a monster or a trap
    monster = None
    trap = None
    for object in objects:
        if object.x == x and object.y == y:
            if object.fighter:
                monster = object
                break
            if object.type == 'trap':
                trap = object
                break

    #attack or be trapped or move
    if monster:
        player.fighter.attack(monster)
    elif trap:
        player.move(dx, dy)
        be_trapped(trap)
        fov_recompute = True
    else:
        if player.fighter.held_timer == 0:
            player.move(dx, dy)
            fov_recompute = True

def be_trapped(obj):
    global no_command
    obj.ch = '^'
    obj.name = obj.trap.trap_type
    if obj.trap.trap_type == 'trap door':
        message('You fell into a trap!',color_trap)
        next_level('down')
    elif obj.trap.trap_type == 'beartrap':
        message('You are caught in a bear trap.',color_trap)
        player.fighter.held_timer = 30
    elif obj.trap.trap_type == 'sleeping gas trap':
        message('A strange white mist envelops you and you fall a sleep.',color_trap)
        no_command = generate_no_command(30)
    elif obj.trap.trap_type == 'arrow trap':
        hit = random.randint(2,21)
        need = 21 - (player.fighter.lvl - 1) - get_player_ac()
        if hit >= need:
            message('Oh no! An arrow shoot you.',color_trap)
            player.fighter.take_damage(roll('1D6'),Object(0,0,'','arrow trap',libtcod.white))
        else:
            message('An arrow shoots past you.',color_trap)
    elif obj.trap.trap_type == 'teleport trap':
        teleport()
    elif obj.trap.trap_type == 'dart trap':
        hit = random.randint(2,21)
        need = 21 - (player.fighter.lvl + 1) - get_player_ac()
        if hit >= need:
            message('A small dart just hit you in the shoulder.',color_trap)
            player.fighter.take_damage(roll('1D4'),Object(0,0,'','dart trap',libtcod.white))
            if player.fighter.hp > 0 and \
                    not next((r for r in get_current_rings() if r.owner.name == 'sustain strength'),None):
                player.fighter.st = max(0,player.fighter.st - 1)
        else:
            message('A small dart whizzes by your ear and vanishes.',color_trap)


def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, int(x), int(y), 1.0, 0.7)
    #debug to ignore pressing shift,alt...
    while True:
        #present the root console to the player and wait for a key-press
        libtcod.console_flush()
        key = libtcod.console_wait_for_keypress(True)
        if key.vk == libtcod.KEY_CHAR or key.vk == libtcod.KEY_ESCAPE:
            break
    #debug, to clear KEY_TEXT event
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, libtcod.Key(), libtcod.Mouse())

    #debug console_wait_for_keypress() can't take a key combination.
    #if key.vk == libtcod.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
    #    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen)

    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def clear_menu():
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

def space_in_inventory(name,type):
    lst=inventory_list()
    if name in ('food','arrow','rock','dart','crossbow bolt') or \
            type in ('potion','scroll','ring','stick'):
        if next((o for o,n in lst if o.name == name and 
                    not(o.equipment and o.equipment.is_equipped)),None):
            return True
    return len(lst) < 26

def inventory_list():
    nums = [1 for i in inventory]
    def groupby(name):
        g = [i for i,obj in enumerate(inventory) 
                if obj.name == name and not (obj.equipment and obj.equipment.is_equipped)]
        if g != []:
            nums[g[0]] = len(g)
            for i in g[1:]:
                nums[i] = 0
    for name in ('food','arrow','rock','dart','crossbow bolt'):
        groupby(name)
    for name in list(set([o.name for o in inventory 
                            if o.type in ('scroll','potion','ring','stick')])):
        groupby(name)
    lst = [(inventory[i],n) for i,n in enumerate(nums) if n != 0]
    lst.sort(key=lambda v:0 if v[0].name=='food' else 1)
    return lst

def inventory_menu(header):
    lst = inventory_list()
    #show a menu with each item of the inventory as an option
    if len(lst) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for obj,n in lst:
            text = ''
            if n > 1:
                text = str(n) + ' '
            text += display_name(obj)
            #show additional information, when it's equipped
            if obj.equipment and obj.equipment.is_equipped:
                text += ' (' + obj.equipment.slot + ')'
            if obj.type == 'stick':
                text += ' (' + str(obj.item.charges) + ')'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(lst) == 0: return None
    return lst[index][0].item

def weapon_menu():
    header = 'Press the key next to an item to throw it, or any other to cancel.\n'
    weapons = [(obj,n) for obj,n in inventory_list() if obj.type=='weapon' and not obj.equipment.is_equipped]
    #show a menu of weapons
    if len(weapons) == 0:
        menu(header, ['No weapons to throw.'], INVENTORY_WIDTH)
        return None
    def option(o,n):
        if n == 1:
            return o.name
        return str(n) + ' ' + o.name
    index = menu(header, [option(o,n)  for o,n in weapons], INVENTORY_WIDTH)
    if index is None: 
        return None
    return weapons[index][0].equipment

def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"

delta_xy_dict = {
libtcod.KEY_UP:(0,-1),
libtcod.KEY_KP8:(0,-1),
libtcod.KEY_DOWN:(0,1),
libtcod.KEY_KP2:(0,1),
libtcod.KEY_LEFT:(-1,0),
libtcod.KEY_KP4:(-1,0),
libtcod.KEY_RIGHT:(1,0),
libtcod.KEY_KP6:(1,0),
libtcod.KEY_HOME:(-1,-1),
libtcod.KEY_KP7:(-1,-1),
libtcod.KEY_PAGEUP:(1,-1),
libtcod.KEY_KP9:(1,-1),
libtcod.KEY_END:(-1,1),
libtcod.KEY_KP1:(-1,1),
libtcod.KEY_PAGEDOWN:(1,1),
libtcod.KEY_KP3:(1,1),
libtcod.KEY_SPACE:(0,0),
libtcod.KEY_KP5:(0,0),
'y':(-1,-1),
'k':(0,-1),
'u':(1,-1),
'h':(-1,0),
'l':(1,0),
'b':(-1,1),
'j':(0,1),
'n':(1,1)
}

def handle_keys():
    global key
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game

    if game_state != 'playing':
        return

    #test for other keys
    #debuged
    #(memo)With Japanese keyboards, '<' is assigned to SHIFT+',' then it can't be get at KEY_CHAR event
    #(memo)On a key press, both KEY_CHAR event and KEY_TEXT event occure  
    #key_char = chr(key.c)
    if key.vk==libtcod.KEY_TEXT:
        key_char = chr(key.text[0])
    else:
        key_char = 0

    if no_command != None and key_char != 'i':
        return

    #handle movement keys
    delta_xy = delta_xy_dict.get(key.vk,None) or delta_xy_dict.get(key_char,None)
    if delta_xy:
        if delta_xy != (0,0): # (0,0) means waiting for the monsters
            player_move_or_attack(*delta_xy)
        return

    #handle command keys
    if key_char == 'g':
        #pick up an item or gold
        for object in objects:  #look for an item in the player's tile
            if object.x == player.x and object.y == player.y:
                if object.item:
                    object.item.pick_up()
                    break
                if object.gold:
                    object.gold.pick_up()
                    break
        return 'didnt-take-turn'

    if key_char == 'i':
        #show the inventory; if an item is selected, use it
        chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
        if chosen_item is not None:
            if chosen_item.use() != 'canceled':
                return
        return 'didnt-take-turn'

    if key_char == 'd':
        #show the inventory; if an item is selected, drop it
        chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
        if chosen_item is not None:
            chosen_item.drop()
        return 'didnt-take-turn'

    if key_char == 'c':
        #show character information
        weapon = get_current_weapon()
        weapon_info = ''
        if weapon != None:
            weapon_info = weapon.owner.name + ' h+:' + str(weapon.hit_plus) + ' d+:' +  \
                            str(weapon.dmg_plus) + ' ' +(weapon.cursed and 'cursed' or '')
        armor = get_current_armor()
        armor_info = ''
        if armor != None:
            armor_info = armor.owner.name+' ac:'+str(armor.ac)+' '+ (armor.cursed and 'cursed' or '')

        def get_ring_info(ring):
            return '\nRing: ' + ring.owner.name + \
                    (ring.ac and ' ac:'+str(ring.ac) or '') + \
                    (ring.st and ' st:'+str(ring.st) or '') + \
                    (ring.hit_plus and ' h+:'+str(ring.hit_plus) or '') + \
                    (ring.dmg_plus and ' d+:'+str(ring.dmg_plus) or '') + \
                    (ring.cursed and ' cursed' or '')
        ring_info = ''.join([get_ring_info(r) for r in get_current_rings()])

        msgbox('Character Information\n\nLevel: ' + str(player.fighter.lvl) + 
                '\nExperience: ' + str(player.fighter.xp) +
                '\nExperience to level up: ' + str(lvl_to_xp(player.fighter.lvl+1)) + 
                '\nGold: ' + str(purse) + 
                '\n\nMaximum HP: ' + str(player.fighter.max_hp) +
                '\nWeapon: ' + weapon_info +
                '\nArmor: ' + armor_info +
                ring_info,
                CHARACTER_SCREEN_WIDTH)
        return 'didnt-take-turn'

    if key_char == '>': #down
        #go down stairs, if the player is on them
        if stairs.x == player.x and stairs.y == player.y:
            next_level('down')
        return 'didnt-take-turn'

    if key_char == '<': #up
        if have_amulet() and stairs.x == player.x and stairs.y == player.y:
            next_level('up')
        else:
            message('I see no way up.')
        return 'didnt-take-turn'

    if key_char == 't':
        weapon = weapon_menu()
        if weapon is not None:
            message('Which direction? or ESC to cancel.')
            dx,dy = target_direction()
            if dx is not None:
                player.fighter.throw(weapon,dx,dy)
                return
        message("Canceled")
        return 'didnt-take-turn'

    if key_char == 's':
        search()
        return 'didnt-take-turn'

    #test save
    if key_char == 'S':
        save_game('test_save_game')
        return 'didnt-take-turn'

    #test load
    if key_char == 'L':
        load_game('test_save_game')
        return 'didnt-take-turn'

    # any key is not pressed
    return 'didnt-take-turn'

def search():
    global fov_recompute
    fov_recompute = True
    neighbor_area = neighborhood(*xy(player))
    for o in [o for o in objects if (o.x,o.y) in neighbor_area]:
        if o.name == 'secret door':
            map[o.x][o.y].blocked = False
            map[o.x][o.y].block_sight = False
            o.clear()
            objects.remove(o)    
        elif o.type == 'trap':
            if o.ch != '^':
                o.ch = '^'
                o.name = 'trap'
                if random.randint(1,2)==1:
                    o.name = o.trap.trap_type
                    message(o.name)

def xp_to_lvl(xp):
    return int(math.log(xp * 0.1) / math.log(2.0) + 1.0)

def lvl_to_xp(lvl):
    return int(10.0 * math.pow(2,lvl-1))

def check_level_up():
    if player.fighter.xp == 0:
        new_lvl = 0
    else:
        new_lvl = xp_to_lvl(player.fighter.xp)
    if new_lvl > player.fighter.lvl:
        add_hp = roll(str(new_lvl - player.fighter.lvl)+'D10')
        player.fighter.max_hp += add_hp
        player.fighter.hp = min(player.fighter.hp+add_hp,player.fighter.max_hp)
        player.fighter.lvl = new_lvl
        message('Your battle skills grow stronger! You reached level ' + str(player.fighter.lvl) + '!', libtcod.yellow)
        
def target_direction():
    #return the target direction or (None,None) if cancelled.
    global key,mouse
    while True:
        #get the key pressed
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        #render the screen to erase the inventory menu and 
        #to show the name of the object under the mouse.
        render_all()

        key_char = (key.vk==libtcod.KEY_TEXT and key.text[0]) or 0
        delta_xy = delta_xy_dict.get(key.vk,None) or delta_xy_dict.get(key_char,None)

        if delta_xy:
            if delta_xy == (0,0):
                continue
            return delta_xy
        elif key.vk == libtcod.KEY_ESCAPE:
            return (None, None)

def projectile_motion(obj,dx,dy):
    obj.x = player.x
    obj.y = player.y
    #move the projectile and show the animation
    while True:
        x = obj.x + dx
        y = obj.y + dy
        if is_blocked(x,y):
            return (x,y)
        obj.clear()
        obj.x = x
        obj.y = y
        obj.draw()
        render_all()
        libtcod.console_flush()
        time.sleep(0.01)

def monster_at(x,y):
    return next((o for o in objects if o.x==x and o.y==y and (o.ch >= 'A' and o.ch <= 'Z')),None)

def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range

    for object in objects:
        if object.fighter and not object == player and map_is_in_fov(object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def save_game(fname='savegame'):
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open(fname, 'n')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player)  #index of player in objects list
    file['stairs_index'] = objects.index(stairs)  #same for the stairs
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['dungeon_level'] = dungeon_level
    file['max_dungeon_level'] = max_dungeon_level
    file['rooms'] = rooms
    file['not_gone_rooms'] = not_gone_rooms
    file['scroll_dict'] = scroll_dict
    file['potion_dict'] = potion_dict
    file['ring_dict'] = ring_dict
    file['stick_dict'] = stick_dict
    file['purse'] = purse
    file['fungi_hit'] = fungi_hit
    file['user_name'] = user_name
    file['killer_monster_name'] = killer_monster_name
    file['end_date'] = end_date
    file.close()

def load_game(fname='savegame'):
    #open the previously saved shelve and load the game data
    global map, objects, player, stairs, inventory, game_msgs, game_state
    global dungeon_level, max_dungeon_level
    global rooms,not_gone_rooms,wandering_monster_generator
    global scroll_dict,potion_dict,ring_dict,stick_dict,magic_item_dict,purse,fungi_hit
    global user_name,killer_monster_name,end_date

    file = shelve.open(fname, 'r')

    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  #get index of player in objects list and access it
    stairs = objects[file['stairs_index']]  #same for the stairs
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    dungeon_level = file['dungeon_level']
    max_dungeon_level = file['max_dungeon_level']
    rooms = file['rooms']
    not_gone_rooms = file['not_gone_rooms']
    scroll_dict = file['scroll_dict']
    potion_dict = file['potion_dict']
    ring_dict = file['ring_dict']
    stick_dict = file['stick_dict']
    #As a feature of the shelve module, file['magic_item_dict'] returns the copy of the magic_item_dict.
    #Maybe it's a deep copy. I need the items in the magic_item_dict to be a reference to the scroll_dict, ...
    #Then the magic_item_dict have to be recreated not to be saved and loaded using the shelve.
    magic_item_dict = {
        'scroll':scroll_dict,
        'potion':potion_dict,
        'stick':stick_dict,
        'ring':ring_dict}
    purse = file['purse']
    fungi_hit = file['fungi_hit']
    user_name = file['user_name']
    killer_monster_name = file['killer_monster_name']
    end_date = file['end_date']
    file.close()
    wandering_monster_generator = generate_wandering_monster()
    initialize_fov()

ascii_lower ='abcdefghijklmnopqrstuvwxyz'

def new_game():
    global player, inventory, purse, game_msgs, game_state, dungeon_level
    global max_dungeon_level,wandering_monster_generator, no_command
    global user_name,killer_monster_name,end_date

    user_name = None
    killer_monster_name = None
    end_date = None

    #reset no_command
    no_command = None

    #set magic items fake names
    set_magic_items_fake_names()

    #set whether a stick is a wand or a staff
    set_stick_type()

    #create object representing the player
    st = weighted_random_choice([16,19,20,21],[0.99,0.0075,0.0015,0.001])

    fighter_component = Fighter(hp=12, ac=10, st=st, xp=0, lvl=1, dmg='1D4',actions=PlayerActions)
    player = Object(0, 0, '@', 'player', libtcod.white, type='player', blocks=1, fighter=fighter_component)

    #player.fighter.lvl = 7#test
    #player.fighter.xp = lvl_to_xp(player.fighter.lvl)#test
    #player.fighter.hp = 30#test
    #player.fighter.max_hp = 30#test
    #player.fighter.st = 21#test

    #player.fighter.hp = 2#test
    #player.fighter.max_hp =2#test

    #player.fighter.confusion_timer=10#test
    #player.fighter.blind_timer = 500#test
    #player.fighter.haste_timer = 100#test

    inventory = []

    #generate map (at this point it's not drawn to the screen)
    dungeon_level = 1
    max_dungeon_level = 1
    #dungeon_level=7#test
    #max_dungeon_level=7#test
    make_map()
    initialize_fov()

    wandering_monster_generator = generate_wandering_monster()
    
    game_state = 'playing'

    purse = 0

    #create the list of game messages and their colors, starts empty
    game_msgs = []

    #a warm welcoming message!
    message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)

    #initial food
    obj = generate_food()
    inventory.append(obj)
    obj.always_visible = True

    #initial equipment: a mace
    obj = generate_weapon('mace')
    obj.equipment.cursed = False
    obj.always_visible = True
    inventory.append(obj)
    obj.equipment.equip()

    #initial equipment: arrows
    for i in range(random.randint(25,39)):
        obj = generate_weapon('arrow')
        obj.equipment.cursed = False
        obj.always_visible = True
        inventory.append(obj)

    #initial equipment: a ring  mail
    obj = generate_armor('ring mail')
    obj.always_visible = True
    obj.equipment.cursed = False
    inventory.append(obj)
    obj.equipment.equip()

    #test potion
    #for i in range(10):
    #    obj = generate_potion('paralysis')
    #    inventory.append(obj)
    #    obj.always_visible = True

    #test scroll
    #obj = generate_scroll('remove curse')
    #inventory.append(obj)
    #obj.always_visible = True

    #test ring
    #ring_name = 'searching'
    #obj = generate_ring(ring_name)
    #inventory.append(obj)
    ###obj.equipment.equip()
    #obj.always_visible = True
    #obj.equipment.cursed = True

    #test stick
    ##obj = generate_stick('lightning')
    #obj = generate_stick('striking')
    #inventory.append(obj)
    #obj.always_visible = True

    #test amulet
    #obj=create_object('amulet')
    #inventory.append(obj)
    #obj.always_visible = True

def next_level(which):#'up' or 'down'
    #advance to the next level
    global dungeon_level,max_dungeon_level,wandering_monster_generator,game_state
    global user_name,end_date,purse
    message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)  #heal the player by 50%
    player.fighter.sense_monsters = False
    player.fighter.sense_magics = False
    if which=='down':
        dungeon_level += 1
        message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    else: #'up'
        dungeon_level -= 1
        message('You feel a wrenching sensation in your gut.', libtcod.red)
        if dungeon_level == 0:
            game_state='you win'
            user_name = get_user_name()
            end_date = datetime.now()
            def reveal_name(dic,typ):
                for name in dic.keys():
                    reveal_magic_item_name(name,typ)
            reveal_name(scroll_dict,'scroll')
            reveal_name(potion_dict,'potion')
            reveal_name(ring_dict,'ring')
            reveal_name(stick_dict,'stick')
            for obj in inventory:
                obj.gold = price(obj)
            purse += sum([o.gold for o in inventory])
            save_game()
            save_score('A total winner')
            return
    make_map()  #create a fresh new level!
    if dungeon_level > max_dungeon_level:
        max_dungeon_level = dungeon_level
    initialize_fov()
    wandering_monster_generator = generate_wandering_monster()

def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True

    #create the FOV map, according to the generated map
    fov_map = [[False for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    libtcod.console_clear(con)  #unexplored areas start black (which is the default background color)
1
def map_is_in_fov(x,y):
    return fov_map[x][y]

def neighborhood(x,y):
    return region(max(0,x-1),max(0,y-1),min(x+1,MAP_WIDTH-1),min(y+1,MAP_HEIGHT-1))

def region(sx,sy,ex,ey):
    return list(itertools.product(range(int(sx),int(ex+1)),range(int(sy),int(ey+1))))

def map_compute_fov(x,y):
    for i,j in region(0,0,MAP_WIDTH-1,MAP_HEIGHT-1):
        fov_map[i][j] = False
        #fov_map[i][j] = True #test

    if player.fighter.blind_timer > 0:
        fov_map[x][y] = True
        return

    for i,j in neighborhood(x,y):
        fov_map[i][j] = True

    r = room_at(x,y)
    if r is not None:
        for i,j in region(r.x1,r.y1,r.x2,r.y2):
            if not map[i][j].dark:
                fov_map[i][j] = True

def is_in_room(r,x,y):
    return r.x1<x<r.x2 and r.y1<y<r.y2

def room_at(x,y):
    return next((r for r in rooms if is_in_room(r,x,y)),None)

def play_game():
    global key, mouse, peace

    player_action = None

    turn_counter = 0

    mouse = libtcod.Mouse()
    key = libtcod.Key()
    #main loop
    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if game_state == 'you died':
            player.color = libtcod.dark_red
            render_all()
            rest_in_peace()
            break

        if game_state == 'you win':
            render_all()
            you_made_it()
            break

        #render the screen
        render_all()

        libtcod.console_flush()

        #level up if needed
        check_level_up()

        peace = True

        player.clear() #clear player before move
        player_action = handle_keys() #handle keys
        if no_command != None:
            player_action = next(no_command)

        #exit game if needed
        if player_action == 'exit':
            save_game()
            break
    
        if player_action != 'didnt-take-turn':
            turn_counter += 1
            turn_counter %= 2

        if game_state == 'playing' and player_action != 'didnt-take-turn':
            #let monsters take their turn
            if player.fighter.haste_timer == 0 or turn_counter == 0:
                for object in objects:
                    if object.ai:
                        if object.fighter.slow:
                            if turn_counter==0:
                                object.clear() #clear monster before move
                                object.ai.take_turn()
                        elif object.fighter.haste:
                            object.clear() #clear monster before move
                            object.ai.take_turn()
                            object.ai.take_turn()
                        else:                        
                            object.clear() #clear monster before move
                            object.ai.take_turn()
                next(wandering_monster_generator)

            #restore player's hit points when peace
            if peace:
                heal_plus = sum([1 for r in get_current_rings() if r.owner.name=='regeneration'])
                if player.fighter.lvl < 8:
                    if random.randint(1,20-player.fighter.lvl*2) == 1:
                        player.fighter.heal(1+heal_plus)
                else:
                    if random.randint(1,3) == 1:
                        player.fighter.heal(random.randint(1,player.fighter.lvl-7)+heal_plus)

            if player.fighter.blind_timer == 0 and \
                    next((r for r in get_current_rings() if r.owner.name == 'searching'),None):
                search()

            if next((r for r in get_current_rings() if r.owner.name == 'teleportation'),None) and random.randint(1,50)==1:
                teleport()

            #use calories
            player.fighter.use_calories()
            #reduce timers
            if player.fighter.confusion_timer > 0:
                player.fighter.confusion_timer -= 1
                if player.fighter.confusion_timer == 0:
                    message('You feel less confused now!')
            if player.fighter.blind_timer > 0:
                player.fighter.blind_timer -= 1
            if player.fighter.cansee_timer > 0:
                player.fighter.cansee_timer -= 1
            if player.fighter.haste_timer > 0:
                player.fighter.haste_timer -= 1
            if player.fighter.held_timer > 0:
                player.fighter.held_timer -= 1

def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, int(SCREEN_WIDTH/2), int(SCREEN_HEIGHT/2-4), libtcod.BKGND_NONE, libtcod.CENTER,
                                 'TOMBS OF THE ANCIENT KINGS')
        libtcod.console_print_ex(0, int(SCREEN_WIDTH/2), int(SCREEN_HEIGHT-2), libtcod.BKGND_NONE, libtcod.CENTER, 'Revised by Masahito3')

        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)

        if choice == 0:  #new game
            new_game()
            play_game()
        if choice == 1:  #load last game
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:  #quit
            break

libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
#libtcod.console_set_custom_font('dejavu_wide12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

main_menu()
