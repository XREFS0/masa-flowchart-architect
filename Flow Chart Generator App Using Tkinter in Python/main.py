"""
MASA 14_Flow Chart Generator App Using Tkinter in Python with Source Code
Developer: MASA
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from graphviz import Digraph
import ast
from PIL import Image, ImageGrab


def generate_flowchart_from_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        messagebox.showerror("Syntax Error", "Invalid Python code")
        return

    dot = Digraph(format="png")
    dot.attr(rankdir="TB")

    counter = 0
    last_nodes = []

    def new_node(label, shape="rectangle"):
        nonlocal counter
        node_id = f"N{counter}"
        dot.node(node_id, label, shape=shape)
        for parent in last_nodes:
            dot.edge(parent, node_id)
        last_nodes.clear()
        last_nodes.append(node_id)
        counter += 1
        return node_id

    new_node("Start", "oval")

    def visit(body):
        nonlocal last_nodes
        for stmt in body:
            if isinstance(stmt, ast.Assign):
                new_node("Assignment")
            elif isinstance(stmt, ast.AugAssign):
                new_node("Augmented Assignment")
            elif isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Call):
                    func_name = stmt.value.func.id if hasattr(stmt.value.func, "id") else "func"
                    new_node(f"Call: {func_name}")
                else:
                    new_node("Expression")
            elif isinstance(stmt, ast.If):
                decision_id = new_node("If Condition", "diamond")
                prev_last = last_nodes.copy()
                last_nodes.clear()
                visit(stmt.body)
                true_last = last_nodes.copy()
                last_nodes.clear()
                visit(stmt.orelse)
                false_last = last_nodes.copy()
                for n in prev_last:
                    dot.edge(n, decision_id)
                last_nodes.clear()
                last_nodes.extend(true_last + false_last)
            elif isinstance(stmt, ast.While):
                loop_id = new_node("While Loop", "diamond")
                prev_last = last_nodes.copy()
                last_nodes.clear()
                visit(stmt.body)
                for n in last_nodes:
                    dot.edge(n, loop_id)
                last_nodes.clear()
                last_nodes.append(loop_id)
            elif isinstance(stmt, ast.For):
                loop_id = new_node("For Loop", "diamond")
                prev_last = last_nodes.copy()
                last_nodes.clear()
                visit(stmt.body)
                for n in last_nodes:
                    dot.edge(n, loop_id)
                last_nodes.clear()
                last_nodes.append(loop_id)
            else:
                new_node(type(stmt).__name__)

    visit(tree.body)
    new_node("End", "oval")
    dot.render("code_flowchart", view=True)


class CanvasNode:
    def __init__(self, app, canvas, x, y, text, shape):
        self.app = app
        self.canvas = canvas
        self.text_label = text
        self.shape = shape
        self.lines = []

        if shape == "oval":
            self.body = canvas.create_oval(x, y, x + 120, y + 50, fill="lightgreen")
        elif shape == "diamond":
            self.body = canvas.create_polygon(
                x + 60, y, x + 120, y + 25, x + 60, y + 50, x, y + 25, fill="khaki"
            )
        else:
            self.body = canvas.create_rectangle(x, y, x + 120, y + 50, fill="lightblue")

        self.text = canvas.create_text(x + 60, y + 25, text=text)

        for item in (self.body, self.text):
            canvas.tag_bind(item, "<Button-1>", self.select)
            canvas.tag_bind(item, "<B1-Motion>", self.move)
            canvas.tag_bind(item, "<Double-Button-1>", self.edit_text)

    def center(self):
        x1, y1, x2, y2 = self.canvas.bbox(self.body)
        return (x1 + x2) // 2, (y1 + y2) // 2

    def select(self, event):
        self.app.selected_node = self
        self.app.last_x = event.x
        self.app.last_y = event.y

        if self.app.connecting:
            if not self.app.src_node:
                self.app.src_node = self
                self.app.canvas.itemconfig(self.body, outline="red", width=2)
            else:
                tgt_node = self
                x1, y1 = self.app.src_node.center()
                x2, y2 = tgt_node.center()
                line = self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST)
                self.app.src_node.lines.append((line, tgt_node))
                self.app.canvas.itemconfig(self.app.src_node.body, outline="black", width=1)
                self.app.connecting = False
                self.app.src_node = None

    def move(self, event):
        dx = event.x - self.app.last_x
        dy = event.y - self.app.last_y
        self.canvas.move(self.body, dx, dy)
        self.canvas.move(self.text, dx, dy)
        self.app.last_x, self.app.last_y = event.x, event.y
        self.update_lines()

    def update_lines(self):
        for line, target in self.lines:
            x1, y1 = self.center()
            x2, y2 = target.center()
            self.canvas.coords(line, x1, y1, x2, y2)
        for node in self.app.nodes:
            for line, target in node.lines:
                if target == self:
                    x1, y1 = node.center()
                    x2, y2 = self.center()
                    self.canvas.coords(line, x1, y1, x2, y2)

    def delete(self):
        for line, target in self.lines:
            self.canvas.delete(line)
        for node in self.app.nodes:
            node.lines = [(l, t) for l, t in node.lines if t != self]
        self.canvas.delete(self.body)
        self.canvas.delete(self.text)

    def edit_text(self, event):
        new_text = simpledialog.askstring("Edit Node Text", "Enter new text:", initialvalue=self.text_label)
        if new_text:
            self.text_label = new_text
            self.canvas.itemconfig(self.text, text=new_text)


class FlowchartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MASA FlowChart Architect")
        self.root.geometry("900x600")

        self.nodes = []
        self.selected_node = None
        self.last_x = self.last_y = 0
        self.connecting = False
        self.src_node = None

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.create_code_tab(notebook)
        self.create_canvas_tab(notebook)

    def create_code_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Code → Flowchart")

        ttk.Label(tab, text="Paste Python Code").pack(pady=5)
        self.code_box = tk.Text(tab, height=18)
        self.code_box.pack(fill="both", expand=True, padx=10)

        ttk.Button(
            tab,
            text="Generate Flowchart",
            command=lambda: generate_flowchart_from_code(self.code_box.get("1.0", tk.END)),
        ).pack(pady=10)

    def create_canvas_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Drag & Drop Canvas")

        toolbar = ttk.Frame(tab)
        toolbar.pack(pady=5)

        ttk.Button(toolbar, text="Start", command=lambda: self.add_node("Start", "oval")).pack(
            side="left", padx=5
        )
        ttk.Button(toolbar, text="Process", command=lambda: self.add_node("Process", "rect")).pack(
            side="left", padx=5
        )
        ttk.Button(toolbar, text="Decision", command=lambda: self.add_node("Decision", "diamond")).pack(
            side="left", padx=5
        )
        ttk.Button(toolbar, text="End", command=lambda: self.add_node("End", "oval")).pack(
            side="left", padx=5
        )

        ttk.Button(toolbar, text="Connect", command=self.connect_nodes).pack(side="left", padx=10)
        ttk.Button(toolbar, text="Delete Selected", command=self.delete_node).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Save Canvas", command=self.save_canvas).pack(side="left", padx=5)

        self.canvas = tk.Canvas(tab, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.track_mouse)

    def track_mouse(self, event):
        self.last_x, self.last_y = event.x, event.y

    def add_node(self, text, shape):
        node = CanvasNode(self, self.canvas, 50, 50, text, shape)
        self.nodes.append(node)

    def connect_nodes(self):
        self.connecting = True
        self.src_node = None
        messagebox.showinfo("Connect Nodes", "Click the source node, then the target node to connect.")

    def delete_node(self):
        if not self.selected_node:
            return
        self.selected_node.delete()
        self.nodes.remove(self.selected_node)
        self.selected_node = None

    def save_canvas(self):
        if not self.nodes:
            messagebox.showwarning("Warning", "No nodes to save!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg")]
        )
        if not file_path:
            return

        self.canvas.update()

        try:
            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()

            img = ImageGrab.grab(bbox=(x, y, x1, y1))

            if file_path.lower().endswith(".jpg"):
                img = img.convert("RGB")

            img.save(file_path)
            messagebox.showinfo("Saved", f"Flowchart saved as {file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    FlowchartApp(root)
    root.mainloop()
