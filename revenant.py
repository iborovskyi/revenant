#! /usr/bin/env python3
# created by Red Fisher <imagination.fault@gmail.com>;
# lisenced under BSD license;

class Game(object):
    def __init__(self):
        # generic modules
        from random import randrange
        from copy import deepcopy
        self.randrange = randrange
        self.deepcopy = deepcopy
        from os import system
        self.system = system

        # getch
        from getch import _Getch
        self.getch = _Getch()

        # game state flag
        self.flag = 'alive'

        # variables and population
        # 'creature sign': ['name', hp, [min_damage,max_damage], [min_resist,max_resist], coordinates, movement buffer, inventory]
        self.creatures = {'@': ['Revenant', 100, [1,4], [0,1], [], ' ', []], \
                          'B': ['Butcher', 100, [1,4], [8,11], [], ' ', ['C']], \
                          'U': ['Undead warrior', 40, [1,4], [0,1], [], ' ', ['t','/']], \
                          'W': ['Undead warlord', 50, [1,4], [0,1], [], ' ', ['P','s']], \
                          'S': ['Skeleton', 20, [1,4], [0,1], [], ' ', ['/','h']], \
                          'G': ['Giant rat', 10, [1,4], [0,1], [], ' ', []], \
                          'F': ['Feeble skeleton', 5, [1,4], [0,1], [], ' ', ['/']]}
        # items - item: [full name, class (weapon, armor, potion, misc), special (damage/res...)]
        # weapon (w) - [name, type, damage(list for range)]
        # armor (a_b - armor body, a_h - armor head) - [name, type, resistance(list for range)]
        # health potion (hp) - [name, type, health restored (single int)
        self.items = {'d': ['heavy dagger', 'w', [4,6]], \
                      '/': ['rusty sword', 'w', [3,11]], \
                      'P': ['broad axe', 'w', [15,21]], \
                      'C': ["Butcher's cleaver", 'w', [20,31]], \
                      'l': ['charred leather', 'a_b', [0,6]], \
                      't': ['tattered chainmail', 'a_b', [3,11]], \
                      's': ['shabby bearskin over mail', 'a_b', [8,11]], \
                      'm': ['iron mask', 'a_h', [3,6]], \
                      'h': ['old nordic helmet', 'a_h', [4,8]], \
                      'o': ['potion of healing', 'p', 80], \
                      '=': ['gold bar', 'm'], \
                      '*': ['rotting remains', 'p', 20]}
        # loose_items - items that lie on the map
        self.loose_items = ['d', 'l', 'm', 'o', 'o', 'o', 'o', 'o', 'o', '=', '=', '=', '=']
        self.level_settings = self.populator(self.level_creator())            # level map; list of lists; persistent
        self.active_map = self.deepcopy(self.level_settings)             # active level map with objects; list of lists; changeable
        self.sight = []     # tiles, seen to player; list of lists; changeable
        self.messages = []

    def level_creator(self):
        """
        creates random empty level map
        """
        level_map = []
        # max - 80 width; 20 height
        #maxwidth = self.randrange(60, 80)
        #maxheight = self.randrange(15, 20)
        maxwidth = 79
        maxheight = 19
        tile = {0: ' ', 1: '#'}
        cr_h = 0    # counter height
        while cr_h <= maxheight:
            level_string = []
            cr_w = 0    # counter width
            if cr_h == 0 or cr_h == maxheight:  # making up and bottom borders solid
                while cr_w <= maxwidth:
                    level_string.append('#')
                    cr_w += 1
            else:
                while cr_w <= maxwidth:
                    if cr_w == 0 or cr_w == maxwidth:   # making left and right borders solid
                        level_string.append('#')
                    else:
                        # making sure all paths are passable
                        if level_map[-1][cr_w] == ' ' and level_map[-1][cr_w + 1] == '#' or \
                            level_map[-1][cr_w] == ' ' and level_map[-1][cr_w - 1] == '#':
                            level_string.append(' ')
                        else:
                            level_string.append(tile[self.randrange(2)])
                    cr_w += 1
            level_map.append(level_string)
            cr_h += 1

        return(level_map)

    def populator(self, level_map):
        """
        takes level_map (list of lists) from level_creator;
        returns populated map (list of lists)
        """
        populated = self.deepcopy(level_map)
        objs = ['^']
        for el in self.creatures.keys():
            objs.append(el)
        objs += self.loose_items
        for obj in objs:
            placed = False
            while placed != True:
                obj_h_pos = self.randrange(len(level_map))
                obj_w_pos = self.randrange(len(level_map[0]))
                if populated[obj_h_pos][obj_w_pos] == ' ':
                    populated[obj_h_pos][obj_w_pos] = obj
                    placed = True
                    if obj in self.creatures.keys():
                        self.creatures[obj][4] = [obj_h_pos, obj_w_pos]
        return(populated)

    def player_sight_update(self):
        """
        determines visible height range;
        passes height range and -len of active_map to sight_filler
        """
        player_h = self.creatures['@'][4][0]
        self.sight = []
        max_h = len(self.active_map) - 1
        sight_range_h = []

        # top
        if player_h - 3 >= 0:
            sight_range_h.append(player_h - 3)
        else:
            sight_range_h.append(0)
        # bottom
        if player_h + 3 <= max_h:
            sight_range_h.append(player_h+4)
        else:
            sight_range_h.append(len(self.active_map))

        height_range = self.deepcopy(range(sight_range_h[0],sight_range_h[1]))
        self.sight_filler(height_range, -len(self.active_map))

    def sight_filler(self, height_range, map_height):
        """
        fills player sight;
        sight radius is 3 for now
        """
        player_w = self.creatures['@'][4][1]
        sight_line = []
        start_w = 0
        end_w = 0

        # left end
        if player_w - 3 >= 0:
            start_w = player_w - 3
        else:
            start_w = 0
        # right end
        if player_w + 3 <= len(self.active_map[0]) - 1:
            end_w = player_w + 3
        else:
            end_w = len(self.active_map[0]) - 1

        # filling lines
        cr_tile = 0
        for tile in self.active_map[map_height]:
            if (map_height+len(self.active_map)) in height_range:
                if cr_tile in range(start_w, end_w+1):
                    sight_line.append(tile)
                else:
                    sight_line.append(' ')
            else:
                sight_line.append(' ')
            cr_tile += 1
        self.sight = self.sight + [sight_line]
        if map_height < -1:
            self.sight_filler(height_range, map_height+1)

    def deal_damage(self, creature, target):
        """
        game without fighting is dull; fighting without dealing/taking damage is... well, it's not fighting in the first place
        takes two single characters as input
        """
        damage = self.randrange(self.creatures[creature][2][0],self.creatures[creature][2][1])
        for item in self.creatures[creature][6]:
            if self.items[item][1] == 'w':
                damage += self.randrange(self.items[item][2][0],self.items[item][2][1])

        resistance = self.randrange(self.creatures[target][3][0],self.creatures[target][3][1])
        for item in self.creatures[target][6]:
            if self.items[item][1] == 'a_b' or self.items[item][1] == 'a_h':
                resistance += self.randrange(self.items[item][2][0],self.items[item][2][1])

        if self.creatures[creature][1] > 0:
            if damage-resistance >= 0:
                self.creatures[target][1] -= (damage-resistance)
            self.upd_messages(self.creatures[creature][0] + ' attacks ' + self.creatures[target][0] + '! ')
            #self.upd_messages(self.creatures[creature][0] + ' attacks ' + self.creatures[target][0] + '! (' + str(self.creatures[target][1])+','+str(damage)+','+str(resistance)+')')  # for testing
            if self.creatures[target][1] <= 0:
                self.drop(target,'*')
                self.active_map[self.creatures[target][4][0]][self.creatures[target][4][1]] = self.creatures[target][5]
                for item in self.creatures[target][6]:
                    self.drop(target, item)
                self.upd_messages(self.creatures[creature][0] + ' reduces ' + self.creatures[target][0] + ' to a pile of bones. ')

    def pick_up(self):
        '''
        pick up an item that is currently in character's tile buffer (self.creatures['@'][5]);
        '''
        if len(self.creatures['@'][6]) < 4:
            item = self.creatures['@'][5]

            cr_w = 0
            cr_a_b = 0
            cr_a_h = 0
            for el in self.creatures['@'][6]:
                if self.items[el][1] == 'w':
                    cr_w += 1
                elif self.items[el][1] == 'a_b':
                    cr_a_b += 1
                elif self.items[el][1] == 'a_h':
                    cr_a_h += 1
                else:
                    pass

            if item in self.items.keys():
                if self.items[item][1] == 'w':
                    if cr_w > 0:
                        self.upd_messages('You can not carry any more items of this type!')
                    else:
                        self.creatures['@'][6].append(item)
                        self.creatures['@'][5] = ' '
                        self.upd_messages('You picked up ' + self.items[item][0] + '. ')
                elif self.items[item][1] == 'a_b':
                    if cr_a_b > 0:
                        self.upd_messages('You can not carry any more items of this type!')
                    else:
                        self.creatures['@'][6].append(item)
                        self.creatures['@'][5] = ' '
                        self.upd_messages('You picked up ' + self.items[item][0] + '. ')
                elif self.items[item][1] == 'a_h':
                    if cr_a_h > 0:
                        self.upd_messages('You can not carry any more items of this type!')
                    else:
                        self.creatures['@'][6].append(item)
                        self.creatures['@'][5] = ' '
                        self.upd_messages('You picked up ' + self.items[item][0] + '. ')
                else:
                    self.creatures['@'][6].append(item)
                    self.creatures['@'][5] = ' '
                    self.upd_messages('You picked up ' + self.items[item][0] + '. ')
            else:
                self.upd_messages('Nothing to pick up here.')
        else:
            self.upd_messages('You can not carry any more items!')
                        
                    

    def drop(self, creature, item):
        '''
        takes creature (single char) and item (single char) as input;
        drops item from creature's inventory
        '''
        flag = False
        if self.creatures[creature][5] == ' ':
            self.creatures[creature][5] = item
            flag = True
        elif self.active_map[self.creatures[creature][4][0]-1][self.creatures[creature][4][1]] == ' ':
            self.active_map[self.creatures[creature][4][0]-1][self.creatures[creature][4][1]] = item
            flag = True
        elif self.active_map[self.creatures[creature][4][0]+1][self.creatures[creature][4][1]] == ' ':
            self.active_map[self.creatures[creature][4][0]+1][self.creatures[creature][4][1]] = item
            flag = True
        elif self.active_map[self.creatures[creature][4][0]][self.creatures[creature][4][1]-1] == ' ':
            self.active_map[self.creatures[creature][4][0]][self.creatures[creature][4][1]-1] = item
            flag = True
        elif self.active_map[self.creatures[creature][4][0]][self.creatures[creature][4][1]+1] == ' ':
            self.active_map[self.creatures[creature][4][0]][self.creatures[creature][4][1]+1] = item
            flag = True
        else:
            pass

        if flag == True:
            buf = []
            for el in self.creatures[creature][6]:
                if el != item:
                    buf.append(el)
            item_ct =  len(self.creatures[creature][6]) - len(buf)
            while item_ct > 1:
                buf.append(item)
                item_ct -= 1
            self.creatures[creature][6] = buf
            return(flag)
        else:
            return(flag)

    def drop_menu(self):
        '''
        player menu for dropping items
        '''
        if len(self.creatures['@'][6]) > 0:
            self.upd_messages('Which item would you like to drop? ("n" for cancel)')
            buf = ''
            for item in self.creatures['@'][6]:
                buf += item + ' - ' + self.items[item][0] + '; '
            self.upd_messages(buf)

            self.draw_screen()

            while 1:
                kbd_inp = self.getch()
                if kbd_inp == 'n':
                    self.upd_messages('Cancelled.')
                    break
                else:
                    if kbd_inp not in self.creatures['@'][6]:
                        pass
                    else:
                        flag = self.drop('@', kbd_inp)
                        if flag:
                            self.upd_messages('You drop ' + self.items[kbd_inp][0] + '. ')
                            break
                        else:
                            self.upd_messages('Nowhere to drop!')
                            break
        else:
            self.upd_messages('Your inventory is empty!')


    def show_inv(self):
        '''
        updates self.messages with string, describing inventory contents;
        '''
        self.upd_messages('Currently you carry: ')
        buf = ''
        for item in self.creatures['@'][6]:
            buf += item + ' - ' + self.items[item][0] + '; '
        self.upd_messages(buf)

    def check_health(self):
        '''
        updates self.messages with string, describing health of player character;
        '''
        if self.creatures['@'][1] > 79:
            self.upd_messages("Seems like you are feeling good.")
        elif self.creatures['@'][1] > 49:
            self.upd_messages("You are feeling normal.")
        elif self.creatures['@'][1] > 19:
            self.upd_messages("You are feeling weak. You should find a way to improve your health.")
        else:
            self.upd_messages("You are barely clinging to existance!")

    def mod_health(self):
        '''
        modifies character health, depending on yummy he/she/it consumed;
        '''
        edibles = []
        for item in self.creatures['@'][6]:
            if self.items[item][1] == 'p':
                edibles.append(item)
        if len(edibles) == 0:
            self.upd_messages("You have nothing edible in your inventory.")
            self.draw_screen()
        else:
            buf = ''
            for item in edibles:
                buf += item + ' - ' + self.items[item][0] + '; '
            self.upd_messages('Which of this would you like to eat? ("n" for cancel)')
            self.upd_messages(buf)
            self.draw_screen()
            while 1:
                kbd_inp = self.getch()
                if kbd_inp == 'n':
                    self.upd_messages('Cancelled.')
                    self.draw_screen()
                    break
                else:
                    if kbd_inp in edibles:
                        if self.creatures['@'][1] == 100:
                            self.upd_messages('You are not hungry.')
                            self.draw_screen()
                            break
                        else:
                            if kbd_inp == '*' and self.creatures['@'][1] > 50:
                                self.upd_messages('You are not that hungry.')
                                self.draw_screen()
                                break
                            else:
                                self.creatures['@'][1] += self.items[kbd_inp][2]
                                if self.creatures['@'][1] > 100:
                                    self.creatures['@'][1] = 100
                                buf = []
                                for item in self.creatures['@'][6]:
                                    if item != kbd_inp:
                                        buf.append(item)
                                self.creatures['@'][6] = buf
                                self.upd_messages('You feel better now.')
                                self.draw_screen()
                                break
            

    def upd_messages(self, message):
        """
        updates list of messages;
        takes string of characters as input
        """
        if len(self.messages) == 2:
            self.messages = self.messages[1:]
        self.messages.append(message)

    def dummy_ai(self, creature):
        """
        uh... not sure, if it has to do something with "intelligence"...
        takes single character as input
        """
        creature_h = self.creatures[creature][4][0]
        creature_w = self.creatures[creature][4][1]
        player_h = self.creatures['@'][4][0]
        player_w = self.creatures['@'][4][1]

        if creature_h < player_h:
            delta_h = 1
        elif creature_h > player_h:
            delta_h = -1
        else:
            delta_h = 0

        if creature_w < player_w:
            delta_w = 1
        elif creature_w > player_w:
            delta_w = -1
        else:
            delta_w = 0

        move_deltas = [(delta_h,0), (0,delta_w)]
        path_tiles = [self.active_map[creature_h + delta_h][creature_w], self.active_map[creature_h][creature_w + delta_w]]

        if path_tiles[0] != '#' and path_tiles[1] == '#':
            self.upd_pos(creature, move_deltas[0])
        elif path_tiles[0] == '#' and path_tiles[1] != '#':
            self.upd_pos(creature, move_deltas[1])
        elif path_tiles[0] != '#' and path_tiles[1] != '#':
            if move_deltas[0] == (0,0):
                self.upd_pos(creature, move_deltas[1])
            elif move_deltas[1] == (0,0):
                self.upd_pos(creature, move_deltas[0])
            else:
                self.upd_pos(creature, move_deltas[self.randrange(2)])
        else:
            pass

    def upd_pos(self, creature, delta):
        """
        updates creature's position;
        takes creature sign and tuple of ints
        """
        if self.creatures[creature][1] > 0:
            creature_h = self.creatures[creature][4][0]
            creature_w = self.creatures[creature][4][1]
            if creature == '@' and self.active_map[creature_h+delta[0]][creature_w+delta[1]] == '^':
                self.flag = 'win'
            else:
                if 0 <= creature_h+delta[0] <= len(self.active_map)-1 and 0 <= creature_w+delta[1] <= len(self.active_map[0])-1:
                    if self.active_map[creature_h+delta[0]][creature_w+delta[1]] != '#':
                        if self.active_map[creature_h+delta[0]][creature_w+delta[1]] in self.creatures.keys() and \
                               creature != self.active_map[creature_h+delta[0]][creature_w+delta[1]]:
                           self.deal_damage(creature, self.active_map[creature_h+delta[0]][creature_w+delta[1]])
                           if creature == '@':
                                buf = []
                                for string in self.sight:
                                    buf += string
                                for el in self.creatures.keys():
                                    if el in buf and el != '@':
                                        self.dummy_ai(el)
                        else:
                            self.active_map[creature_h][creature_w] = self.creatures[creature][5]
                            self.creatures[creature][5] = self.active_map[creature_h+delta[0]][creature_w+delta[1]]
                            self.active_map[creature_h+delta[0]][creature_w+delta[1]] = creature
                            self.creatures[creature][4] = [creature_h+delta[0],creature_w+delta[1]]
                            if creature == '@':
                                buf = []
                                for string in self.sight:
                                    buf += string
                                for el in self.creatures.keys():
                                    if el in buf and el != '@':
                                        self.dummy_ai(el)
                self.player_sight_update()

    def draw_screen(self):
        """
        redraws screen
        """
        self.system('clear')
        # for testing
        #for string in self.active_map:
        #    buf = ''
        #    for char in string:
        #        buf += char
        #    print(buf)
        #print('\n')
        for string in self.sight:
            buf = ''
            for char in string:
                buf += char
            print(buf)
        for string in self.messages:
            print(string)
        
    def engine(self):
        """
        responsible for interactions with user
        """
        self.system('clear')
        print('\n\n\n\n\n\n\n\n')
        print('################################################################################')
        print('#                   You find yourself in a cold wet corridor                   #')
        print('#                    of place that seems to be an old crypt.                   #')
        print("#          You don't remember a thing, your body is pale and cold -            #")
        print("#                   all this leaves you with one explanation:                  #")
        print("#        you are a revenant, the one who somehow returned from Death.          #")
        print("#                 And now you have to fight for your new life.                 #")
        print('################################################################################')
        print('\n\n\n\n\n\n\n')
        kbd_inp = self.getch()
        self.upd_pos('@',(0,0))
        self.upd_messages("For help pres 'h'.")
        self.draw_screen()
        while self.flag == 'alive':
            if self.creatures['@'][1] <= 0:
                self.flag = 'dead'
                break
            kbd_inp = self.getch()
            if kbd_inp == 'w':
                delta = (-1,0)
                self.upd_pos('@',delta)
                self.draw_screen()
            elif kbd_inp == 's':
                delta = (1,0)
                self.upd_pos('@',delta)
                self.draw_screen()
            elif kbd_inp == 'a':
                delta = (0,-1)
                self.upd_pos('@',delta)
                self.draw_screen()
            elif kbd_inp == 'd':
                delta = (0,1)
                self.upd_pos('@',delta)
                self.draw_screen()
            elif kbd_inp == 'i':
                self.show_inv()
                self.draw_screen()
            elif kbd_inp == 'p':
                self.pick_up()
                self.draw_screen()
            elif kbd_inp == 'o':
                self.drop_menu()
                self.draw_screen()
            elif kbd_inp == 'c':
                self.check_health()
                self.draw_screen()
            elif kbd_inp == 'e':
                self.mod_health()
            elif kbd_inp == 'q':
                break
            elif kbd_inp == 'h':
                self.system('clear')
                print('Controls:')
                print('wasd - movement; to hit monster just move towards him;')
                print('p - pick up item;')
                print('o - drop item;')
                print('i - show inventory;')
                print('c - check health;')
                print('e - eat something;')
                print('q - quit;')
                print('h - show this note;\n')
                print('Bestiary:')
                print('G - giant rat; low threat;')
                print('F - feeble skeleton; low threat;')
                print('S - skeleton; moderate threat;')
                print('U - undead warrior; high threat;')
                print('W - undead warlord; deadly;')
                print('B - Butcher; deadly;\n')
                print('Press any key to return to game.')
                kbd_inp = self.getch()
                self.draw_screen()
            else:
                pass
        if self.flag == 'dead':
            if 'h' in self.creatures['@'][6] and 'P' in self.creatures['@'][6] and 's' in self.creatures['@'][6]:
                print('\n\n\n\n\n\n\n\n')
                print('################################################################################')
                print("#        Even your undead body can not bear severe damage it received.         #")
                print("#          As you fall down, your consciousness fades away from you.           #")
                print("#                        At the very bay of existance                          #")
                print("# you hear the proud sound of horns of the mighty heroes of the Corpse Hall.   #")
                print("#                             Walhall awaits you.                              #")
                print('################################################################################')
                print('\n\n\n\n\n\n\n\n')
            else:
                print('\n\n\n\n\n\n\n\n\n')
                print('################################################################################')
                print("#        Even your undead body can not bear severe damage it received.         #")
                print("#          As you fall down, your consciousness fades away from you.           #")
                print("#                            Now you die for real.                             #")
                print('################################################################################')
                print('\n\n\n\n\n\n\n\n\n')
        if self.flag == 'win':
            print('\n\n\n\n\n\n\n\n\n')
            print('################################################################################')
            print("#     After long - hours, days, weeks? - of lingering in the dark of wet       #")
            print("# coridors of the old crypt, you at last find your way up, to the sunlight...  #")
            print("#                     Who you were? What will you do now?                      #")
            print("#          It's up to you to search for answeres to these questions.           #")
            print('################################################################################')
            print('\n\n\n\n\n\n\n\n')

        if self.flag == 'win':
            achievements = []
            if 'h' in self.creatures['@'][6] and 'P' in self.creatures['@'][6] and 's' in self.creatures['@'][6] and self.creatures['B'][1] <= 0:
                achievements.append("True Viking: Obtain shabby bearskin over mail,\n               old nordic helmet, broad axe and kill Butcher.")
            Gandhi = True
            butcher = True
            for creature in self.creatures:
                if self.creatures[creature][1] <= 0:
                    Gandhi = False
                if self.creatures[creature][1] > 0 and creature != '@':
                    butcher = False
            if Gandhi == True:
                achievements.append("Gandhi: Get to the surface without killing any creature.")
            if butcher == True:
                achievements.append("The Real Butcher: Kill every dweller of the crypt.")
            gold = 0
            for item in self.creatures['@'][6]:
                if item == '=':
                    gold += 1
            if gold == 4:
                achievements.append("A greed in need is a greed indeed: Collect four gold bars.")
#            if len(achievements) == 0:
#                achievements.append("You get an achievement for getting no achievements... Wait O_o.\n\n")

            if len(achievements) > 0:
                kbd_inp = self.getch()
                print("Congratulations! Your achievements for this run:")
                for el in achievements:
                    print(el)
                print('\n')


R = Game()
R.engine()
