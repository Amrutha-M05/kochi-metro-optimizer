import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Dict, List
import sys
import os

# Import your existing classes (make sure dijkstra.py is in the same directory)
try:
    from dijkstra import KochiMetroNetwork, MetroRouteOptimizer
except ImportError:
    print("Error: Could not import from dijkstra.py")
    print("Make sure dijkstra.py is in the same directory as this GUI file")
    sys.exit(1)

class KochiMetroGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kochi Metro Route Optimizer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f2f5')
        
        # Initialize the metro network and optimizer
        self.network = KochiMetroNetwork()
        self.optimizer = MetroRouteOptimizer(self.network)
        
        # Variables
        self.start_station_var = tk.StringVar()
        self.cost_weight_var = tk.DoubleVar(value=0.3)
        self.time_weight_var = tk.DoubleVar(value=0.4)
        self.stops_weight_var = tk.DoubleVar(value=0.3)
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.setup_weight_validation()
        
    def setup_styles(self):
        """Setup custom styles for the GUI"""
        style = ttk.Style()
        
        # Configure styles for modern look
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'),
                       foreground='#2c3e50',
                       background='#f0f2f5')
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 10),
                       foreground='#7f8c8d',
                       background='#f0f2f5')
        
        style.configure('Section.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground='#34495e',
                       background='#ffffff')
        
        style.configure('Custom.TFrame',
                       background='#ffffff',
                       relief='solid',
                       borderwidth=1)
        
        style.configure('Calculate.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       foreground='white')
        
        # Map the button colors (this might not work on all systems)
        style.map('Calculate.TButton',
                 background=[('active', '#2980b9'), ('!active', '#3498db')])
        
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Content area with two columns
        content_frame = tk.Frame(main_frame, bg='#f0f2f5')
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Left panel - Input controls
        self.create_input_panel(content_frame)
        
        # Right panel - Results
        self.create_results_panel(content_frame)
        
    def create_header(self, parent):
        """Create the header section"""
        header_frame = tk.Frame(parent, bg='#3498db', height=100)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame,
                              text="Kochi Metro Route Optimizer",
                              font=('Segoe UI', 24, 'bold'),
                              fg='white',
                              bg='#3498db')
        title_label.pack(expand=True)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Find the most efficient routes using Dijkstra's Algorithm",
                                 font=('Segoe UI', 12),
                                 fg='white',
                                 bg='#3498db')
        subtitle_label.pack()
        
    def create_input_panel(self, parent):
        """Create the input controls panel"""
        input_frame = ttk.Frame(parent, style='Custom.TFrame', padding=20)
        input_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Station selection
        station_frame = tk.Frame(input_frame, bg='white')
        station_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(station_frame, text="Starting Station", 
                 style='Section.TLabel').pack(anchor='w')
        
        # Station dropdown with search capability
        self.station_combo = ttk.Combobox(station_frame,
                                         textvariable=self.start_station_var,
                                         values=sorted(list(self.network.stations)),
                                         state='readonly',
                                         width=30,
                                         font=('Segoe UI', 10))
        self.station_combo.pack(fill='x', pady=(5, 0))
        self.station_combo.set("Select starting station...")
        
        # Optimization weights section
        weights_frame = tk.Frame(input_frame, bg='white')
        weights_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(weights_frame, text="Optimization Preferences", 
                 style='Section.TLabel').pack(anchor='w')
        
        ttk.Label(weights_frame, 
                 text="Adjust weights to prioritize cost, time, or fewer stops (must sum to 1.0)",
                 font=('Segoe UI', 9),
                 foreground='#7f8c8d',
                 background='white').pack(anchor='w', pady=(5, 10))
        
        # Weight controls in a grid
        weights_grid = tk.Frame(weights_frame, bg='white')
        weights_grid.pack(fill='x')
        
        # Cost weight
        cost_frame = tk.Frame(weights_grid, bg='white')
        cost_frame.grid(row=0, column=0, padx=(0, 10), sticky='ew')
        
        tk.Label(cost_frame, text="Cost Weight",
                font=('Segoe UI', 9, 'bold'),
                bg='white', fg='#e74c3c').pack()
        
        self.cost_scale = tk.Scale(cost_frame, from_=0, to=1, resolution=0.1,
                                  orient='horizontal', variable=self.cost_weight_var,
                                  bg='white', fg='#e74c3c', font=('Segoe UI', 8))
        self.cost_scale.pack(fill='x')
        
        self.cost_entry = tk.Entry(cost_frame, textvariable=self.cost_weight_var,
                                  width=6, justify='center', font=('Segoe UI', 9))
        self.cost_entry.pack(pady=(5, 0))
        
        # Time weight
        time_frame = tk.Frame(weights_grid, bg='white')
        time_frame.grid(row=0, column=1, padx=(0, 10), sticky='ew')
        
        tk.Label(time_frame, text="Time Weight",
                font=('Segoe UI', 9, 'bold'),
                bg='white', fg='#f39c12').pack()
        
        self.time_scale = tk.Scale(time_frame, from_=0, to=1, resolution=0.1,
                                  orient='horizontal', variable=self.time_weight_var,
                                  bg='white', fg='#f39c12', font=('Segoe UI', 8))
        self.time_scale.pack(fill='x')
        
        self.time_entry = tk.Entry(time_frame, textvariable=self.time_weight_var,
                                  width=6, justify='center', font=('Segoe UI', 9))
        self.time_entry.pack(pady=(5, 0))
        
        # Stops weight
        stops_frame = tk.Frame(weights_grid, bg='white')
        stops_frame.grid(row=0, column=2, sticky='ew')
        
        tk.Label(stops_frame, text="Stops Weight",
                font=('Segoe UI', 9, 'bold'),
                bg='white', fg='#3498db').pack()
        
        self.stops_scale = tk.Scale(stops_frame, from_=0, to=1, resolution=0.1,
                                   orient='horizontal', variable=self.stops_weight_var,
                                   bg='white', fg='#3498db', font=('Segoe UI', 8))
        self.stops_scale.pack(fill='x')
        
        self.stops_entry = tk.Entry(stops_frame, textvariable=self.stops_weight_var,
                                   width=6, justify='center', font=('Segoe UI', 9))
        self.stops_entry.pack(pady=(5, 0))
        
        # Configure grid weights
        weights_grid.columnconfigure(0, weight=1)
        weights_grid.columnconfigure(1, weight=1)
        weights_grid.columnconfigure(2, weight=1)
        
        # Weight sum indicator
        self.weight_sum_label = tk.Label(weights_frame,
                                        text="Sum: 1.0 ✓",
                                        font=('Segoe UI', 9, 'bold'),
                                        bg='#d5f4e6',
                                        fg='#27ae60',
                                        relief='solid',
                                        borderwidth=1)
        self.weight_sum_label.pack(fill='x', pady=(10, 0))
        
        # Calculate button
        self.calculate_btn = tk.Button(input_frame,
                                      text="Calculate Optimal Routes",
                                      font=('Segoe UI', 12, 'bold'),
                                      bg='#3498db',
                                      fg='white',
                                      relief='flat',
                                      padx=20,
                                      pady=10,
                                      cursor='hand2',
                                      command=self.calculate_routes)
        self.calculate_btn.pack(fill='x', pady=(20, 0))
        
        # Quick preset buttons
        preset_frame = tk.Frame(input_frame, bg='white')
        preset_frame.pack(fill='x', pady=(10, 0))
        
        tk.Label(preset_frame, text="Quick Presets:",
                font=('Segoe UI', 9, 'bold'),
                bg='white').pack(anchor='w')
        
        preset_buttons_frame = tk.Frame(preset_frame, bg='white')
        preset_buttons_frame.pack(fill='x', pady=(5, 0))
        
        tk.Button(preset_buttons_frame, text="Cost Focus",
                 font=('Segoe UI', 8), bg='#e74c3c', fg='white',
                 command=lambda: self.set_preset(0.6, 0.2, 0.2)).pack(side='left', padx=(0, 5))
        
        tk.Button(preset_buttons_frame, text="Time Focus",
                 font=('Segoe UI', 8), bg='#f39c12', fg='white',
                 command=lambda: self.set_preset(0.2, 0.6, 0.2)).pack(side='left', padx=(0, 5))
        
        tk.Button(preset_buttons_frame, text="Fewer Stops",
                 font=('Segoe UI', 8), bg='#3498db', fg='white',
                 command=lambda: self.set_preset(0.2, 0.2, 0.6)).pack(side='left')
        
    def create_results_panel(self, parent):
        """Create the results display panel"""
        results_frame = ttk.Frame(parent, style='Custom.TFrame', padding=20)
        results_frame.pack(side='right', fill='both', expand=True)
        
        # Results header
        self.results_header = tk.Label(results_frame,
                                      text="Select a starting station and calculate routes",
                                      font=('Segoe UI', 14, 'bold'),
                                      bg='white',
                                      fg='#7f8c8d')
        self.results_header.pack(pady=(0, 20))
        
        # Results display area
        self.results_text = scrolledtext.ScrolledText(results_frame,
                                                     height=25,
                                                     font=('Consolas', 10),
                                                     wrap='word',
                                                     bg='#f8f9fa',
                                                     fg='#2c3e50',
                                                     relief='flat',
                                                     borderwidth=0,
                                                     padx=10,
                                                     pady=10)
        self.results_text.pack(fill='both', expand=True)
        
        # Configure text tags for styling
        self.results_text.tag_config('header', font=('Segoe UI', 12, 'bold'), 
                                    foreground='#2c3e50')
        self.results_text.tag_config('destination', font=('Segoe UI', 11, 'bold'), 
                                    foreground='#3498db')
        self.results_text.tag_config('cost', foreground='#e74c3c')
        self.results_text.tag_config('time', foreground='#f39c12')
        self.results_text.tag_config('stops', foreground='#3498db')
        self.results_text.tag_config('path', foreground='#7f8c8d', font=('Consolas', 9))
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(results_frame, mode='indeterminate')
        
    def setup_weight_validation(self):
        """Setup validation for weight inputs"""
        # Bind events to update weight sum
        self.cost_weight_var.trace('w', self.update_weight_sum)
        self.time_weight_var.trace('w', self.update_weight_sum)
        self.stops_weight_var.trace('w', self.update_weight_sum)
        
        # Bind scale movements to entry updates
        self.cost_scale.config(command=lambda x: self.update_weight_sum())
        self.time_scale.config(command=lambda x: self.update_weight_sum())
        self.stops_scale.config(command=lambda x: self.update_weight_sum())
        
    def update_weight_sum(self, *args):
        """Update the weight sum indicator"""
        try:
            total = (self.cost_weight_var.get() + 
                    self.time_weight_var.get() + 
                    self.stops_weight_var.get())
            
            if abs(total - 1.0) < 0.001:
                self.weight_sum_label.config(text="Sum: 1.0 ✓",
                                           bg='#d5f4e6',
                                           fg='#27ae60')
            else:
                self.weight_sum_label.config(text=f"Sum: {total:.2f} (must be 1.0)",
                                           bg='#fadbd8',
                                           fg='#e74c3c')
        except tk.TclError:
            pass  # Ignore errors during variable updates
    
    def set_preset(self, cost, time, stops):
        """Set preset weight values"""
        self.cost_weight_var.set(cost)
        self.time_weight_var.set(time)
        self.stops_weight_var.set(stops)
        
    def validate_inputs(self):
        """Validate user inputs before calculation"""
        if not self.start_station_var.get() or self.start_station_var.get() == "Select starting station...":
            messagebox.showerror("Error", "Please select a starting station")
            return False
            
        total_weight = (self.cost_weight_var.get() + 
                       self.time_weight_var.get() + 
                       self.stops_weight_var.get())
        
        if abs(total_weight - 1.0) > 0.001:
            messagebox.showerror("Error", "Weights must sum to 1.0")
            return False
            
        return True
        
    def calculate_routes(self):
        """Calculate and display optimal routes"""
        if not self.validate_inputs():
            return
            
        # Disable calculate button and show progress
        self.calculate_btn.config(state='disabled', text="Calculating...")
        self.progress.pack(fill='x', pady=(10, 0))
        self.progress.start()
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.results_header.config(text="Calculating optimal routes...")
        
        # Run calculation in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._calculate_routes_thread)
        thread.daemon = True
        thread.start()
        
    def _calculate_routes_thread(self):
        """Thread function for route calculation"""
        try:
            start_station = self.start_station_var.get()
            cost_weight = self.cost_weight_var.get()
            time_weight = self.time_weight_var.get()
            stops_weight = self.stops_weight_var.get()
            
            # Calculate routes using your existing optimizer
            routes = self.optimizer.find_optimal_routes(
                start_station, cost_weight, time_weight, stops_weight
            )
            
            # Update GUI in main thread
            self.root.after(0, self._display_results, start_station, routes)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
            
    def _display_results(self, start_station, routes):
        """Display calculation results in the GUI"""
        # Stop progress and re-enable button
        self.progress.stop()
        self.progress.pack_forget()
        self.calculate_btn.config(state='normal', text="Calculate Optimal Routes")
        
        # Update header
        self.results_header.config(text=f"Optimal Routes from {start_station}")
        
        # Clear and populate results
        self.results_text.delete(1.0, tk.END)
        
        if not routes:
            self.results_text.insert(tk.END, "No routes found from the selected station.\n")
            return
            
        # Sort routes by composite score
        sorted_routes = sorted(routes.items(), key=lambda x: x[1]['composite_score'])
        
        # Add header
        header = f"{'DESTINATION':<20} {'COST':<8} {'TIME':<8} {'STOPS':<6} ROUTE\n"
        self.results_text.insert(tk.END, header, 'header')
        self.results_text.insert(tk.END, "=" * 80 + "\n\n")
        
        # Add each route
        for destination, route_info in sorted_routes:
            # Destination
            self.results_text.insert(tk.END, f"{destination:<20} ", 'destination')
            
            # Metrics
            self.results_text.insert(tk.END, f"₹{route_info['total_cost']:<7.0f} ", 'cost')
            self.results_text.insert(tk.END, f"{route_info['total_time']:<7.1f}m ", 'time')
            self.results_text.insert(tk.END, f"{route_info['total_stops']:<6d} ", 'stops')
            
            # Path
            path_str = " → ".join(route_info['path'])
            self.results_text.insert(tk.END, f"{path_str}\n", 'path')
            
            # Add some spacing
            if len(sorted_routes) > 10 and sorted_routes.index((destination, route_info)) < len(sorted_routes) - 1:
                if sorted_routes.index((destination, route_info)) % 5 == 4:
                    self.results_text.insert(tk.END, "\n")
        
        # Scroll to top
        self.results_text.see(1.0)
        
    def _show_error(self, error_message):
        """Show error message"""
        self.progress.stop()
        self.progress.pack_forget()
        self.calculate_btn.config(state='normal', text="Calculate Optimal Routes")
        messagebox.showerror("Error", f"An error occurred: {error_message}")

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = KochiMetroGUI(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Set minimum size
    root.minsize(1000, 700)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        messagebox.showerror("Critical Error", f"A critical error occurred: {e}")
        
if __name__ == "__main__":
    main()