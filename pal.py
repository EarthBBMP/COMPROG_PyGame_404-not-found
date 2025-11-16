import pygame, random
pygame.init()

#adjust size
window_width=500
window_height=500

screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Spooky")

fsp=10
clock=pygame.time.Clock()

white=(225,225,225)
black=(0,0,0)
red=(255,0,0)

#add image
pics=pygame.image.load("ghosty.png")
pics_rect= pics.get_rect()
pics_rect.topleft=(0,0)

selected_img=None
game_over=False

#make jigsaw pieces
rows=3
cols=3
num_frames= rows*cols

frame_width= window_width // rows
frame_height= window_height // cols
frames=[]
random_index= list(range(0,num_frames))
#for loops
for i in range(num_frames):
    x=(i%rows)*frame_width
    y=(i//cols)*frame_height
    rect=pygame.Rect(x,y,frame_width,frame_height)
    random_position=random.choice(random_index)
    random_index.remove(random_position)
    frames.append({'rect':rect,'border': white, 'order':i,'position':random_position})
    
    
    
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
#click to change piece/mouse button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button ==1 and not game_over:
            mouse_pos=pygame.mouse.get_pos()
            
            for frame in frames:
                rect=frame['rect']
                order=frame['order'] #make frame subsequent (1-9)
                
                if rect.collidepoint(mouse_pos):
                    if not selected_img:
                        selected_img=frame
                        frame['border']=red #when selected it turn red
                    else:
                        #swap positions
                        current_img=frame
                        if current_img['order'] != selected_img['order']:
                            #swap image
                            temp = selected_img['position']
                            frames[selected_img['order']]['position']=frames[current_img['order']]['position']
                            frames[current_img['order']]['position']=temp
                            
                            frames[selected_img['order']]['border']=white
                            selected_img=None
                            
                            #check if puzzle is complete
                            game_over=True
                            for frame in frames:
                                if frame['order'] != frame['position']:
                                    game_over=False
                                    
                            
    #fill background        
    screen.fill(white)
    #merge pieces
    if not game_over:
    #image area/randomize pieces
        for i,val in enumerate(frames):
            pos=frames[i]['position']
            img_area=pygame.Rect(frames[pos]['rect'].x,frames[pos]['rect'].y,frame_width,frame_height)
            screen.blit(pics,frames[i]['rect'],img_area)
            pygame.draw.rect(screen,frames[i]['border'],frames[i]['rect'],1)
    else:
        screen.blit(pics,pics_rect)
    #screen.blit(pics,pics_rect,(0,0,100,100)) #x,y,w,h parts of image
    
    pygame.display.update()
    clock.tick(fsp)
       
pygame.quit()