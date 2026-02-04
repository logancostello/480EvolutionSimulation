from spacial.Point import Point

class QuadTree:
    """ Efficient data structure for finding entities within a give region """
    
    def __init__(self, top_left, bottom_right, threshold, max_depth):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.threshold = threshold
        self.max_depth = max_depth
        self.contents = []
        self.divided = False
        self.children = [None, None, None, None]

    def insert(self, entity):

        # don't insert if not in bounds
        if not self.is_in_bounds(entity):
            return False
        
        # if already divided, add point to children
        if self.divided:
            for child in self.children:
                if child.insert(entity): 
                    return True # break after placing into one child to prevent duplication
        
        else:
            # if not divided, add to contents
            self.contents.append(entity)

            # divide if needed
            if len(self.contents) > self.threshold:
                self.divide()

            return True

    def divide(self):

        # don't go past max depth
        if self.max_depth <= 0:
            return

        # split four ways
        center = Point(
            self.top_left.x + (self.bottom_right.x - self.top_left.x) / 2,
            self.top_left.y + (self.bottom_right.y - self.top_left.y) / 2
            )
        
        self.children = [
            QuadTree(self.top_left, center, self.threshold, self.max_depth - 1), # NW
            QuadTree(Point(center.x, self.top_left.y), Point(self.bottom_right.x, center.y), self.threshold, self.max_depth - 1), # NE
            QuadTree(center, self.bottom_right, self.threshold, self.max_depth - 1), # SE
            QuadTree(Point(self.top_left.x, center.y), Point(center.x, self.bottom_right.y), self.threshold, self.max_depth - 1) # SW
        ]

        # move contents to children
        for entity in self.contents:
            for child in self.children:
                if child.insert(entity):
                    break

        # mark as divided
        self.contents = []
        self.divided = True

    def remove(self, entity):

        # can't remove if not in bounds
        if not self.is_in_bounds(entity):
            return False
        
        # if divided, remove from children
        if self.divided:
            for child in self.children:
                if child.remove(entity): 
                    self.try_collapse()
                    return True
            
        else:
            # if not divided, remove from contents
            if entity in self.contents: # check incase of border edge case
                self.contents.remove(entity)
                return True
            return False
            
    def try_collapse(self):

        # leaves cant collapse
        if not self.divided:
            return False
        
        # grandparents cant collapse
        for child in self.children:
            if child.divided:
                return False
            
        # get all contents from children
        total_items = []
        for child in self.children:
            total_items.extend(child.contents)

        # collapse if under threshold
        if len(total_items) <= self.threshold:
            self.contents = total_items
            self.divided = False
            self.children = [None, None, None, None]
            return True
        return False

    def is_in_bounds(self, entity):
        return self.top_left.x <= entity.pos.x <= self.bottom_right.x and self.top_left.y <= entity.pos.y <= self.bottom_right.y
    
    def get_all(self):
        if not self.divided:
            return self.contents
        
        all_entities = []
        for child in self.children:
            all_entities.extend(child.get_all())
        return all_entities