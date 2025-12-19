import tkinter as tk
from tkinter import messagebox
import heapq
from collections import deque
import time

# ==========================================
# 1. Backend: Logic & Algorithms (زي ما هو)
# ==========================================

class FarmerLogic:
    def __init__(self):
        self.initial_state = (0, 0, 0, 0)
        self.goal_state = (1, 1, 1, 1)

    def is_valid(self, state):
        f, w, s, c = state
        if w == s and f != w: return False
        if s == c and f != s: return False
        return True

    def get_successors(self, state):
        successors = []
        f, w, s, c = state
        possible_moves = [0, 1, 2, 3] 
        new_f = 1 - f
        
        for move in possible_moves:
            new_state = list(state)
            new_state[0] = new_f
            
            if move > 0: 
                if state[move] == f:
                    new_state[move] = 1 - state[move]
                else:
                    continue
            
            if self.is_valid(tuple(new_state)):
                successors.append(tuple(new_state))
        return successors

    def heuristic(self, state):
        return sum([1 for item in state if item == 0])

    def solve_bfs(self):
        queue = deque([(self.initial_state, [self.initial_state])])
        visited = set([self.initial_state])
        while queue:
            current, path = queue.popleft()
            if current == self.goal_state: return path
            for succ in self.get_successors(current):
                if succ not in visited:
                    visited.add(succ)
                    queue.append((succ, path + [succ]))
        return None

    def solve_dfs(self):
        stack = [(self.initial_state, [self.initial_state])]
        visited = set()
        while stack:
            current, path = stack.pop()
            if current == self.goal_state: return path
            if current not in visited:
                visited.add(current)
                for succ in self.get_successors(current):
                    stack.append((succ, path + [succ]))
        return None

    def solve_ucs(self):
        pq = []
        heapq.heappush(pq, (0, self.initial_state, [self.initial_state]))
        cost_so_far = {self.initial_state: 0}
        while pq:
            cost, current, path = heapq.heappop(pq)
            if current == self.goal_state: return path
            for succ in self.get_successors(current):
                new_cost = cost + 1
                if succ not in cost_so_far or new_cost < cost_so_far[succ]:
                    cost_so_far[succ] = new_cost
                    heapq.heappush(pq, (new_cost, succ, path + [succ]))
        return None

    def solve_ids(self):
        depth_limit = 0
        while True:
            result = self.dls(self.initial_state, [self.initial_state], depth_limit)
            if result is not None: return result
            depth_limit += 1
            if depth_limit > 25: return None

    def dls(self, current, path, limit):
        if current == self.goal_state: return path
        if limit <= 0: return None
        for succ in self.get_successors(current):
            if succ not in path:
                result = self.dls(succ, path + [succ], limit - 1)
                if result is not None: return result
        return None

    def solve_astar(self):
        start_node = self.initial_state
        g_start = 0
        h_start = self.heuristic(start_node)
        pq = []
        heapq.heappush(pq, (g_start + h_start, g_start, start_node, [start_node]))
        cost_so_far = {start_node: 0}
        while pq:
            f, g, current, path = heapq.heappop(pq)
            if current == self.goal_state: return path
            for succ in self.get_successors(current):
                new_g = g + 1
                if succ not in cost_so_far or new_g < cost_so_far[succ]:
                    cost_so_far[succ] = new_g
                    new_f = new_g + self.heuristic(succ)
                    heapq.heappush(pq, (new_f, new_g, succ, path + [succ]))
        return None

# ==========================================
# 2. Frontend: Responsive GUI
# ==========================================

class FarmerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Responsive AI Farmer Solver")
        # Make the window start larger
        self.root.geometry("800x600")
        
        self.logic = FarmerLogic()
        self.current_state = (0, 0, 0, 0)
        self.is_animating = False

        # --- Layout Configuration ---
        # Allow the root window to resize the canvas frame
        self.root.rowconfigure(0, weight=1) 
        self.root.columnconfigure(0, weight=1)

        # Main Container
        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        # 1. Canvas Area (Responsive)
        # weight=1 means it will take up all extra space
        self.canvas = tk.Canvas(main_frame, bg="#e0f7fa", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind the resize event
        self.canvas.bind("<Configure>", self.on_resize)

        self.items_data = {
            'F': {'emoji': '👨‍🌾', 'name': 'Farmer'},
            'W': {'emoji': '🐺', 'name': 'Wolf'},
            'S': {'emoji': '🐑', 'name': 'Sheep'},
            'C': {'emoji': '🥬', 'name': 'Cabbage'}
        }

        # 2. Controls Area (Bottom)
        ctrl_frame = tk.Frame(root, bd=2, relief="groove")
        ctrl_frame.pack(fill="x", side="bottom", padx=10, pady=5)

        # Left: Manual Play
        manual_frame = tk.Frame(ctrl_frame)
        manual_frame.pack(side="left", padx=10, pady=5)
        tk.Label(manual_frame, text="🎮 Manual Play", font=("Arial", 10, "bold")).pack()
        
        btn_frame = tk.Frame(manual_frame)
        btn_frame.pack()
        tk.Button(btn_frame, text="Farmer", command=lambda: self.manual_move(0)).grid(row=0, column=0, pady=2)
        tk.Button(btn_frame, text="+ Wolf", command=lambda: self.manual_move(1)).grid(row=0, column=1, padx=2)
        tk.Button(btn_frame, text="+ Sheep", command=lambda: self.manual_move(2)).grid(row=1, column=0, pady=2)
        tk.Button(btn_frame, text="+ Cabbage", command=lambda: self.manual_move(3)).grid(row=1, column=1, padx=2)

        # Center: Speed Control
        speed_frame = tk.Frame(ctrl_frame, bd=1, relief="sunken", padx=10)
        speed_frame.pack(side="left", padx=20, expand=True) # expand to center it
        tk.Label(speed_frame, text="⏱️ Speed", font=("Arial", 9)).pack()
        self.speed_scale = tk.Scale(speed_frame, from_=200, to=1500, orient="horizontal", length=150)
        self.speed_scale.set(600)
        self.speed_scale.pack()

        # Right: AI Algorithms
        ai_frame = tk.Frame(ctrl_frame)
        ai_frame.pack(side="right", padx=10, pady=5)
        tk.Label(ai_frame, text="🤖 AI Auto-Solve", font=("Arial", 10, "bold")).pack(pady=2)

        alg_grid = tk.Frame(ai_frame)
        alg_grid.pack()
        tk.Button(alg_grid, text="BFS", bg="#fff9c4", width=6, command=lambda: self.run_algorithm("BFS")).grid(row=0, column=0, padx=1)
        tk.Button(alg_grid, text="DFS", bg="#ffe0b2", width=6, command=lambda: self.run_algorithm("DFS")).grid(row=0, column=1, padx=1)
        tk.Button(alg_grid, text="UCS", bg="#b2dfdb", width=6, command=lambda: self.run_algorithm("UCS")).grid(row=0, column=2, padx=1)
        tk.Button(alg_grid, text="IDS", bg="#e1bee7", width=6, command=lambda: self.run_algorithm("IDS")).grid(row=1, column=0, padx=1)
        tk.Button(alg_grid, text="A*", bg="#c8e6c9", width=14, command=lambda: self.run_algorithm("A*")).grid(row=1, column=1, columnspan=2, padx=1)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")
        status_lbl = tk.Label(root, textvariable=self.status_var, font=("Arial", 11), fg="blue", bg="#f0f0f0")
        status_lbl.pack(side="bottom", fill="x")
        
        tk.Button(ctrl_frame, text="Reset", command=self.reset_game, fg="red").pack(side="right", padx=5)

    def on_resize(self, event):
        """Called whenever window is resized"""
        self.draw_responsive_state()

    def draw_responsive_state(self):
        """Draws elements based on current canvas width/height"""
        self.canvas.delete("all")
        
        # Get current dimensions
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Avoid drawing if window is too small (startup glitch prevention)
        if w < 50 or h < 50: return

        # Dynamic Coordinates
        river_start = w * 0.3
        river_end = w * 0.7
        
        # Draw Banks
        self.canvas.create_rectangle(0, 0, river_start, h, fill="#a5d6a7", outline="") # Left
        self.canvas.create_rectangle(river_end, 0, w, h, fill="#a5d6a7", outline="")   # Right
        self.canvas.create_rectangle(river_start, 0, river_end, h, fill="#4fc3f7", outline="") # River

        # Labels
        self.canvas.create_text(river_start/2, h - 30, text="Left Bank", font=("Arial", 14, "bold"))
        self.canvas.create_text(river_end + (w-river_end)/2, h - 30, text="Right Bank", font=("Arial", 14, "bold"))

        # Draw Items
        f, wolf, sheep, cab = self.current_state
        positions = [f, wolf, sheep, cab]
        keys = ['F', 'W', 'S', 'C']
        
        # Calculate vertical spacing dynamically
        start_y = h * 0.2
        gap_y = h * 0.15
        
        for i, val in enumerate(positions):
            key = keys[i]
            # X Position: Center of Left Bank OR Center of Right Bank
            x_pos = (river_start / 2) if val == 0 else (river_end + (w - river_end) / 2)
            y_pos = start_y + (i * gap_y)
            
            # Draw Emoji
            font_size = int(h * 0.08) # Dynamic Font Size based on height
            if font_size < 12: font_size = 12
            
            self.canvas.create_text(x_pos, y_pos, text=self.items_data[key]['emoji'], 
                                    font=("Arial", font_size), tags="item")
            self.canvas.create_text(x_pos, y_pos + (font_size/1.5), text=self.items_data[key]['name'], 
                                    font=("Arial", int(font_size/3)), tags="item")

    def manual_move(self, item_idx):
        if self.is_animating: return
        f = self.current_state[0]
        new_state_list = list(self.current_state)
        new_state_list[0] = 1 - f
        if item_idx > 0:
            if self.current_state[item_idx] != f:
                messagebox.showerror("Error", "Item not with Farmer!")
                return
            new_state_list[item_idx] = 1 - f
        
        new_state = tuple(new_state_list)
        self.current_state = new_state
        self.draw_responsive_state()

        if not self.logic.is_valid(new_state):
            self.status_var.set("💀 Game Over!")
            messagebox.showerror("Failed", "Invalid Move! Game Over.")
            self.reset_game()
        elif new_state == (1, 1, 1, 1):
            self.status_var.set("🎉 WINNER!")
            messagebox.showinfo("Success", "Puzzle Solved!")

    def run_algorithm(self, name):
        if self.is_animating: return
        self.reset_game()
        self.is_animating = True
        self.status_var.set(f"Running {name}...")
        self.root.update()

        path = []
        if name == "BFS": path = self.logic.solve_bfs()
        elif name == "DFS": path = self.logic.solve_dfs()
        elif name == "UCS": path = self.logic.solve_ucs()
        elif name == "IDS": path = self.logic.solve_ids()
        elif name == "A*":  path = self.logic.solve_astar()

        if path:
            self.animate_step(path, 0, name)
        else:
            self.status_var.set(f"{name} Failed.")
            self.is_animating = False

    def animate_step(self, path, index, algo_name):
        if not self.is_animating: return
        
        if index >= len(path):
            self.is_animating = False
            self.status_var.set(f"✅ {algo_name} Finished!")
            return

        state = path[index]
        self.current_state = state
        self.draw_responsive_state()
        self.status_var.set(f"{algo_name}: Step {index}/{len(path)-1}")

        delay = self.speed_scale.get()
        self.root.after(delay, lambda: self.animate_step(path, index + 1, algo_name))

    def reset_game(self):
        self.is_animating = False
        self.current_state = (0, 0, 0, 0)
        self.draw_responsive_state()
        self.status_var.set("Ready.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FarmerApp(root)
    root.mainloop()