# roguelike

## Overview

This is a roguelike game based on 'Complete Roguelike Tutorial' in RogueBasin.
And the rules, items and monsters are inspired from the rogue version 3.1. 

## Requirement

This program runs only on Python 3 and Linux.

## Usage

python3 ./roguelike.py

## Reference

[Complete Roguelike Tutorial in RogueBasin](https://www.roguebasin.com/index.php/Complete_Roguelike_Tutorial,_using_python%2Blibtcod)
libtcod
rogue version 3.1

## Author

masahito3

## License

I want to follow the original tutorial's license, but I'm not sure what it is.
If possible, I would like to use the MIT license.

## Operations

↑ : move up
↓ : move down
← : move left
→ : move right
keypad 8 : move up
keypad 2 : move down
keypad 4 : move left
keypad 6 : move right
keypad 7 : move up left
HOME     : move up left


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



g : pick up an item from the f
loor
s : search the room tiles and walls neighbering the player
i : show inventory menu
  on the inventory menu
  a..z : press an alphabet before the item name you want to use
  ESC : cancel
d : show drop menu 
  on the drop menu
  a..z : press an alphabet before the item name you want to drop
  ESC : cancel
c : show the player's information
t : show the weapon menu to throw a weapon
  on the weapon menu
  a..z : press an alphabet before the item name you want to throw
  ↑ : throw up
  ↓ : throw down
  → : throw right
  ← : throw left
  ESC : cancel
> : go up stairs
< : go down stairs


### throw weapons
t




## Monsters



## Traps



## Armors


