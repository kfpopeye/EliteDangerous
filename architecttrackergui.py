import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from typing import Optional
import traceback

from config import config

import globals
from globals import logger
import helpers
from tooltip import Tooltip

# --- GUI Definition ---
class ArchitectTrackerGUI(tk.Toplevel):
    edBlue = "#1fbeff"
    edOrange = "#ff8500"
    bgBlack = "#1a1a1a"
    column_visibility = {}
    canvas_tooltip = None

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Architect Tracker")
        self.geometry("800x600")
        self.configure(bg=self.bgBlack)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.column_visibility, self.hide_provided, self.theme, self.column_names, self.trans_bg, self.win_top, self.opac_amount = helpers.load_gui_settings()

        self.setAlpha(self.opac_amount)
        self.setStayOnTop(self.win_top)
        self.setTransparentBg(self.trans_bg)
        self.setStyle()
        helpers.load_facility_requirements()
        if not globals.SITE_LOCATION:
            self._build_info_widgets()
        else:
            self._build_widgets()
            self.refresh()

    def setStayOnTop(self, val):
        self.win_top = val
        if platform.system() == "Darwin":
            self.wm_attributes("-topmost", self.win_top)
        elif platform.system() == "Windows":
            self.wm_attributes("-topmost", self.win_top)
        else:
            self.attributes('-topmost', self.win_top)

    def setAlpha(self, percentage):
        self.opac_amount = percentage
        if platform.system() == "Darwin":
            self.attributes("-alpha", self.opac_amount / 100)
        elif platform.system() == "Windows":
            self.attributes("-alpha", self.opac_amount / 100)
        else:
            self.wm_attributes("-alpha", self.opac_amount / 100)

    def setTransparentBg(self, val):
        """Linux does not support this unless working under a native Win32 platform (ie. wine)"""
        try:
            self.trans_bg = val
            if self.theme == "Dark Mode":
                if self.trans_bg:
                    if platform.system() == "Darwin":
                        self.wm_attributes("-transparent", self.trans_bg)
                        self.config(bg='systemTransparent')
                    elif platform.system() == "Windows":
                        self.attributes('-transparentcolor', ArchitectTrackerGUI.bgBlack)
                    else:
                        ws = self.tk.call("tk", "windowingsystem")
                        if ws == "win32":
                            self.wm_attributes("-transparent", self.trans_bg)
                else:
                    if platform.system() == "Darwin":
                        self.wm_attributes("-transparent", self.trans_bg)
                        self.config(bg='white')
                    elif platform.system() == "Windows":
                        self.attributes('-transparentcolor', "red")
                    else:
                        ws = self.tk.call("tk", "windowingsystem")
                        if ws == "win32":
                            self.wm_attributes("-transparent", "red")
            elif self.theme == "Light Mode":
                if self.trans_bg:
                    if platform.system() == "Darwin":
                        self.wm_attributes("-transparent", self.trans_bg)
                        self.config(bg='systemTransparent')
                    elif platform.system() == "Windows":
                        self.attributes('-transparentcolor', '#d9d9d9')
                    else:
                        ws = self.tk.call("tk", "windowingsystem")
                        if ws == "win32":
                            self.wm_attributes("-transparent", '#d9d9d9')
                else:
                    if platform.system() == "Darwin":
                        self.wm_attributes("-transparent", self.trans_bg)
                        self.config(bg='white')
                    elif platform.system() == "Windows":
                        self.attributes('-transparentcolor', "red")
                    else:
                        ws = self.tk.call("tk", "windowingsystem")
                        if ws == "win32":
                            self.wm_attributes("-transparent", "red")
        except tk.TclError as e:
            logger.warning("Transparency not supported under this Linux version: %s", e)
    
    def auto_size_tree(self):
        """Adjust column widths to fit content."""
        style_font = self.style.lookup("ArchTrack.Treeview", "font")
        font = tkFont.Font(font=style_font)

        for col in self.tree["columns"]:
            max_width = 0
            if col != "#0":  # Exclude the tree column
                for item in self.tree.get_children():
                    text = self.tree.set(item, col)
                    width = font.measure(text) + 10
                    max_width = max(max_width, width)
                text = self.tree.heading(col, "text")
                width = font.measure(text) + 10
                max_width = max(max_width, width)
                # Add some padding
                self.tree.column(col, width=max_width)

        self.update_idletasks()

        """Adjust height to fit content."""
        num_items = 0
        if self.tree.get_children():
            num_items = len(self.tree.get_children())
        self.tree.configure(height=num_items)
        self.update_idletasks()

    def setStyle(self):
        logger.info("setStyle theme is: %s", self.theme)

        self.style = ttk.Style()
        if self.theme == "Dark Mode":
            self.style.theme_use("clam")
            self.style.configure("ArchTrack.Treeview.Heading",
                                    background=ArchitectTrackerGUI.bgBlack,
                                    foreground=ArchitectTrackerGUI.edOrange)
            self.style.configure("ArchTrack.TButton",
                                    background=ArchitectTrackerGUI.bgBlack,
                                    foreground=ArchitectTrackerGUI.edOrange,
                                    padding=(6, 2))
            self.style.configure("ArchTrack.Vertical.TScrollbar",
                                    gripcount=0,
                                    background=ArchitectTrackerGUI.bgBlack,  # Dark background for the scrollbar
                                    troughcolor=ArchitectTrackerGUI.bgBlack,  # Match trough to background
                                    lightcolor=ArchitectTrackerGUI.edOrange,
                                    darkcolor=ArchitectTrackerGUI.edOrange,
                                    sliderlength=20,  # Length of the slider
                                    sliderrelief="flat",
                                    thickness=12,  # Scrollbar thickness
                                    arrowcolor=ArchitectTrackerGUI.edOrange)  # Color for the arrows
            self.style.configure("ArchTrack.Treeview",
                                    background=ArchitectTrackerGUI.bgBlack,
                                    foreground=ArchitectTrackerGUI.edOrange,
                                    rowheight=24,
                                    selectbackground=ArchitectTrackerGUI.bgBlack)
            self.style.configure("ArchTrack.TCombobox",
                                    background=ArchitectTrackerGUI.bgBlack,
                                    foreground=ArchitectTrackerGUI.edOrange,
                                    selectbackground=ArchitectTrackerGUI.bgBlack,
                                    arrowcolor=ArchitectTrackerGUI.edOrange)            
            self.style.configure("ArchTrack.TFrame",
                                    background=ArchitectTrackerGUI.bgBlack)
            self.style.configure("ArchTrack.TLabel",
                                    background=ArchitectTrackerGUI.bgBlack,
                                    foreground=ArchitectTrackerGUI.edOrange)
            self.style.map("ArchTrack.TButton",
               foreground=[("disabled", ArchitectTrackerGUI.bgBlack)],  # Color for disabled text
               background=[("disabled", "#7d7d7d")])  # Color for disabled background
            self.style.map("ArchTrack.Treeview", foreground=[("selected", ArchitectTrackerGUI.edBlue)])
            self.style.map("ArchTrack.TCombobox",
                                fieldbackground=[('readonly', ArchitectTrackerGUI.bgBlack)], # Background color of the entry field
                                background=[('readonly', ArchitectTrackerGUI.bgBlack)]) # Background color of the dropdown list
        elif self.theme == "Light Mode":
            self.style.theme_use("default")  # Use default theme
            self.style.configure("Treeview", rowheight=24)

    def _build_info_widgets(self):
        frame = ttk.Frame(self, padding=10, style="ArchTrack.TFrame")
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Construction site data not found!",
                  background=self.bgBlack,
                  foreground=self.edOrange).grid(row=0, column=0, sticky="nsew", padx=10)
        ttk.Label(frame,
                  text="Visit a construction site and the required commodities will automatically be displayed.",
                  background=self.bgBlack,
                  foreground=self.edOrange).grid(row=1, column=0, sticky="nsew", padx=10)
        self.update_idletasks()
        self.geometry(f"{self.winfo_reqwidth()}x{self.winfo_reqheight()}")

    def _build_widgets(self):
        frame = ttk.Frame(self, padding=8, style="ArchTrack.TFrame")
        frame.pack(fill=tk.BOTH, expand=True)

        # Top controls (row 0)
        dropframe = ttk.Frame(frame, padding=8, style="ArchTrack.TFrame")
        dropframe.grid(row=0, column=0, sticky="nsew", padx=(0, 2))

        self.deleteStation = ttk.Button(dropframe, text="X", style="ArchTrack.TButton", width=1, command=self.on_delete_station)
        self.deleteStation.grid(row=0, column=0, sticky="w")
        Tooltip(self.deleteStation, "Delete the site currently shown.")

        self.station_var = tk.StringVar()
        self.station_var.trace_add("write", self._on_change_station_var)
        self.dropdown = ttk.Combobox(dropframe, textvariable=self.station_var, state="readonly", style="ArchTrack.TCombobox")
        self.dropdown.grid(row=0, column=1, sticky="w", padx=(0, 2))
        self.dropdown.bind("<<ComboboxSelected>>", lambda e: (self.refresh(), self.dropdown.after(1, self._clear_combo_selection)))

        self.changeToPrevStation = ttk.Button(dropframe, text="<", style="ArchTrack.TButton", width=1, command=self.on_prev_station)
        self.changeToPrevStation.grid(row=0, column=2, sticky="w")
        Tooltip(self.changeToPrevStation, "Change to the previous site.")

        self.changeStation = ttk.Button(dropframe, text=">", style="ArchTrack.TButton", width=1, command=self.on_next_station)
        self.changeStation.grid(row=0, column=3, sticky="w")
        Tooltip(self.changeStation, "Change to the next site.")

        marketframe = ttk.Frame(frame, padding=0, style="ArchTrack.TFrame")
        marketframe.grid(row=0, column=3, sticky="nsew", padx=(0, 2), pady=(0))

        self.togglePrefStation = ttk.Button(marketframe, text="$\\Ly\\Alt", style="ArchTrack.TButton", width=8, command=self.on_toggle_prefMarket)
        self.togglePrefStation.grid(row=0, column=0, sticky="w")
        Tooltip(self.togglePrefStation, "Switch between closest, cheapest\nand alternate markets.")

        self.toggleTypeStation = ttk.Button(marketframe, text="O\\S", style="ArchTrack.TButton", width=3, command=self.on_toggle_prefType)
        self.toggleTypeStation.grid(row=0, column=1, sticky="w")
        Tooltip(self.toggleTypeStation, "Prefer orbital or surface markets.")
        
        labelframe = ttk.Frame(marketframe)
        labelframe.grid(row=0, column=2, sticky="w")

        ttk.Label(labelframe, text="Preferred Market:", style="ArchTrack.TLabel", padding=0).pack(anchor="w", fill='x')
        self.market_name_label = ttk.Label(labelframe, text="", style="ArchTrack.TLabel", padding=0)
        self.market_name_label['text'] = "Holding text"
        self.market_name_label.pack(anchor="w", fill='x')

        carrierframe = ttk.Frame(frame, padding=8, style="ArchTrack.TFrame")
        carrierframe.grid(row=0, column=5, sticky="nsew", padx=(0, 2))

        self.canvas = tk.Canvas(carrierframe, width=25, height=25)
        self.canvas.grid(row=0, column=0, sticky="w")
        self.draw_canvas()

        ttk.Label(carrierframe, text="Carrier:", style="ArchTrack.TLabel").grid(row=0, column=1, sticky="e", padx=(0, 5))
        self.carrier_label = ttk.Label(carrierframe, text="", style="ArchTrack.TLabel")
        self.carrier_label.grid(row=0, column=2, sticky="w")

        # Treeview setup (row 1)
        cols = list(globals.DEFAULT_COLUMNS.keys())
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", style="ArchTrack.Treeview")
        for idx, c in enumerate(cols):
            self.tree.heading(c, text=self.column_names[idx])
            self.tree.column(c, anchor='w' if c == "Material" else 'center')

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview, style="ArchTrack.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=1, column=0, columnspan=7, sticky="nsew")
        scrollbar.grid(row=1, column=7, sticky="ns")

        # Make row 1 expandable
        frame.rowconfigure(1, weight=1)
        for i in range(8):
            frame.columnconfigure(i, weight=1 if i < 7 else 0)

        self.refresh_columns()  # Ensure columns initial visibility

    def draw_canvas(self):
        if self.theme == "Dark Mode":
            bg = self.style.lookup("ArchTrack.TButton", "background")
            fg = self.style.lookup("ArchTrack.TButton", "foreground")
            active_bg = self.style.lookup("ArchTrack.TButton", "background", state=("active",))
        else:
            bg = self.style.lookup("TButton", "background")
            fg = self.style.lookup("TButton", "foreground")
            active_bg = self.style.lookup("TButton", "background", state=("active",))

        # Clear canvas first
        self.canvas.delete("all")

        # Draw main rectangle
        self.rect_id = self.canvas.create_rectangle(
            0, 0, 25, 25,
            fill=bg,
            outline="black",
            tags="canvas_button"
        )

        # Draw play/pause symbol
        if globals.FCAPI_PAUSED:
            self.canvas.create_rectangle(7, 5, 12, 20, fill=fg, outline="black", tags="canvas_button")
            self.canvas.create_rectangle(15, 5, 20, 20, fill=fg, outline="black", tags="canvas_button")
            tooltip_text = "Press to UNpause\ncarrier updates."
        else:
            self.canvas.create_polygon(7, 5, 7, 20, 20, 13, fill=fg, outline="black", tags="canvas_button")
            tooltip_text = "Press to pause\ncarrier updates."

        # Attach tooltip to the canvas itself (not individual items)
        if hasattr(self, "canvas_tooltip") and self.canvas_tooltip:
            self.canvas_tooltip._hide()
        self.canvas_tooltip = Tooltip(self.canvas, tooltip_text, follow_mouse=True)

        # Bind hover for rectangle color
        self.canvas.tag_bind("canvas_button", "<Enter>", lambda e: self.canvas.itemconfig(self.rect_id, fill=active_bg))
        self.canvas.tag_bind("canvas_button", "<Leave>", lambda e: self.canvas.itemconfig(self.rect_id, fill=bg))

        # Bind click for canvas (anywhere)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def _on_change_station_var(self, *args):
        if self.station_var.get() == '-All-':
            self.deleteStation.config(state="disabled")
        else:
            self.deleteStation.config(state="enabled")

    def _on_canvas_hover(self, event, color):
        self.canvas.itemconfig("canvas_button", fill=color)
        
    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def refresh(self):
        # Remember the currently selected station name
        current_selection = self.station_var.get()

        # Load new data
        data = helpers.load_facility_requirements()
        if data == {}:
            self.clear_frame()
            self._build_info_widgets()
            globals.SITE_LOCATION = None
            return
        self.data = data

        # Prepare data for display
        display = [
            (
              (full.split(':', 1)[-1].strip() if ':' in full else
               full.split(';', 1)[-1].strip() if ';' in full else full),
              full
            )
            for full in data
        ]
        self.station_map = {name: full for name, full in display}
        self.station_map['-All-'] = None

        # Update dropdown
        values = [name for name, _ in display]
        if len(values) > 1:
            values.insert(0, '-All-')
        self.dropdown['values'] = values

        # Restore selection or default to first station
        if values:
            if current_selection in values:
                self.station_var.set(current_selection)
            else:
                self.station_var.set(values[0])

            # Refresh data for selected station
            self.display_station()
        else:
            # No data - clear tree
            self.tree.delete(*self.tree.get_children())

        #set preferred market label text
        mode = helpers.getPreferedMarket()
        if mode == globals.MARKET_MODE.Cheapest:
            t = 'cheapest ($)'
        elif mode == globals.MARKET_MODE.Closest:
            t = 'closest (Ly)'
        else:
            t = 'alternate (Alt)'
            
        t = t + " " + helpers.getPreferedType().name
        self.market_name_label['text'] = t
        
        # Set the carrier label
        self.carrier_label['text'] = globals.CARRIER_TRACKER.carrier_name or 'N/A'

        self.draw_canvas() #resets pause button

        self.update_idletasks()
        self.auto_size_tree()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        '''
        #is this needed for VR?
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        if height > screen_height:
            height = screen_height
        '''
        self.geometry(f"{width}x{height}")

    def display_station(self):
        self.tree.delete(*self.tree.get_children())
        sel = self.station_var.get()

        if sel == '-All-':
            materials = {}
            for site in self.data.values():
                for material_key, info in site['materials'].items():
                    if material_key not in materials:
                        materials[material_key] = {
                            'Name_Localised': info['Name_Localised'],
                            'RequiredAmount': 0,
                            'ProvidedAmount': 0
                        }
                    materials[material_key]['RequiredAmount'] += info['RequiredAmount']
                    materials[material_key]['ProvidedAmount'] += info['ProvidedAmount']
        else:
            full = self.station_map.get(sel)
            if not full:
                return
            materials = self.data[full]['materials']

        cargo_items = helpers.load_starship_cargo_data()
        # Create lookup for cargo items
        cargo_lookup = {i.get('Name'): i for i in cargo_items}

        # Set the alternating row and highlight colours
        if self.theme == "Dark Mode":
            if self.trans_bg:
                self.tree.tag_configure('evenrow', background=self.bgBlack)
            else:
                self.tree.tag_configure('evenrow', background='#2a2a2a')
            self.tree.tag_configure('oddrow', background=self.bgBlack)
            self.tree.tag_configure('highlightedrow', foreground=self.edBlue)
        else:
            if self.trans_bg:
                self.tree.tag_configure('oddrow', background='#d9d9d9')
            else:
                self.tree.tag_configure('oddrow', background='#ffffff')
            self.tree.tag_configure('evenrow', background='#d9d9d9')
            self.tree.tag_configure('highlightedrow', foreground='#ff6347')

        self.tree.tag_configure('totalsrow', font=('TkDefaultFont', 10, 'bold'))

        req_total = 0
        prov_total = 0
        need_total = 0
        fc_total = 0
        ship_total = 0
        short_total = 0
        rows_index = 0

        # Insert the materials into the tree
        for idx, (mat, vals) in enumerate(sorted(materials.items())):
            req = vals['RequiredAmount']
            prov = vals['ProvidedAmount']
            if self.hide_provided and prov >= req:
                continue
            safeMat = mat.replace("$", "").replace("_name;", "")
            locName = vals['Name_Localised']
            need = req - prov

            pref_market = helpers.get_prefMarket_name(mat)

            # Get fleet carrier and ship cargo quantities
            #TODO: change these to use $_name; (can't till EDMC updates cargo and fc)
            fc_qty = globals.CARRIER_TRACKER.get_quantity(safeMat)
            ship_qty = cargo_lookup.get(safeMat, {}).get('Count', 0)

            # Calculate shortage
            short = max(0, need - (fc_qty + ship_qty))

            # Determine row color based on even or odd index
            row_tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            tags = [row_tag]

            if globals.SHIP_STATE == globals.SHIP_MODE.DockedAtMarket:
                for_sale = helpers.is_mat_in_stock(mat)
                if for_sale and short > 0:
                    tags.append('highlightedrow')
            elif globals.SHIP_STATE == globals.SHIP_MODE.DockedAtFC:
                if need > 0 and fc_qty > 0 and need > ship_qty:
                    tags.append('highlightedrow')
            elif globals.SHIP_STATE == globals.SHIP_MODE.DockedAtSite:
                if need > 0 and ship_qty > 0:
                    tags.append('highlightedrow')

            # Insert row into the tree view
            self.tree.insert("", "end", values=(locName, req, prov, need, pref_market,
                                               fc_qty, ship_qty, short), tags=tuple(tags))

            rows_index += 1
            req_total = req_total + req
            prov_total = prov_total + prov
            need_total = need_total + need
            fc_total = fc_total + fc_qty
            ship_total = ship_total + ship_qty
            short_total = short_total + short
            
        market_note = "* denotes orbital"
        if helpers.getPreferedType() == globals.STATION_TYPE.Orbital:
            market_note = "* denotes surface"

        total_row_tag = 'evenrow' if rows_index % 2 == 0 else 'oddrow'
        tags = (total_row_tag, 'totalsrow')
        self.tree.insert("", "end", values=("Totals", req_total, prov_total, need_total, market_note,
                                               fc_total, ship_total, short_total), tags=tuple(tags))

    def on_close(self):
        globals.AT_BUTTON.set("Show Architect Tracker (tracking disabled)")
        self.destroy()  # Close the window

    def on_canvas_click(self, event):
        globals.FCAPI_PAUSED = not globals.FCAPI_PAUSED
        if globals.FCAPI_PAUSED:
            logger.info(f'Fleet carrier API paused.')
        else:
            logger.info(f'Fleet carrier API UNpaused.')
        self.draw_canvas()

    def on_next_station(self):
        values = self.dropdown['values']
        if not values:
            logger.info("No stations to switch to.")
            return

        next_ndx = self.dropdown.current() + 1
        if next_ndx >= len(values):
            next_ndx = 0

        self.dropdown.current(next_ndx)
        self.dropdown.selection_clear()
        logger.info("Changing to station: %s", self.dropdown.get())
        self.refresh()

    def on_prev_station(self):
        values = self.dropdown['values']
        if not values:
            logger.info("No stations to switch to.")
            return

        prev_ndx = self.dropdown.current() - 1
        if prev_ndx <= -1:
            prev_ndx = len(values) - 1

        self.dropdown.current(prev_ndx)
        self.dropdown.selection_clear()
        logger.info("Changing to station: %s", self.dropdown.get())
        self.refresh()

    def change_station(self, station):
        short_name = (station.split(':', 1)[-1].strip() if ':' in station else
                        station.split(';', 1)[-1].strip() if ';' in station
                        else station)

        values = self.dropdown['values']
        if not values:
            logger.info("No stations to switch to.")
            return

        if short_name in values:
            self.station_var.set(short_name)
            return
        else:
            self.refresh()

        values = self.dropdown['values']
        if short_name in values:
            self.station_var.set(short_name)
            return
        else:
            logger.info("Could not change to station: %s", short_name)

    def on_delete_station(self):
        sel = self.station_var.get()
        station_name = self.station_map.get(sel)
        if self.data.pop(station_name, None):
            logger.info("Deleted station: %s", station_name)
        else:
            logger.info("Could not delete station: %s", station_name)

        try:
            import json
            with open(globals.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error("Error saving data: %s", e)

        self.refresh()

    def reset_Style(self, new_theme):
        self.theme = new_theme
        logger.info("reset_Style theme is: %s", self.theme)
        self.setStyle()
        self.refresh()

    def toggle_column(self, column, is_visible: bool):
        self.column_visibility[column] = is_visible
        self.refresh_columns()

    def toggle_hide_provided(self, val):
        self.hide_provided = val
        self.refresh()

    def refresh_columns(self):
        visible_columns = [col for col, vis in self.column_visibility.items() if vis]
        self.tree["displaycolumns"] = visible_columns
        """for col in visible_columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)"""

    def on_toggle_prefMarket(self):
        old = helpers.getPreferedMarket()

        if old == globals.MARKET_MODE.Cheapest:
            config.set('ArchTrack_prefMarket', globals.MARKET_MODE.Closest.value)
        elif old == globals.MARKET_MODE.Closest:
            config.set('ArchTrack_prefMarket', globals.MARKET_MODE.Alternate.value)
        else:
            config.set('ArchTrack_prefMarket', globals.MARKET_MODE.Cheapest.value)
        self.refresh()
        
    def on_toggle_prefType(self):
        old = helpers.getPreferedType()
        if old == globals.STATION_TYPE.Orbital:            
            config.set('ArchTrack_prefType', globals.STATION_TYPE.Surface.value)
        else:
            config.set('ArchTrack_prefType', globals.STATION_TYPE.Orbital.value)
        self.refresh()

    def rename_column(self, c, v):
        self.tree.heading(c, text=v)
        cols = self.tree["columns"]
        col_index = cols.index(c)
        self.column_names[col_index] = v
