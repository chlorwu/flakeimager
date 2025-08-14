# Welcome to the new and enhanced FlakeImager!
# By Chloe Wu, 2025 SIP intern @ PHY-01 in Yan Lab under Carlos Gonzalez's mentorship.
# NEW FEATURES:
    # Actually know what tool you're on with the tool indicator at the top of the screen!
    # See where your line is going to be drawn with live line previews in measurement and color comparison tools!
    # Clear all button!
    # Create a scale bar with the scale bar tool with adjustable magnification and length! (Screenshot and paste image into your work!)

# IMPORTANT: CHANGE THIS TO YOUR OWN FILE PATH (keep single quotes)
file_path = '/Users/chloewu/Downloads/' 
# PLAY AROUND WITH THIS TO CHANGE THE SIZE OF THE WINDOW
scale = 0.5 

# Thank you to Bruce Li at the Velasco Lab for making the original FlakeImager, which this is based on.
# Email chloe.yixuan.wu@gmail.com or Discord message @chlorine_4921 with any questions, suggestions or requests, and I'll get back to you within 24 hrs.

#!/usr/bin/env python3
from tkinter import *
from tkinter import filedialog, ttk
import numpy as np
from PIL import Image
import os
import math
import math

root = Tk()


class FlakeImager:
    def __init__(self, master):
        self.master = master
        self.canvas = None
        self.background_image = None
        self.current_tool = "none"
        self.pixels_to_dist = 200./325 / scale  # pixel to distance conversion factor
        self.pixels_to_dist = 200./325 / scale  # pixel to distance conversion factor
        
        # Tool-specific variables
        self.measure_positions = {}
        self.temp_line = None  # For real-time line preview
        
        self.color_positions1 = {}
        self.color_positions2 = {}
        self.color_temp_line = None  # For real-time color comparison line preview
        
        self.scale_magnification = StringVar(value="20X")
        self.scale_length = StringVar(value="10")
        self.scale_bar_placed = False  # Track if scale bar is already placed
        self.scale_frame = None  # Will hold reference to scale frame
        
        self.setup_ui()
        self.load_image()
        
    def setup_ui(self):
        # Main canvas
        self.canvas = Canvas(self.master)
        self.canvas.pack(fill=BOTH, expand=1)
        
        # Control frame at bottom
        control_frame = Frame(self.master, bg='lightgray', height=145)
        control_frame = Frame(self.master, bg='lightgray', height=145)
        control_frame.pack(side=BOTTOM, fill=X)
        control_frame.pack_propagate(False)
        
        # Top row for tool indicator and clear button
        top_row = Frame(control_frame, bg='lightgray')
        top_row.pack(side=TOP, fill=X, padx=10, pady=0)
        top_row.pack(side=TOP, fill=X, padx=10, pady=0)
        
        # Current tool indicator
        self.tool_indicator = Label(top_row, text="Current Tool: None - Select a tool to begin", 
                                  font=('Arial', 11, 'bold'), bg='white', relief=RIDGE, height=2)
        self.tool_indicator.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        # Clear button
        clear_button = Button(top_row, text="Clear All", 
                             command=self.clear_all,
                             bg='lightcoral', width=15, height=2, font=('Arial', 10, 'bold'))
        clear_button.pack(side=RIGHT)
        
        # Bottom row for main controls
        bottom_row = Frame(control_frame, bg='lightgray')
        bottom_row.pack(side=BOTTOM, fill=BOTH, expand=True, padx=10, pady=3)
        bottom_row.pack(side=BOTTOM, fill=BOTH, expand=True, padx=10, pady=3)
        
        # Tool selection frame
        tool_frame = LabelFrame(bottom_row, text="Tools", font=('Arial', 11, 'bold'), width=140)
        tool_frame.pack(side=LEFT, padx=(0, 10), fill=Y)
        tool_frame.pack_propagate(False)
        
        # Inner frame to center buttons
        button_container = Frame(tool_frame)
        button_container.pack(expand=True, fill=BOTH, padx=3, pady=0)
        button_container.pack(expand=True, fill=BOTH, padx=3, pady=0)
        
        # Tool buttons with consistent sizing
        Button(button_container, text="Measure Distance", 
               command=lambda: self.set_tool("measure"),
               bg='lightblue', width=15, height=1, font=('Arial', 10)).pack(pady=2, fill=X)
        
        Button(button_container, text="Color Compare", 
               command=lambda: self.set_tool("color"),
               bg='lightgreen', width=15, height=1, font=('Arial', 10)).pack(pady=2, fill=X)
        
        Button(button_container, text="Scale Bar", 
               command=lambda: self.set_tool("scale"),
               bg='lightyellow', width=15, height=1, font=('Arial', 10)).pack(pady=2, fill=X)
        
        # Measurement display frame
        measure_frame = LabelFrame(bottom_row, text="Measurement Results", font=('Arial', 11, 'bold'), width=400)
        measure_frame.pack(side=LEFT, padx=(0, 5), fill=Y)
        measure_frame = LabelFrame(bottom_row, text="Measurement Results", font=('Arial', 11, 'bold'), width=400)
        measure_frame.pack(side=LEFT, padx=(0, 5), fill=Y)
        measure_frame.pack_propagate(False)
        
        self.distance_indicator = Label(measure_frame, text="Distance: Select Measure tool and drag on image", 
                                      relief=RIDGE, height=3, wraplength=400, justify=LEFT,
                                      font=('Arial', 10))
        self.distance_indicator.pack(fill=X, padx=10, pady=2)
        self.distance_indicator.pack(fill=X, padx=10, pady=2)
        
        self.color_diff_indicator = Label(measure_frame, text="Color Contrast: Select Color Compare tool and draw two lines", 
                                        relief=RIDGE, height=3, wraplength=300, justify=LEFT,
                                        font=('Arial', 10))
        self.color_diff_indicator.pack(fill=X, padx=10, pady=2)
        self.color_diff_indicator.pack(fill=X, padx=10, pady=2)
        
        # Scale bar settings frame
        self.scale_frame = LabelFrame(bottom_row, text="Scale Bar Settings", font=('Arial', 11, 'bold'), width=450)
        self.scale_frame.pack_propagate(False)
        
        # Padding container
        scale_container = Frame(self.scale_frame)
        scale_container.pack(expand=True, fill=BOTH, padx=10, pady=2)
        scale_container.pack(expand=True, fill=BOTH, padx=10, pady=2)
        
        Label(scale_container, text="Magnification:", font=('Arial', 10)).pack(pady=1)
        
        # Radio button frame for magnification selection
        magnif_frame = Frame(scale_container)
        magnif_frame.pack(pady=2)
        magnif_frame.pack(pady=2)
        
        # Radio buttons in a 1x4 grid
        magnif_options = ["5X", "10X", "20X", "50X"]
        for i, option in enumerate(magnif_options):
            rb = Radiobutton(magnif_frame, text=option, variable=self.scale_magnification, 
                           value=option, font=('Arial', 9), selectcolor='blue',
                           activebackground='white')
            rb.grid(row=0, column=i, padx=5, pady=0)
    

        # Container frame for label and entry side-by-side
        length_frame = Frame(scale_container)
        length_frame.pack(pady=(0, 0))

        # Label on the left
        Label(length_frame, text="Length (μm):", font=('Arial', 10)).pack(side='left', padx=(0, 5))  

        # Container frame for label and entry side-by-side
        length_frame = Frame(scale_container)
        length_frame.pack(pady=(0, 0))

        # Label on the left
        Label(length_frame, text="Length (μm):", font=('Arial', 10)).pack(side='left', padx=(0, 5))  
        
        # Entry on the right
        self.scale_entry = Entry(length_frame, textvariable=self.scale_length, width=20, font=('Arial', 11))
        self.scale_entry.pack(side='left')
        # Entry on the right
        self.scale_entry = Entry(length_frame, textvariable=self.scale_length, width=20, font=('Arial', 11))
        self.scale_entry.pack(side='left')
        self.scale_entry.config(state='normal', relief='sunken', bd=2)
        
        # Bind events for entering scale length
        self.scale_entry.bind('<Return>', self.validate_scale_length)
        self.scale_entry.bind('<FocusOut>', self.validate_scale_length)
        
        # Status for scale bar
        # Status for scale bar
        self.scale_status = Label(scale_container, text="Ready to place", font=('Arial', 9), 
                                 fg='green', wraplength=200, justify=CENTER)
        self.scale_status.pack(pady=2)
        self.scale_status.pack(pady=2)
        
        # Initially hide the scale frame (it will be shown when scale tool is selected)
        self.scale_frame.pack(side=RIGHT, padx=(0, 0), fill=Y)
        self.scale_frame.pack_forget()
        
    def validate_scale_length(self, event=None):
        """Validate the scale length input"""
        try:
            length = float(self.scale_length.get())
            if length <= 0:
                self.scale_status.config(text="Enter positive length", fg='red')
                return False
            else:
                self.scale_status.config(text="Ready to place", fg='green')
                return True
        except ValueError:
            self.scale_status.config(text="Invalid length", fg='red')
            return False
        
    def load_image(self):
        try:
            image_file_name = (os.path.split(filedialog.askopenfilename(initialdir=self.master))[-1]).split('.')[0]
            if not image_file_name:
                return
            
            self.prep_image_file(image_file_name)
            self.background_image = PhotoImage(file=file_path + image_file_name + ".png")
            self.canvas.create_image(0, 0, anchor=NW, image=self.background_image)
            
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def prep_image_file(self, image_name):
        path_name = file_path
        
        if os.path.isfile(path_name + image_name + ".png"):
            print("detected as PNG")
            pass
        elif os.path.isfile(path_name + image_name + ".jpg"):
            print("detected as JPG")
            img = Image.open(path_name + image_name + '.jpg')
            new_img = img.resize((math.floor(1200*scale), math.floor(800*scale)))
            new_img = img.resize((math.floor(1200*scale), math.floor(800*scale)))
            new_img.save(path_name + image_name + '.png', 'png')
            #os.remove(path_name + image_name + ".jpg")
            #os.remove(path_name + image_name + ".jpg")
            
            # Clean up other PNG files
            #for pic_file in os.listdir(path_name):
                #if (".png" in pic_file) and (pic_file != image_name + ".png"):
                   # os.remove(path_name + pic_file)
            #for pic_file in os.listdir(path_name):
                #if (".png" in pic_file) and (pic_file != image_name + ".png"):
                   # os.remove(path_name + pic_file)
    
    def set_tool(self, tool_name):
        self.current_tool = tool_name
        self.canvas.unbind('<ButtonPress-1>')
        self.canvas.unbind('<ButtonRelease-1>')
        self.canvas.unbind('<B1-Motion>')
        
        # Clear tool-specific elements when switching tools
        if tool_name != "measure":
            # Clear measurement line and reset distance display
            self.canvas.delete("measure_line")
            self.canvas.delete("temp_line")
            self.measure_positions = {}
            self.distance_indicator.config(text="Distance: Select Measure tool and drag on image")
            
        if tool_name != "color":
            # Clear color comparison lines and reset display
            self.canvas.delete("color_line1")
            self.canvas.delete("color_line2")
            self.canvas.delete("color_temp_line")
            self.color_positions1 = {}
            self.color_positions2 = {}
            self.color_diff_indicator.config(text="Color Contrast: Select Color Compare tool and draw two lines")
        
        # Always hide scale frame first
        if self.scale_frame.winfo_ismapped():
            self.scale_frame.pack_forget()
        
        if tool_name == "measure":
            self.tool_indicator.config(text="Current Tool: Measure Distance (Click and drag to measure)", bg='lightblue')
            self.canvas.bind('<ButtonPress-1>', self.measure_start)
            self.canvas.bind('<ButtonRelease-1>', self.measure_stop)
            self.canvas.bind('<B1-Motion>', self.measure_drag)
            
        elif tool_name == "color":
            self.tool_indicator.config(text="Current Tool: Color Compare (Draw two lines to compare)", bg='lightgreen')
            self.canvas.bind('<ButtonPress-1>', self.color_start)
            self.canvas.bind('<ButtonRelease-1>', self.color_stop)
            self.canvas.bind('<B1-Motion>', self.color_drag)
            
        elif tool_name == "scale":
            # Show scale frame when scale tool is selected
            self.scale_frame.pack(side=RIGHT, padx=(0, 0), fill=Y)
            
            # Force update
            self.scale_frame.update_idletasks()
            
            # Focus
            self.scale_entry.focus_set()
            
            if self.scale_bar_placed:
                self.tool_indicator.config(text="Current Tool: Scale Bar - Clear first to place a new scale bar", bg='orange')
            else:
                self.tool_indicator.config(text="Current Tool: Scale Bar - Click to place scale bar", bg='lightyellow')
                self.canvas.bind('<ButtonPress-1>', self.scale_click)
    
    def clear_all(self):
        self.canvas.delete("measure_line")
        self.canvas.delete("color_line1")
        self.canvas.delete("color_line2")
        self.canvas.delete("scale_bar")
        self.canvas.delete("temp_line")
        self.canvas.delete("color_temp_line")
        
        # Reset variables
        self.measure_positions = {}
        self.color_positions1 = {}
        self.color_positions2 = {}
        self.temp_line = None
        self.color_temp_line = None
        self.scale_bar_placed = False
        
        # Reset indicators
        self.distance_indicator.config(text="Distance: Select Measure tool and drag on image")
        self.color_diff_indicator.config(text="Color Contrast: Select Color Compare tool and draw two lines")
        self.scale_status.config(text="Ready to place", fg='green')
        
        # Update tool indicator if scale tool is active
        if self.current_tool == "scale":
            self.tool_indicator.config(text="Current Tool: Scale Bar - Click to place scale bar", bg='lightyellow')
            self.canvas.bind('<ButtonPress-1>', self.scale_click)
    
    # MEASUREMENT TOOL METHODS
    def measure_start(self, event):
        self.measure_positions['start'] = (event.x, event.y)
        self.canvas.delete("measure_line")
        self.canvas.delete("temp_line")
    
    def measure_drag(self, event):
        if 'start' in self.measure_positions:
            # Delete previous temporary line
            if self.temp_line:
                self.canvas.delete("temp_line")
            
            # Draw temporary line during drag
            self.temp_line = self.canvas.create_line(
                self.measure_positions['start'][0], 
                self.measure_positions['start'][1],
                event.x, event.y, 
                fill="red", width=3, dash=(5, 5), tags="temp_line"
            )
    
    def measure_stop(self, event):
        if 'start' not in self.measure_positions:
            return
            
        self.measure_positions['stop'] = (event.x, event.y)
        
        # Remove temporary line and draw final line
        self.canvas.delete("temp_line")
        self.canvas.create_line(
            self.measure_positions['start'][0], 
            self.measure_positions['start'][1],
            event.x, event.y, 
            fill="red", width=5, tags="measure_line"
        )
        
        # Calculate and display distance
        distance = self.calculate_distance()
        distance_display = (f"Distance: 5X: {distance*4:.2f}μm || "
                          f"10X: {distance*2:.2f}μm || "
                          f"20X: {distance:.2f}μm || "
        distance_display = (f"Distance: 5X: {distance*4:.2f}μm || "
                          f"10X: {distance*2:.2f}μm || "
                          f"20X: {distance:.2f}μm || "
                          f"50X: {distance/2.56:.2f}μm")
        self.distance_indicator.config(text=distance_display)
    
    def calculate_distance(self):
        if 'start' not in self.measure_positions or 'stop' not in self.measure_positions:
            return 0
        
        x1, y1 = self.measure_positions['start']
        x2, y2 = self.measure_positions['stop']
        pixel_distance = ((x2-x1)**2 + (y2-y1)**2)**0.5
        return pixel_distance * self.pixels_to_dist
    
    # COLOR COMPARISON TOOL METHODS
    def color_start(self, event):
        
        # Clear any existing temporary line
        self.canvas.delete("color_temp_line")
        
        if 'start' not in self.color_positions1:
            self.color_positions1['start'] = (event.x, event.y)
        elif 'stop' not in self.color_positions1:
            # First line not complete, ignore this click
            return
        elif 'start' not in self.color_positions2:
            self.color_positions2['start'] = (event.x, event.y)
        elif 'stop' not in self.color_positions2:
            # Second line not complete, ignore this click
            return
        # If both lines are complete, ignore additional clicks
    
    def color_drag(self, event):
        # Real-time line preview for color comparison
        if 'start' in self.color_positions1 and 'stop' not in self.color_positions1:
            # Drawing first line
            if self.color_temp_line:
                self.canvas.delete("color_temp_line")
            
            self.color_temp_line = self.canvas.create_line(
                self.color_positions1['start'][0], 
                self.color_positions1['start'][1],
                event.x, event.y, 
                fill="blue", width=2, dash=(3, 3), tags="color_temp_line"
            )
        elif 'start' in self.color_positions2 and 'stop' not in self.color_positions2:
            # Drawing second line
            if self.color_temp_line:
                self.canvas.delete("color_temp_line")
            
            self.color_temp_line = self.canvas.create_line(
                self.color_positions2['start'][0], 
                self.color_positions2['start'][1],
                event.x, event.y, 
                fill="green", width=2, dash=(3, 3), tags="color_temp_line"
            )
    
    def color_stop(self, event):
        # Clear temporary line
        self.canvas.delete("color_temp_line")
        
        if 'stop' not in self.color_positions1:
            self.color_positions1['stop'] = (event.x, event.y)
            self.canvas.create_line(
                self.color_positions1['start'][0], self.color_positions1['start'][1],
                event.x, event.y, 
                fill="blue", width=3, tags="color_line1"
            )
        elif 'stop' not in self.color_positions2:
            self.color_positions2['stop'] = (event.x, event.y)
            self.canvas.create_line(
                self.color_positions2['start'][0], self.color_positions2['start'][1],
                event.x, event.y, 
                fill="green", width=3, tags="color_line2"
            )
            
            # Analyze RGB when both lines are complete
            self.analyze_rgb()
    
    def analyze_rgb(self):
        if not all(['stop' in self.color_positions1, 'stop' in self.color_positions2]):
            return
        
        sample_number = 35
        
        # Get RGB samples from both lines
        line1_rgb = self.get_line_rgb_samples(
            self.color_positions1['start'], self.color_positions1['stop'], sample_number
        )
        line2_rgb = self.get_line_rgb_samples(
            self.color_positions2['start'], self.color_positions2['stop'], sample_number
        )
        
        # Calculate averages
        line1_avg = [sum(channel)/len(line1_rgb) for channel in zip(*line1_rgb)]
        line2_avg = [sum(channel)/len(line2_rgb) for channel in zip(*line2_rgb)]
        
        # Calculate contrast percentages
        rgb_contrast = []
        for i in range(3):
            if line2_avg[i] != 0:  # Avoid division by zero
                contrast = abs(1 - line1_avg[i]/line2_avg[i]) * 100
                rgb_contrast.append(f"{contrast:.2f}%")
            else:
                rgb_contrast.append("N/A")
        
        # Update display
        contrast_text = f"RGB Contrast - R: {rgb_contrast[0]} || G: {rgb_contrast[1]} || B: {rgb_contrast[2]}"
        contrast_text = f"RGB Contrast - R: {rgb_contrast[0]} || G: {rgb_contrast[1]} || B: {rgb_contrast[2]}"
        self.color_diff_indicator.config(text=contrast_text)
    
    def get_line_rgb_samples(self, start_pos, stop_pos, sample_count):
        x0, y0 = start_pos
        x1, y1 = stop_pos
        
        rgb_samples = []
        for i in range(sample_count + 1):
            if sample_count == 0:
                x, y = x0, y0
            else:
                x = int(x0 + (x1 - x0) * i / sample_count)
                y = int(y0 + (y1 - y0) * i / sample_count)
            
            try:
                rgb = self.background_image.get(x, y)
                rgb_samples.append(rgb)
            except:
                rgb_samples.append((0, 0, 0))  # Default if pixel access fails
        
        return rgb_samples
    
    # SCALE BAR TOOL METHODS
    def scale_click(self, event):
        if self.scale_bar_placed:
            return  # Only one scale bar allowed
            
        # Validate length before placing
        if not self.validate_scale_length():
            return
            
        try:
            length_um = float(self.scale_length.get())
            magnification = self.scale_magnification.get()
            
            # Convert micrometers to pixels based on magnification
            magnif_factors = {"5X": 4.0, "10X": 2.0, "20X": 1.0, "50X": 1/2.56}
            
            if magnification in magnif_factors:
                # Calculate pixel length for the scale bar
                pixel_length = length_um / (self.pixels_to_dist * magnif_factors[magnification])
                
                # Draw scale bar (horizontal white line with black outline)
                x, y = event.x, event.y
                
                # Black outline
                self.canvas.create_line(x-1, y-1, x + pixel_length+1, y-1, 
                                      fill="black", width=7, tags="scale_bar")
                self.canvas.create_line(x-1, y+1, x + pixel_length+1, y+1, 
                                      fill="black", width=7, tags="scale_bar")
                
                # White scale bar
                self.canvas.create_line(x, y, x + pixel_length, y, 
                                      fill="white", width=7, tags="scale_bar")
                                      fill="white", width=7, tags="scale_bar")
                
                # Add text label with black outline
                label_text = f"{length_um}μm"
                
                # Black outline for text
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            self.canvas.create_text(x + pixel_length/2 + dx, y - 15 + dy, 
                                                  text=label_text, fill="black", 
                                                  font=('Arial', 15, 'bold'), tags="scale_bar")
                                                  font=('Arial', 15, 'bold'), tags="scale_bar")
                
                # White text
                self.canvas.create_text(x + pixel_length/2, y - 15, 
                                      text=label_text, fill="white", 
                                      font=('Arial', 15, 'bold'), tags="scale_bar")
                                      font=('Arial', 15, 'bold'), tags="scale_bar")
                
                # Mark scale bar as placed
                self.scale_bar_placed = True
                self.scale_status.config(text="Scale bar placed", fg='blue')
                self.tool_indicator.config(text="Current Tool: Scale Bar - Scale bar placed (Clear to place new one)", bg='orange')
                
        except ValueError:
            self.scale_status.config(text="Invalid length", fg='red')

app = FlakeImager(root)
root.wm_geometry(f"{int(1200*scale)}x{int(800*scale + 145)}")
root.wm_geometry(f"{int(1200*scale)}x{int(800*scale + 145)}")
root.title('Enhanced Flake Imager')
root.mainloop()
