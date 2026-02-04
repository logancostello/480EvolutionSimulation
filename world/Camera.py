import pygame

class Camera:
    """ Camera system for 2D world with zoom and pan capabilities """
    def __init__(self, world_width, world_height):
        self.world_width = world_width
        self.world_height = world_height
        
        # Camera position (center of view in world coordinates)
        self.x = world_width / 2
        self.y = world_height / 2
        
        # Zoom level (1.0 = normal, >1.0 = zoomed in, <1.0 = zoomed out)
        self.zoom = 0.25
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        
        # Panning
        self.is_panning = False
        self.pan_start_pos = (0, 0)
        self.pan_start_camera = (0, 0)
    
    def handle_event(self, event):
        """ Handle camera-related events (zoom and pan) """
        if event.type == pygame.MOUSEWHEEL:
            # Zoom with mouse wheel
            mouse_pos = pygame.mouse.get_pos()
            world_pos_before = self.screen_to_world(mouse_pos)
            
            # Adjust zoom
            zoom_factor = 1.1
            if event.y > 0:  # Scroll up - zoom in
                self.zoom *= zoom_factor
            elif event.y < 0:  # Scroll down - zoom out
                self.zoom /= zoom_factor
            
            # Clamp zoom
            self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
            
            # Adjust camera position to zoom towards mouse cursor
            world_pos_after = self.screen_to_world(mouse_pos)
            self.x += world_pos_before[0] - world_pos_after[0]
            self.y += world_pos_before[1] - world_pos_after[1]
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Middle mouse button
                self.is_panning = True
                self.pan_start_pos = event.pos
                self.pan_start_camera = (self.x, self.y)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_panning = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_panning:
                # Calculate pan offset in screen space
                dx = event.pos[0] - self.pan_start_pos[0]
                dy = event.pos[1] - self.pan_start_pos[1]
                
                # Convert to world space and update camera
                self.x = self.pan_start_camera[0] - dx / self.zoom
                self.y = self.pan_start_camera[1] - dy / self.zoom
    
    def screen_to_world(self, screen_pos):
        """ Convert screen coordinates to world coordinates """
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        world_x = self.x + (screen_pos[0] - screen_width / 2) / self.zoom
        world_y = self.y + (screen_pos[1] - screen_height / 2) / self.zoom
        
        return (world_x, world_y)
    
    def world_to_screen(self, world_pos):
        """ Convert world coordinates to screen coordinates """
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        screen_x = (world_pos[0] - self.x) * self.zoom + screen_width / 2
        screen_y = (world_pos[1] - self.y) * self.zoom + screen_height / 2
        
        return (screen_x, screen_y)
    
    def get_visible_area(self):
        """ Get the visible world area as (left, top, width, height) """
        screen_width, screen_height = pygame.display.get_surface().get_size()
        
        visible_width = screen_width / self.zoom
        visible_height = screen_height / self.zoom
        
        left = self.x - visible_width / 2
        top = self.y - visible_height / 2
        
        return (left, top, visible_width, visible_height)
    
    def apply(self, entity_rect):
        """ Apply camera transform to an entity's rect for rendering """
        screen_pos = self.world_to_screen((entity_rect.x, entity_rect.y))
        scaled_width = entity_rect.width * self.zoom
        scaled_height = entity_rect.height * self.zoom
        
        return pygame.Rect(screen_pos[0], screen_pos[1], scaled_width, scaled_height)