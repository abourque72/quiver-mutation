import tkinter as tk
from functools import partial 

#node_radius = 10
#node_spacing = 100

class Node:
    def __init__(self, app, canvas, x, y, node_radius):
        self.app = app
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = node_radius
        self.letters = ['', 'F', 'M']
        self.current_letter = 0
        self.id = canvas.create_oval(x - self.radius, y - self.radius,
                                     x + self.radius, y + self.radius,
                                     outline='black', fill = 'white', tags='node')
        self.text_id = canvas.create_text(x,y, text=self.letters[self.current_letter], font=('Arial', self.radius+2, 'bold'))
        self.arrow_to = set()
        self.nodes_to = set()
        self.arrow_from = set()
        self.nodes_from = set()
        canvas.tag_bind(self.id, '<Button-1>', self.on_click)
        canvas.tag_bind(self.text_id, '<Button-1>', self.on_click)
        canvas.tag_bind(self.id, '<B1-Motion>', self.on_drag)
        canvas.tag_bind(self.text_id, '<B1-Motion>', self.on_drag)

    def on_drag(self,event):
        if self.canvas.mode == 'move nodes':
            #move node and letter
            dx = event.x - self.x
            dy = event.y - self.y
            self.canvas.move(self.id, dx, dy)
            self.canvas.move(self.text_id, dx, dy)
            self.x = event.x
            self.y = event.y

            #update lines
            for tup in self.arrow_to:
                midx = (self.x + tup[0].x)//2
                midy = (self.y + tup[0].y)//2
                self.canvas.coords(tup[1], self.x, self.y, midx, midy)
                self.canvas.coords(tup[2], midx, midy, tup[0].x, tup[0].y)
                self.canvas.move(tup[3], (dx/2), (dy/2))

            for tup in self.arrow_from:
                midx = (self.x + tup[0].x)//2
                midy = (self.y + tup[0].y)//2
                self.canvas.coords(tup[1], tup[0].x, tup[0].y, midx, midy)
                self.canvas.coords(tup[2], midx, midy, self.x, self.y)
                self.canvas.move(tup[3], (dx/2), (dy/2))
                
    def on_click(self, event):
        if self.canvas.mode == 'set nodes':
            self.current_letter = (self.current_letter + 1) % len(self.letters)
            self.canvas.itemconfig(self.text_id, text=self.letters[self.current_letter])
        elif self.canvas.mode == 'mutate' and self.current_letter == 2:
            #first, prep list of nodes which are either frozen or mutable. mutable should go first. 
            quiver_nodes = []
            n = 0
            for node in self.app.nodes:
                if node.current_letter == 1:
                    quiver_nodes.append(node)
                elif node.current_letter == 2:
                    quiver_nodes.insert(0, node)
                    n += 1
            m = len(quiver_nodes)
            #n = number of mutable nodes, m = number of mutable and frozen nodes.
            A = [[0 for _ in range(n)] for _ in range(m)]
            k = m
            for i in range(n):
                if quiver_nodes[i] == self:
                    k = i
            for i in range(m):
                for j in range(n):
                    node_i, node_j = quiver_nodes[i], quiver_nodes[j]
                    if node_j in node_i.nodes_to:
                        l = 0
                        for tup in node_i.arrow_to:
                            if tup[0] == node_j:
                                l = int(self.canvas.itemcget(tup[3],"text"))
                        A[i][j] = l
                    elif node_j in node_i.nodes_from:
                        l = 0
                        for tup in node_i.arrow_from:
                            if tup[0] == node_j:
                                l = int(self.canvas.itemcget(tup[3], "text"))
                        A[i][j] = -l
            #A is the extended exchange matrix of the quiver.
            
            B = [[0 for _ in range(n)] for _ in range(m)]
            
            for i in range(m):
                for j in range(n):
                    if i == k or j == k:
                        B[i][j] = -A[i][j]
                    elif A[i][k] > 0 and A[k][j] > 0:
                        B[i][j] = A[i][j] + A[i][k]*A[k][j]
                    elif A[i][k] < 0 and A[k][j] < 0:
                        B[i][j] = A[i][j] - A[i][k]*A[k][j]
                    else: 
                        B[i][j] = A[i][j]
                        
            #B is the extended exchange matrix of the mutated quiver. 
            
            #now we need to edit the quiver visually. 
            
            #first, deletion:
            
            for node in quiver_nodes:
                node.nodes_to = set()
                node.nodes_from = set()
                node.arrow_from = set()
                for tup in node.arrow_to:
                    self.canvas.delete(tup[1])
                    self.canvas.delete(tup[2])
                    self.canvas.tag_unbind(tup[3], '<Button-1>')
                    self.canvas.tag_unbind(tup[3], '<Button-3>')
                    self.canvas.delete(tup[3])
                node.arrow_to = set()
            
            for i in range(n):
                for j in range(i+1, n):
                    node_i, node_j = quiver_nodes[i], quiver_nodes[j]
                    if B[i][j] > 0:
                        node_i.nodes_to.add(node_j)
                        node_j.nodes_from.add(node_i)
                        x1 = node_i.x
                        y1 = node_i.y 
                        x2 = node_j.x 
                        y2 = node_j.y 
                        mx = (x1+x2)//2
                        my = (y1+y2)//2
                        am = self.canvas.create_line(x1,y1,mx,my,fill='black', arrow=tk.LAST)
                        me = self.canvas.create_line(mx,my,x2,y2,fill='black')
                        mult = self.canvas.create_text(mx, my, text=str(B[i][j]), font = ('Arial', self.radius))
                        p_on_left_click_edge = partial(self.on_left_click_edge, mult)
                        p_on_right_click_edge = partial(self.on_right_click_edge, mult)
                        self.canvas.tag_bind(mult, '<Button-1>', p_on_left_click_edge)
                        self.canvas.tag_bind(mult, '<Button-3>', p_on_right_click_edge)
                        node_i.arrow_to.add((node_j,am,me,mult))
                        node_j.arrow_from.add((node_i,am,me,mult))
                    elif B[i][j] < 0:
                        node_j.nodes_to.add(node_i)
                        node_i.nodes_from.add(node_j)
                        x2 = node_i.x
                        y2 = node_i.y 
                        x1 = node_j.x 
                        y1 = node_j.y 
                        mx = (x1+x2)//2
                        my = (y1+y2)//2
                        am = self.canvas.create_line(x1,y1,mx,my,fill='black', arrow=tk.LAST)
                        me = self.canvas.create_line(mx,my,x2,y2,fill='black')
                        mult = self.canvas.create_text(mx, my, text=str(-B[i][j]), font = ('Arial', self.radius))
                        p_on_left_click_edge = partial(self.on_left_click_edge, mult)
                        p_on_right_click_edge = partial(self.on_right_click_edge, mult)
                        self.canvas.tag_bind(mult, '<Button-1>', p_on_left_click_edge)
                        self.canvas.tag_bind(mult, '<Button-3>', p_on_right_click_edge)
                        node_j.arrow_to.add((node_i,am,me,mult))
                        node_i.arrow_from.add((node_j,am,me,mult))
            
            for i in range(n,m):
                for j in range(n):
                    node_i, node_j = quiver_nodes[i], quiver_nodes[j]
                    if B[i][j] > 0:
                        node_i.nodes_to.add(node_j)
                        node_j.nodes_from.add(node_i)
                        x1 = node_i.x
                        y1 = node_i.y 
                        x2 = node_j.x 
                        y2 = node_j.y 
                        mx = (x1+x2)//2
                        my = (y1+y2)//2
                        am = self.canvas.create_line(x1,y1,mx,my,fill='black', arrow=tk.LAST)
                        me = self.canvas.create_line(mx,my,x2,y2,fill='black')
                        mult = self.canvas.create_text(mx, my, text=str(B[i][j]), font = ('Arial', self.radius))
                        p_on_left_click_edge = partial(self.on_left_click_edge, mult)
                        p_on_right_click_edge = partial(self.on_right_click_edge, mult)
                        self.canvas.tag_bind(mult, '<Button-1>', p_on_left_click_edge)
                        self.canvas.tag_bind(mult, '<Button-3>', p_on_right_click_edge)
                        node_i.arrow_to.add((node_j,am,me,mult))
                        node_j.arrow_from.add((node_i,am,me,mult))
                    elif B[i][j] < 0:
                        node_j.nodes_to.add(node_i)
                        node_i.nodes_from.add(node_j)
                        x2 = node_i.x
                        y2 = node_i.y 
                        x1 = node_j.x 
                        y1 = node_j.y 
                        mx = (x1+x2)//2
                        my = (y1+y2)//2
                        am = self.canvas.create_line(x1,y1,mx,my,fill='black', arrow=tk.LAST)
                        me = self.canvas.create_line(mx,my,x2,y2,fill='black')
                        mult = self.canvas.create_text(mx, my, text=str(-B[i][j]), font = ('Arial', self.radius))
                        p_on_left_click_edge = partial(self.on_left_click_edge, mult)
                        p_on_right_click_edge = partial(self.on_right_click_edge, mult)
                        self.canvas.tag_bind(mult, '<Button-1>', p_on_left_click_edge)
                        self.canvas.tag_bind(mult, '<Button-3>', p_on_right_click_edge)
                        node_j.arrow_to.add((node_i,am,me,mult))
                        node_i.arrow_from.add((node_j,am,me,mult))
            
            
                
        elif self.canvas.mode == 'edges' and self.current_letter != 0:
            if not hasattr(self.canvas, 'selected_node'):
                self.canvas.selected_node = self
            else:
                selected_node = self.canvas.selected_node
                if selected_node != self:
                    if self.current_letter == 1 and selected_node.current_letter == 1:
                        return
                    if selected_node in self.nodes_to:
                        return
                        
                    if selected_node not in self.nodes_from:
                        midx = (selected_node.x + self.x)//2
                        midy = (selected_node.y + self.y)//2
                        arrow_to_mid = self.canvas.create_line(selected_node.x, selected_node.y, midx, midy,
                                                fill='black', arrow=tk.LAST)  # Add arrowhead
                        mid_to_end = self.canvas.create_line(midx, midy, self.x, self.y, fill='black')
                        mult = self.canvas.create_text(midx, midy, text="1", font = ('Arial', self.radius)) 
                        p_on_left_click_edge = partial(self.on_left_click_edge, mult)
                        p_on_right_click_edge = partial(self.on_right_click_edge, mult)
                        self.canvas.tag_bind(mult, '<Button-1>', p_on_left_click_edge)
                        self.canvas.tag_bind(mult, '<Button-3>', p_on_right_click_edge)
                        selected_node.arrow_to.add((self, arrow_to_mid, mid_to_end, mult))
                        selected_node.nodes_to.add(self)
                        self.arrow_from.add((selected_node, arrow_to_mid, mid_to_end, mult))
                        self.nodes_from.add(selected_node)
                    # else:
                        # for tup in self.arrow_from:
                            # if selected_node == tup[0]:
                                # self.canvas.itemconfig(tup[3], text=str(1+int(self.canvas.itemcget(tup[3], "text"))))
                    del self.canvas.selected_node
                else:
                    del self.canvas.selected_node

    def on_left_click_edge(self, w, event):
        self.canvas.itemconfig(w, text=str(1+int(self.canvas.itemcget(w,"text"))))
        
    def on_right_click_edge(self, w, event):
        if int(self.canvas.itemcget(w,"text")) > 1:
            self.canvas.itemconfig(w, text=str(-1+int(self.canvas.itemcget(w,"text"))))
        elif int(self.canvas.itemcget(w,"text")) == 1:
            t = (0,0,0,0)
            for tup in self.arrow_from:
                if tup[3] == w:
                    t = tup
            sel = t[0]
            am = t[1]
            me = t[2]
            self.nodes_from.discard(sel)
            sel.nodes_to.discard(self)
            self.arrow_from.discard(t)
            sel.arrow_to.discard((self,am,me,w))
            self.canvas.delete(am)
            self.canvas.delete(me)
            self.canvas.delete(w)

class GridApp:
    def __init__(self, root, rows, cols, node_spacing, node_radius):
        self.root = root
        self.root.title("Node Grid")

        self.canvas = tk.Canvas(root, width=cols*node_spacing, height=rows*node_spacing)
        self.canvas.pack()

        self.nodes = []
        for row in range(rows):
            for col in range(cols):
                x = col * node_spacing + (node_spacing // 2)
                y = row * node_spacing + (node_spacing // 2)
                self.nodes.append(Node(self, self.canvas, x, y, node_radius))

        self.modes = ['set nodes', 'move nodes', 'edges', 'mutate']  # Add more modes as needed
        self.setup_modes()
        self.canvas.mode = 'set nodes'
        self.set_mode('set nodes')

    def setup_modes(self):
        self.mode_buttons = []

        for mode in self.modes:
            button = tk.Button(self.root, text=mode.capitalize(), command=lambda m=mode: self.set_mode(m))
            button.pack(side='left')
            self.mode_buttons.append(button)

    def set_mode(self, mode):
        for button in self.mode_buttons:
            button.config(state='normal')
        old_mode = self.canvas.mode
        self.canvas.mode = mode
        self.mode_buttons[self.modes.index(mode)].config(state='disabled')

        if old_mode == 'set nodes' and mode != 'set nodes':
            for node in self.nodes:
                if node.current_letter == 0:
                    node.canvas.itemconfigure(node.id, state = tk.HIDDEN)
                    node.canvas.itemconfigure(node.text_id, state = tk.HIDDEN)
        elif old_mode != 'set nodes' and mode == 'set nodes':
            for node in self.nodes:
                if node.current_letter == 0:
                    node.canvas.itemconfigure(node.id, state = tk.NORMAL)
                    node.canvas.itemconfigure(node.text_id, state = tk.NORMAL)

        

if __name__ == "__main__":
    cfg_numrows = 5
    cfg_numcols = 5
    cfg_noderadius = 10
    cfg_nodespacing = 100
    cfg = 'quiver_config.txt'
    try:
        with open(cfg, 'r') as file:
            for line in file:
                line_split = line.split('=')
                if line_split[0] == 'num_rows':
                    cfg_numrows = int(line_split[1])
                elif line_split[0] == 'num_columns':
                    cfg_numcols = int(line_split[1])
                elif line_split[0] == 'node_radius':
                    cfg_noderadius = int(line_split[1])
                elif line_split[0] == 'node_spacing':
                    cfg_nodespacing = int(line_split[1])
    except FileNotFoundError:
        print("Config file not found. Please create a flip_config.txt file and format as per the instructions on GitHub.")
    except Exception as e:
        print("An error occurred: ", e)

    root = tk.Tk()
    app = GridApp(root, rows=cfg_numrows, cols=cfg_numcols, node_spacing=cfg_nodespacing, node_radius=cfg_noderadius)
    root.mainloop()
