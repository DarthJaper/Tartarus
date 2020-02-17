import tcod as libtcod

from enum import Enum

from game_states import GameStates

from menus import inventory_menu


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names.capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height,
               bar_width, panel_height, panel_y, mouse, colors, game_state):

    if fov_recompute:
    # Draw all the tiles in the game map
    
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)

                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map)

    #UI rendering;

    libtcod.console_set_default_background(con, libtcod.black)
    libtcod.console_set_default_foreground(con, libtcod.white)
    
    #!!!!! TODO; Chanve "140" to depth var
    libtcod.console_print_ex(con, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, "Depth;")
    libtcod.console_print_ex(con, 1, 2, libtcod.BKGND_NONE, libtcod.LEFT, "140")

    libtcod.console_print_ex(con, 36, 1, libtcod.BKGND_NONE, libtcod.LEFT, "123")
    libtcod.console_print_ex(con, 36, 2, libtcod.BKGND_NONE, libtcod.LEFT, "4 4")
    libtcod.console_print_ex(con, 36, 3, libtcod.BKGND_NONE, libtcod.LEFT, "526")
    
    libtcod.console_set_default_foreground(con, libtcod.dark_gray)
    libtcod.console_print_ex(con, 31, 38, libtcod.BKGND_NONE, libtcod.LEFT, "Tartarus")
    
    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
  

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'

        inventory_menu(con, inventory_title, player.inventory, 50, screen_width, screen_height)



def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

def draw_entity(con, entity, fov_map):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
        idx = [ 0, 5 ] # indexes of the keys
        col = [ entity.color, libtcod.Color( 64,0,0 )] # colors : black, red, white
        colors=libtcod.color_gen_map(col,idx)
        
        color = colors[entity.z]
        libtcod.console_set_default_foreground(con, color)
        libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
