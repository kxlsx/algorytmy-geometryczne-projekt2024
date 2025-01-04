import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import json
import tkinter as tk
from tkinter import filedialog


#  np. tak: segments = load_from_file("Ścieżka\\do\\pliku\\segments.json")
def load_from_file(filepath):
    with open(filepath, 'r') as f:
        segments = json.load(f)
    return segments


class Creator:
    def __init__(self):
        plt.style.use('grayscale')
        self.segments = []
        self.fig, self.ax = plt.subplots()
        self.start_point = None

        button_ax = self.fig.add_axes([0.1, 0.01, 0.15, 0.055])
        self.save_button = Button(button_ax, 'Zapisz')
        self.save_button.on_clicked(self.save_segments_to_file)
        
        button_ax = self.fig.add_axes([0.68, 0.01, 0.3, 0.055])
        self.gen_button = Button(button_ax, 'Wygeneruj losowo odcinki')
        self.gen_button.on_clicked(self.clear)
        self.gen_button.on_clicked(self.generate_random_segments_dialog)
        
        button_ax = self.fig.add_axes([0.4, 0.01, 0.2, 0.055])
        self.clear_button = Button(button_ax, 'Wyczyść')
        self.clear_button.on_clicked(self.clear)
        
        
    def is_vertical(self, x1, y1, x2, y2):
        return x1 == x2
    
    
    def has_proper_x(self, x1, y1, x2, y2):
        for point1, point2 in self.segments:
            if point1[0] == x1 and point1[1] != y1:
                return False
            if point2[0] == x2 and point2[1] != y2:
                return False
            
        return True
    
    
    def has_overlap(self, x1, y1, x2, y2):
        slope1 = (y2-y1)/(x2-x1)
        y_intersection_1 = y1 - slope1*x1
        
        for point1, point2 in self.segments:
            slope2 = (point2[1]-point1[1])/(point2[0]-point1[0])
            y_intersection_2 = point1[1] - slope2*point1[0]
            
            if slope1 == slope2:
                if y_intersection_1 == y_intersection_2:
                    
                    if (x1 < point1[0] < x2) or (x1 < point2[0] < x2):
                        return True 
            
            else:
                x = (y_intersection_2 - y_intersection_1)/(slope1 - slope2)
                y = slope1*x + y_intersection_1
                
                if (x1 < x < x2) and (min(y1, y2) < y < max(y1, y2)) and (point1[0] < x < point2[0]) and (min(point1[1], point2[1]) < y < max(point1[1], point2[1])):
                    return True
                
        return False
                
                
    def add_segment(self, x1, y1, x2, y2):
        if self.is_vertical(x1, y1, x2, y2):
            self.start_point = None
            return False
            
        if not self.has_proper_x(x1, y1, x2, y2):
            self.start_point = None
            return False
        
        if self.has_overlap(x1, y1, x2, y2):
            self.start_point = None
            return False
        
        self.segments.append( ((x1, y1), (x2, y2)) )
        self.ax.plot([x1, x2], [y1, y2], marker='.', color='black')
        self.fig.canvas.draw()
        
        return True


    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        if self.start_point is None:
            self.start_point = (event.xdata, event.ydata)
        else:
            end_point = (event.xdata, event.ydata)
            
            x1, y1 = self.start_point
            x2, y2 = end_point
            if x1 > x2: 
                x1, x2 = x2, x1
                y1, y2 = y2, y1
                
            self.add_segment(x1, y1, x2, y2)            
            self.start_point = None


    def generate_random_segments_dialog(self, event):
        dialog = tk.Toplevel()
        dialog.title("Parametry do tworzenia losowych odcinków")

        self.count_var = tk.StringVar(value="100")
        self.xmin_var = tk.StringVar(value="0")
        self.xmax_var = tk.StringVar(value="100")
        self.ymin_var = tk.StringVar(value="0")
        self.ymax_var = tk.StringVar(value="100")

        tk.Label(dialog, text="Liczba odcinków").grid(row = 0, column = 0, padx = 5, pady = 5, sticky = "e")
        tk.Entry(dialog, textvariable=self.count_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="x_min").grid(row = 1, column = 0, padx = 5, pady = 5, sticky = "e")
        tk.Entry(dialog, textvariable = self.xmin_var).grid(row = 1, column = 1, padx = 5, pady = 5)

        tk.Label(dialog, text="x_max").grid(row = 2, column = 0, padx = 5, pady = 5, sticky = "e")
        tk.Entry(dialog, textvariable = self.xmax_var).grid(row = 2, column = 1, padx = 5, pady = 5)

        tk.Label(dialog, text="y_min").grid(row = 3, column = 0, padx = 5, pady = 5, sticky = "e")
        tk.Entry(dialog, textvariable = self.ymin_var).grid(row = 3, column = 1, padx = 5, pady = 5)

        tk.Label(dialog, text="y_max").grid(row = 4, column = 0, padx = 5, pady = 5, sticky = "e")
        tk.Entry(dialog, textvariable = self.ymax_var).grid(row = 4, column = 1, padx = 5, pady = 5)

        tk.Button(dialog, text="OK", command=lambda: self.on_dialog_ok(dialog)).grid(row = 5, column = 0, columnspan = 2, pady = 10)

        tk.Button(dialog, text="Anuluj", command=dialog.destroy).grid(row = 6, column = 0, columnspan = 2, pady = 5)

        dialog.grab_set()


    def on_dialog_ok(self, dialog):
        try:
            count = int(self.count_var.get())
            x_min = float(self.xmin_var.get())
            x_max = float(self.xmax_var.get())
            y_min = float(self.ymin_var.get())
            y_max = float(self.ymax_var.get())

            self.generate_random_segments(count, x_min, x_max, y_min, y_max)
        except ValueError:
            print("Wprowadzono błędne parametry")
            return

        dialog.destroy()
        
    
    def generate_random_segments(self, count, x_min, x_max, y_min, y_max):
        while len(self.segments) < count:
            x1, y1 = np.random.uniform(x_min, x_max), np.random.uniform(y_min, y_max)
            x2, y2 = np.random.uniform(x_min, x_max), np.random.uniform(y_min, y_max)
            
            if x1 > x2: 
                x1, x2 = x2, x1
                y1, y2 = y2, y1
                
            self.add_segment(x1, y1, x2, y2)


    def save_segments_to_file(self, event):
        root = tk.Tk()
        root.withdraw()

        filepath = filedialog.asksaveasfilename(
            defaultextension = ".json",
            filetypes = [("JSON files", "*.json"), ("All files", "*.*")],
            initialfile = "segments.json",
            title = "Zapisz listę odcinków do pliku"
            )

        if filepath:
            with open(filepath, 'w') as f:
                json.dump(self.segments, f)
                
                
    def clear(self, event):
        self.segments = []
        self.ax.clear()
        self.ax.set_title("Naciśnij myszką, aby dodać punkt lub wybierz opcję z dolnego menu")
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.fig.canvas.draw()


    def run(self):
        self.ax.set_title("Naciśnij myszką, aby dodać punkt lub wybierz opcję z dolnego menu")
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        plt.show()


creator = Creator()
creator.run()
