import pygame
import sys
import math
import random
pygame.init()

#screen size
W, H = 900, 520
scr = pygame.display.set_mode((W, H))
clk = pygame.time.Clock()
pygame.display.set_caption("Game with Menu")

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 200, 0)
BUTTON_HOVER = (0, 255, 0)

#fonts
F = pygame.font.SysFont(None, 28)  #small font
G = pygame.font.SysFont(None, 36)  #big font
menu_font = pygame.font.SysFont(None, 48)

#menu button
button_width, button_height = 300, 80
button_rect = pygame.Rect((W - button_width)//2, H - 150, button_width, button_height)

#menu background
menu_bg = pygame.image.load("image/interface_enter.png")
menu_bg = pygame.transform.scale(menu_bg, (W, H))

#map images
bg_img = pygame.image.load("image/BackGround.PNG").convert()  #map 1 bg
ground_img = pygame.image.load("image/Ground.PNG").convert()
bg2_img = pygame.image.load("image/3_background.png").convert()  #map 2 bg
bg3_img = pygame.image.load("image/3_game_background.png").convert()  #map 2 bg after puzzle

#image sizes
BG_W = bg_img.get_width()
BG_H = bg_img.get_height()
BG2_W = bg2_img.get_width()
BG2_H = bg2_img.get_height()
BG3_W = bg3_img.get_width()
BG3_H = bg3_img.get_height()
GROUND_H = ground_img.get_height()
GROUND_Y = H - GROUND_H  #ground y position

#map settings
MAP_1 = 1
MAP_2 = 2
current_map = MAP_1
MAP2_REPEATS = 3  #repeat map 2 bg 3 times

#object images
obj_box = pygame.image.load("image/Box.png").convert_alpha()
quest_icon = pygame.image.load("image/icon.png").convert_alpha()
door_img = pygame.image.load("image/Door.PNG").convert_alpha()
end_img = pygame.image.load("image/end.png").convert()

#player sprites
player_left_1 = pygame.image.load("image/player_left_1.png").convert_alpha()
player_left_2 = pygame.image.load("image/player_left_2.png").convert_alpha()
player_right_1 = pygame.image.load("image/player_right_1.png").convert_alpha()
player_right_2 = pygame.image.load("image/player_right_2.png").convert_alpha()

#box size
BOX_W, BOX_H = 80, 50

#player settings
pw, ph = 94, 114  #player width height
gy = H - GROUND_H  #ground y level
px, py = 110.0, gy - ph  #player start position
spd = 6  #player speed
player_direction = 1  #1=right -1=left
player_anim_frame = 0  #current anim frame
player_anim_timer = 0  #anim timer
player_base_y = gy - ph  #base y for float
float_offset = 0.0  #current float offset
float_speed = 0.1  #float animation speed
float_amount = 3.0  #how much player floats

#map 1 objects
objs = [
    {"name": "Board", "rect": pygame.Rect(420, gy - BOX_H - 50, BOX_W, BOX_H)}  #map 1 board
]

#map 2 objects
objs_map2 = []  #init when enter map 2

#ghost npc settings
GHOST_NPC_X = 2240  #ghost interaction x position
GHOST_NPC_H = 80  #ghost interaction height

#interaction range
rng = 150

#world bounds
WORLD_MIN_X = 0
WORLD_MAX_X = W - pw  #right edge minus player width

#ui state
q = False  #quest menu open
tgt = None  #target object
e_lock = False  #e key lock
cam = 0.0  #camera position
puzzle_completed = False  #map 1 puzzle done
puzzle2_completed = False  #map 2 puzzle done
ghost_interacted = False  #ghost talked to
showing_dialogue = False  #show dialogue
showing_end = False  #show end screen

#camera settings
USE_CAMERA = False  #enable camera follow

#door size
DOOR_W = 150
DOOR_H = 200

def draw_menu_button():
    #draw menu button with hover effect
    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(scr, color, button_rect)
    text_surface = menu_font.render("Click to Start", True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    scr.blit(text_surface, text_rect)

def bg(cam=0.0):
    #draw background and ground
    global current_map
    
    if current_map == MAP_1:
        #map 1 - static or scrolling bg
        if cam == 0.0:
            #static bg
            scr.blit(bg_img, (0, 0))
            scr.blit(ground_img, (0, GROUND_Y))
        else:
            #scrolling bg - tile horizontally
            off = -int(cam) % BG_W
            scr.blit(bg_img, (off - BG_W, 0))
            scr.blit(ground_img, (off - BG_W, GROUND_Y))
            scr.blit(bg_img, (off, 0))
            scr.blit(ground_img, (off, GROUND_Y))
    else:
        #map 2 - repeat bg tiles
        if cam == 0.0:
            cam = px  #use player pos if no cam
        
        #calculate which tiles visible
        map_width = BG2_W * MAP2_REPEATS
        screen_left_world = cam - W // 2
        screen_right_world = cam + W // 2
        first_tile = max(0, int(screen_left_world // BG2_W) - 1)
        last_tile = min(MAP2_REPEATS - 1, int(screen_right_world // BG2_W) + 1)
        
        #draw visible tiles
        global puzzle2_completed
        for tile_x in range(first_tile, last_tile + 1):
            if 0 <= tile_x < MAP2_REPEATS:
                tile_world_x = tile_x * BG2_W
                screen_x = tile_world_x - cam + W // 2
                if screen_x > -BG2_W and screen_x < W:
                    #replace last tile if puzzle done
                    if puzzle2_completed and tile_x == MAP2_REPEATS - 1:
                        scr.blit(bg3_img, (screen_x, 0))
                    else:
                        scr.blit(bg2_img, (screen_x, 0))

def w2s(x, y, cam=0.0):
    #convert world coords to screen coords
    if cam == 0.0:
        return int(x), int(y)  #no cam - direct mapping
    else:
        return int(x - cam + W // 2), int(y)  #with cam - player centered

def draw_objs(cam=0.0):
    #draw interactable objects and door
    global current_map, puzzle2_completed
    
    if current_map == MAP_1:
        #draw map 1 board
        for o in objs:
            box_bottom_y = gy - 50
            sx, sy_bottom = w2s(o["rect"].x, box_bottom_y, cam)
            box_img = pygame.transform.scale(obj_box, (o["rect"].w, o["rect"].h))
            sy = sy_bottom - o["rect"].h
            scr.blit(box_img, (sx, sy))
        
        #draw door if puzzle done
        if puzzle_completed:
            door_x = W - DOOR_W - 50
            door_y = gy - DOOR_H
            sx, sy = w2s(door_x, door_y, cam)
            door_scaled = pygame.transform.scale(door_img, (DOOR_W, DOOR_H))
            scr.blit(door_scaled, (sx, sy))
    
    elif current_map == MAP_2:
        #draw map 2 board if puzzle not done
        if not puzzle2_completed:
            for o in objs_map2:
                box_bottom_y = o["rect"].y + o["rect"].h
                sx, sy_bottom = w2s(o["rect"].x, box_bottom_y, cam)
                box_img = pygame.transform.scale(obj_box, (o["rect"].w, o["rect"].h))
                sy = sy_bottom - o["rect"].h
                scr.blit(box_img, (sx, sy))

def nearest(px_world):
    #find nearest interactable object to player
    global current_map, puzzle_completed, puzzle2_completed, ghost_interacted
    
    best, dmin = None, 1e9
    
    if current_map == MAP_1:
        #check map 1 objects
        for o in objs:
            cx, cy = o["rect"].center
            d = math.hypot(px_world - cx, (py + ph / 2) - cy)
            if d < dmin:
                best, dmin = o, d
    elif current_map == MAP_2:
        #check map 2 objects
        for o in objs_map2:
            cx, cy = o["rect"].center
            d = math.hypot(px_world - cx, (py + ph / 2) - cy)
            if d < dmin:
                best, dmin = o, d
        
        #check ghost if puzzle done
        if puzzle2_completed and not ghost_interacted:
            ghost_center_x = GHOST_NPC_X
            ghost_center_y = py + ph / 2
            d = math.hypot(px_world - ghost_center_x, (py + ph / 2) - ghost_center_y)
            if d < dmin:
                best = {"name": "Ghost", "center": (ghost_center_x, ghost_center_y), "rect": pygame.Rect(GHOST_NPC_X - 50, py + ph - GHOST_NPC_H, 100, GHOST_NPC_H)}
                dmin = d
    
    #check door if puzzle done on map 1
    if current_map == MAP_1 and puzzle_completed:
        door_x = W - DOOR_W - 50
        door_y = gy - DOOR_H
        door_center_x = door_x + DOOR_W // 2
        door_center_y = door_y + DOOR_H // 2
        d = math.hypot(px_world - door_center_x, (py + ph / 2) - door_center_y)
        if d < dmin:
            best = {"name": "Door", "center": (door_center_x, door_center_y)}
            dmin = d
    
    return best, dmin

def draw_player(cam=0.0):
    #draw player with float animation
    float_offset = math.sin(pygame.time.get_ticks() * float_speed * 0.01) * float_amount
    current_y = py + float_offset
    
    #get sprite based on direction and frame
    if player_direction == 1:
        #facing right
        if player_anim_frame == 0:
            current_sprite = player_right_1
        else:
            current_sprite = player_right_2
    else:
        #facing left
        if player_anim_frame == 0:
            current_sprite = player_left_1
        else:
            current_sprite = player_left_2
    
    #scale sprite to player size
    sprite_rect = current_sprite.get_rect()
    if sprite_rect.width != pw or sprite_rect.height != ph:
        current_sprite = pygame.transform.scale(current_sprite, (pw, ph))
    
    #draw player
    sx, sy = w2s(px, current_y, cam)
    scr.blit(current_sprite, (sx, sy))

def hud(cam=0.0):
    #draw hud bar with x pos and map info
    global current_map
    bar = pygame.Surface((W, 30), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 120))
    scr.blit(bar, (0, 0))
    scr.blit(F.render(f"x={int(px)}", True, (240, 240, 240)), (12, 6))
    
    #show map number
    map_text = F.render(f"Map: {current_map}", True, (240, 240, 240))
    scr.blit(map_text, (W - map_text.get_width() - 12, 6))

    #show interaction hint if near object
    o, d = nearest(px + pw / 2)
    if o and d <= rng and not q and not showing_dialogue and not showing_end:
        if o.get("name") == "Board":
            #dont show hint if puzzle done
            if (current_map == MAP_1 and puzzle_completed) or (current_map == MAP_2 and puzzle2_completed):
                pass
            else:
                hint = F.render(f"[E] {o.get('name', 'Unknown')}", True, (255, 255, 255))
                scr.blit(hint, (W // 2 - hint.get_width() // 2, 6))
        elif o.get("name") == "Door":
            hint = F.render("[E] Enter Door", True, (255, 255, 255))
            scr.blit(hint, (W // 2 - hint.get_width() // 2, 6))
        elif o.get("name") == "Ghost":
            hint = F.render("[E] Talk to Ghost", True, (255, 255, 255))
            scr.blit(hint, (W // 2 - hint.get_width() // 2, 6))
        else:
            hint = F.render(f"[E] {o.get('name', 'Unknown')}", True, (255, 255, 255))
            scr.blit(hint, (W // 2 - hint.get_width() // 2, 6))

def draw_interact_icon(cam=0.0):
    #draw interaction icon above object
    o, d = nearest(px + pw / 2)
    if o and d <= rng and not q and not showing_dialogue and not showing_end:
        #dont show icon if puzzle done
        if o.get("name") == "Board":
            if (current_map == MAP_1 and puzzle_completed) or (current_map == MAP_2 and puzzle2_completed):
                return
        #get icon position based on object type
        if o.get("name") == "Door":
            cx, cy = o.get("center", (0, 0))
            top_y = cy - DOOR_H // 2
        elif o.get("name") == "Ghost":
            cx, cy = o.get("center", (0, 0))
            top_y = py + ph - GHOST_NPC_H - 20
        else:
            cx = o["rect"].centerx
            top_y = o["rect"].y
        sx, sy = w2s(cx, top_y, cam)

        #scale icon
        icon_size = 40
        if quest_icon.get_width() > 0 and quest_icon.get_height() > 0:
            icon_scale = icon_size / max(quest_icon.get_width(), quest_icon.get_height())
            icon_w = int(quest_icon.get_width() * icon_scale)
            icon_h = int(quest_icon.get_height() * icon_scale)
            icon_scaled = pygame.transform.scale(quest_icon, (icon_w, icon_h))
        else:
            icon_scaled = quest_icon

        #draw icon above object
        sx -= icon_scaled.get_width() // 2
        sy -= icon_scaled.get_height() + 10
        scr.blit(icon_scaled, (sx, sy))

def quest():
    dim = pygame.Surface((W, H), pygame.SRCALPHA); dim.fill((0, 0, 0, 150))
    scr.blit(dim, (0, 0))
    w, h = int(W * 0.6), int(H * 0.55)
    x, y = (W - w) // 2, (H - h) // 2
    p = pygame.Rect(x, y, w, h)
    pygame.draw.rect(scr, (235, 235, 240), p, border_radius=16)
    pygame.draw.rect(scr, (40, 40, 45), p, 4, border_radius=16)
    scr.blit(G.render("Quest", True, (20, 20, 28)), (p.centerx - 40, p.y + 18))
    lines = [
        f"Target: {tgt['name']}" if tgt else "No target",
        "• Explore",
        "• Find crystal",
        "• Return to board",
        "E/Esc: close",
    ]
    yy = y + 70
    for s in lines:
        scr.blit(F.render(s, True, (35, 35, 45)), (x + 28, yy)); yy += 32

def draw_ghost_dialogue():
    dim = pygame.Surface((W, H), pygame.SRCALPHA); dim.fill((0, 0, 0, 150))
    scr.blit(dim, (0, 0))
    w, h = int(W * 0.7), int(H * 0.3)
    x, y = (W - w) // 2, (H - h) // 2
    p = pygame.Rect(x, y, w, h)
    pygame.draw.rect(scr, (235, 235, 240), p, border_radius=16)
    pygame.draw.rect(scr, (40, 40, 45), p, 4, border_radius=16)
    
    scr.blit(G.render("Ghost", True, (20, 20, 28)), (x + 28, y + 18))
    
    dialogue_text = "You make me free, thank you!"
    lines = dialogue_text.split('\n') if '\n' in dialogue_text else [dialogue_text]
    yy = y + 70
    for line in lines:
        scr.blit(F.render(line, True, (35, 35, 45)), (x + 28, yy))
        yy += 32
    
    esc_text = F.render("Press E/Esc to continue", True, (100, 100, 120))
    scr.blit(esc_text, (x + 28, y + h - 35))

def draw_end_screen():
    end_scaled = pygame.transform.scale(end_img, (W, H))
    scr.blit(end_scaled, (0, 0))
    
    instruction = F.render("Click anywhere to return to menu", True, (255, 255, 255))
    text_rect = instruction.get_rect(center=(W // 2, H - 30))
    bg_rect = text_rect.inflate(20, 10)
    bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surf.fill((0, 0, 0, 150))
    scr.blit(bg_surf, bg_rect)
    scr.blit(instruction, text_rect)

def jigsaw_puzzle(puzzle_image="image/puzzle.png"):
    #jigsaw puzzle game - swap pieces to complete
    global puzzle_completed, puzzle2_completed, e_lock, current_map
    
    is_map2 = (current_map == MAP_2)
    puzzle_done = puzzle2_completed if is_map2 else puzzle_completed
    
    #already done
    if puzzle_done:
        return True
    
    #puzzle window setup
    puzzle_window = pygame.Surface((500, 500))
    puzzle_rect = pygame.Rect((W - 500) // 2, (H - 500) // 2, 500, 500)
    
    #load puzzle image
    try:
        puzzle_pic = pygame.image.load(puzzle_image).convert()
    except:
        #try fallback images
        try:
            puzzle_pic = pygame.image.load("image/puzzle.png").convert()
        except:
            try:
                puzzle_pic = pygame.image.load("image/ghosty.png").convert()
            except:
                #create placeholder
                puzzle_pic = pygame.Surface((500, 500))
                puzzle_pic.fill((100, 100, 150))
    
    #scale to 500x500
    if puzzle_pic.get_width() != 500 or puzzle_pic.get_height() != 500:
        puzzle_pic = pygame.transform.scale(puzzle_pic, (500, 500))
    
    puzzle_pic_rect = puzzle_pic.get_rect()
    puzzle_pic_rect.topleft = (0, 0)
    
    selected_img = None  #selected piece
    game_over = False  #puzzle complete
    show_completion = False  #show done text
    completion_timer = 0
    
    #split image into 3x3 pieces
    rows = 3
    cols = 3
    num_frames = rows * cols
    frame_width = 500 // rows
    frame_height = 500 // cols
    frames = []
    random_index = list(range(0, num_frames))
    
    #create shuffled pieces
    for i in range(num_frames):
        x = (i % rows) * frame_width
        y = (i // cols) * frame_height
        rect = pygame.Rect(x, y, frame_width, frame_height)
        random_position = random.choice(random_index)
        random_index.remove(random_position)
        frames.append({'rect': rect, 'border': WHITE, 'order': i, 'position': random_position})
    
    #puzzle game loop
    running_puzzle = True
    while running_puzzle:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_puzzle = False
                e_lock = False
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running_puzzle = False
                    e_lock = False
                    return False
            
            #click to swap pieces
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over and not show_completion:
                mouse_pos = pygame.mouse.get_pos()
                puzzle_mouse_pos = (mouse_pos[0] - puzzle_rect.x, mouse_pos[1] - puzzle_rect.y)
                
                if puzzle_rect.collidepoint(mouse_pos):
                    for frame in frames:
                        #get frame rect and order
                        rect = frame['rect']
                        order = frame['order']
                        
                        if rect.collidepoint(puzzle_mouse_pos):
                            if not selected_img:
                                #select piece
                                selected_img = frame
                                frame['border'] = (255, 0, 0)  #red border
                            else:
                                #swap with selected
                                current_img = frame
                                if current_img['order'] != selected_img['order']:
                                    #swap positions
                                    temp = selected_img['position']
                                    frames[selected_img['order']]['position'] = frames[current_img['order']]['position']
                                    frames[current_img['order']]['position'] = temp
                                    
                                    frames[selected_img['order']]['border'] = WHITE
                                    selected_img = None
                                    
                                    #check if complete
                                    game_over = True
                                    for frame in frames:
                                        if frame['order'] != frame['position']:
                                            game_over = False
                                            break
                                    
                                    #mark puzzle done
                                    if game_over:
                                        if is_map2:
                                            puzzle2_completed = True
                                        else:
                                            puzzle_completed = True
                                        show_completion = True
                                        completion_timer = 180  #3 seconds
        
        if show_completion:
            completion_timer -= 1
            if completion_timer <= 0:
                running_puzzle = False
                e_lock = False
                return True
        
        bg(cam)
        draw_objs(cam)
        draw_player(cam)
        hud(cam)
        
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        scr.blit(dim, (0, 0))
        
        puzzle_window.fill((225, 225, 225))
        
        if show_completion:
            puzzle_window.blit(puzzle_pic, puzzle_pic_rect)
            complete_font = pygame.font.SysFont(None, 60)
            complete_text = complete_font.render("DONE!", True, (0, 200, 0))
            text_rect = complete_text.get_rect(center=(250, 250))
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(puzzle_window, (255, 255, 255), bg_rect)
            pygame.draw.rect(puzzle_window, (0, 200, 0), bg_rect, 3)
            puzzle_window.blit(complete_text, text_rect)
        elif not game_over:
            for i, val in enumerate(frames):
                pos = frames[i]['position']
                img_area = pygame.Rect(frames[pos]['rect'].x, frames[pos]['rect'].y, frame_width, frame_height)
                puzzle_window.blit(puzzle_pic, frames[i]['rect'], img_area)
                pygame.draw.rect(puzzle_window, frames[i]['border'], frames[i]['rect'], 1)
        else:
            puzzle_window.blit(puzzle_pic, puzzle_pic_rect)
        
        scr.blit(puzzle_window, puzzle_rect)
        pygame.display.flip()
        clk.tick(60)
    
    e_lock = False
    if is_map2:
        return puzzle2_completed
    else:
        return puzzle_completed

def teleport_to_map2():
    #teleport player to map 2
    global current_map, px, py, cam, USE_CAMERA, objs_map2, puzzle2_completed
    
    current_map = MAP_2
    USE_CAMERA = True  #enable camera on map 2
    px = 100.0  #start x pos
    py = H - ph - 35  #start y pos
    cam = px  #set cam to player
    
    #create board if puzzle not done
    if not puzzle2_completed:
        map2_width = BG2_W * MAP2_REPEATS
        board_x = int(map2_width * 0.8)  #80% of map width
        board_y = py + ph - 60
        objs_map2 = [
            {"name": "Board", "rect": pygame.Rect(board_x, board_y - BOX_H, BOX_W, BOX_H)}
        ]
    else:
        objs_map2 = []

def start_game():
    #main game loop
    global px, q, tgt, e_lock, cam, player_direction, player_anim_frame, player_anim_timer, current_map, USE_CAMERA
    global showing_dialogue, showing_end, ghost_interacted, py, puzzle_completed, puzzle2_completed
    running_game = True
    
    #reset game state
    current_map = MAP_1
    USE_CAMERA = False
    showing_dialogue = False
    showing_end = False
    ghost_interacted = False
    puzzle_completed = False
    puzzle2_completed = False
    q = False
    tgt = None
    e_lock = False
    cam = 0.0
    
    #reset player position
    px = 110.0  #start x
    py = gy - ph  #start y

    while running_game:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_e and not e_lock:
                    e_lock = True
                    if showing_dialogue:
                        showing_dialogue = False
                        showing_end = True
                        e_lock = False
                    elif showing_end:
                        e_lock = False
                    elif q:
                        q, tgt = False, None
                    else:
                        o, d = nearest(px + pw / 2)
                        if o and d <= rng:
                            if o.get("name") == "Ghost":
                                showing_dialogue = True
                                ghost_interacted = True
                                e_lock = False
                            elif o.get("name") == "Door":
                                teleport_to_map2()
                                e_lock = False
                            elif o.get("name") == "Board":
                                if current_map == MAP_1:
                                    if not puzzle_completed:
                                        jigsaw_puzzle("image/puzzle.png")
                                    else:
                                        e_lock = False
                                elif current_map == MAP_2:
                                    if not puzzle2_completed:
                                        jigsaw_puzzle("image/ghost.png")
                                    else:
                                        e_lock = False
                            else:
                                q, tgt = True, o
                if e.key == pygame.K_ESCAPE:
                    if showing_dialogue:
                        showing_dialogue = False
                        showing_end = True
                    elif q:
                        q, tgt = False, None
            if e.type == pygame.MOUSEBUTTONDOWN:
                if showing_end:
                    showing_end = False
                    ghost_interacted = False
                    running_game = False
                    return
            if e.type == pygame.KEYUP and e.key == pygame.K_e:
                e_lock = False

        #player movement
        keys = pygame.key.get_pressed()
        if not q and not showing_dialogue and not showing_end:
            moved = False
            
            #get map boundaries
            if current_map == MAP_1:
                min_x = WORLD_MIN_X
                max_x = WORLD_MAX_X
            else:
                min_x = WORLD_MIN_X
                max_x = BG2_W * MAP2_REPEATS - pw
            
            #move left
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                new_x = px - spd
                if new_x >= min_x:
                    px = new_x  #move normally
                    player_direction = -1
                    moved = True
                elif px > min_x:
                    #move only to boundary
                    remaining = px - min_x
                    if remaining > 0:
                        px = min_x  #move to boundary
                        player_direction = -1
                        moved = True
                    else:
                        player_direction = -1  #just face direction
            #move right
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                new_x = px + spd
                if new_x <= max_x:
                    px = new_x  #move normally
                    player_direction = 1
                    moved = True
                elif px < max_x:
                    #move only to boundary
                    remaining = max_x - px
                    if remaining > 0:
                        px = max_x  #move to boundary
                        player_direction = 1
                        moved = True
                    else:
                        player_direction = 1  #just face direction
            
            #update animation
            if moved:
                player_anim_timer += 1
                if player_anim_timer >= 10:  #change frame every 10 ticks
                    player_anim_frame = 1 - player_anim_frame  #toggle frame
                    player_anim_timer = 0
            else:
                #idle - use first frame
                player_anim_frame = 0
                player_anim_timer = 0

        #update camera
        if USE_CAMERA:
            if current_map == MAP_1:
                cam = 0.0  #no cam on map 1
            else:
                cam = px  #cam follows player
                map_width = BG2_W * MAP2_REPEATS
                min_cam = W // 2  #dont scroll past left edge
                max_cam = map_width - W // 2  #dont scroll past right edge
                #clamp camera
                if cam < min_cam:
                    cam = min_cam
                elif cam > max_cam:
                    cam = max_cam
        else:
            cam = 0.0  #cam disabled

        if showing_end:
            draw_end_screen()
        else:
            bg(cam)
            draw_objs(cam)
            draw_player(cam)
            hud(cam)
            if not q and not showing_dialogue:
                draw_interact_icon(cam)
            if q:
                quest()
            if showing_dialogue:
                draw_ghost_dialogue()

        pygame.display.flip()
        clk.tick(60)

def main():
    #menu loop
    in_menu = True
    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    start_game()  #start game when button clicked

        #draw menu
        scr.blit(menu_bg, (0, 0))
        draw_menu_button()
        pygame.display.flip()
        clk.tick(60)

if __name__ == "__main__":
    main()