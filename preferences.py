import os
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import webbrowser

import myNotebook as nb
from config import appname, appversion, config

import globals
from globals import logger
import helpers

# --- Settings Hooks ---
def pluginprefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> nb.Frame | None:
    column_display_vars = {}

    column_visibility, hide_provided, theme, column_display, trans_bg, win_top, opac_amount = helpers.load_gui_settings() #globals.SHOW_UI_AT_START is set in plugin_start3()

    if config.get('ArchTrack_fcapimode') is None:
        fcapi_mode = "First then pause"
        logger.info(f"fcapi_mode not found using default settings.")
    else:
        fcapi_mode = config.get_str('ArchTrack_fcapimode')

    column_description = {}
    column_description["Material"] = "The commodities the construction site requires."
    column_description["Required"] = "The total amount required by the construction site."
    column_description["Provided"] = "The total amount delivered to the construction site."
    column_description["Needed"] = "Required minus Provided"
    column_description["Pref Market"] = "The closest or cheapest market that has the commodity."
    column_description["Carrier Qty"] = "The total amount you fleet carrier has."
    column_description["Ship Qty"] = "The total amount your starship has."
    column_description["Shortfall"] = "Needed minus Carrier Qty minus Ship Qty (or 0 if negative)"

    # PREFS FRAME ************************************************
    pref_frame = nb.Frame(parent)
    title_frame = nb.Frame(pref_frame, border=0)
    title_frame.grid(row=0, column=1, columnspan=2)
    nb.Label(title_frame, text="Architect Tracker (" + globals.ARCHITECT_TRACKER_VER + ") plugin by CMDR kfpopeye.").grid(row=0, column=1, sticky="nsew")
    nb.Button(title_frame, text="Open website", command=open_url).grid(row=0, column=2, sticky="w")

    upper_row = nb.Frame(pref_frame, border=0)
    upper_row.grid(row=1, column=1, columnspan=2)

    # COLUMNS FRAME ************************************************
    col_frame = nb.Frame(upper_row, border=2, relief="groove")
    col_frame.grid(row=1, column=0)

    #configure column headers
    g_row = 0
    nb.Label(col_frame, text="Change columns to display or rename:").grid(row=g_row, column=0, columnspan=2, sticky="nsew")
    g_row = g_row +1
    for idx, (col, visible) in enumerate(column_visibility.items()):
        var = tk.BooleanVar(value=visible)
        if idx == 0:
            chk = nb.Checkbutton(
                col_frame,
                text=col,
                variable=var,
                state="disabled"
            )
            var.set(True)
        else:
            chk = nb.Checkbutton(
                col_frame,
                text=col,
                variable=var,
                command=lambda c=col, v=var: toggle_column(c, v.get())
            )
        chk.grid(row=g_row, column=0, sticky="nsew")

        display_var = tk.StringVar(value=column_display[idx])
        column_display_vars[col] = display_var
        c_name = tk.Entry(col_frame, textvariable=display_var)
        c_name.bind("<KeyRelease>", lambda e, c=col, v=display_var: on_column_rename(c, v.get()))
        c_name.grid(row=g_row, column=1, sticky="nsew")

        nb.Label(col_frame, text=column_description[col]).grid(row=g_row, column=2, sticky="w", padx=5)
        g_row = g_row + 1

    # CAPI FRAME ************************************************
    capi_frame = nb.Frame(upper_row, border=2, relief="groove")
    capi_frame.grid(row=1, column=1, sticky="nsew")
    g_row = 0

    #select FCAPI mode
    nb.Label(capi_frame, text="Select fleet capi mode:").grid(row=g_row, sticky="nw")
    g_row = g_row +1
    fcapi_var = tk.StringVar(value=fcapi_mode)
    capi_opt = ttk.Combobox(capi_frame, textvariable=fcapi_var, state="readonly")
    capi_opt['values'] = ("First then pause", "Only when unpaused")
    capi_opt.grid(row=g_row, sticky="nw", padx=5, pady=5)
    g_row = g_row +1
    capi_opt.bind("<<ComboboxSelected>>", lambda event: change_fcapi_mode(fcapi_var.get()))

    #display fcapi notes
    text2_widget = tk.Text(capi_frame, height=8, width=40, wrap='word', font=('Verdana', 9), border=0)
    text2_widget.tag_configure('big', font=('Verdana', 9, 'bold'))
    text2_widget.tag_configure('underline', font=('Verdana', 9, 'underline'))

    text2_widget.insert(tk.END, "Fleet Carrier API Options\n\n", 'underline')
    text2_widget.insert(tk.END, "First then pause\n", 'big')
    text2_widget.insert(tk.END, "Accepts the first update then automatically pauses.\n")
    text2_widget.insert(tk.END, "Only when UNpaused\n", 'big')
    text2_widget.insert(tk.END, "Only accepts updates when NOT paused.\n")

    text2_widget.config(state='disabled')
    text2_widget.grid(row=g_row, sticky="nsew", padx=5, pady=5)

    # BUTTONS FRAME ************************************************
    but_frame = nb.Frame(pref_frame, border=2, relief="groove")
    but_frame.grid(row=2, column=1, sticky="nw")
    g_row = 0

    #remove fully provided materials
    hide_var = tk.BooleanVar(value=hide_provided)
    chk_hide = nb.Checkbutton(
        but_frame,
        text="Remove delivered from lists",
        variable=hide_var,
        command=lambda val=hide_var: toggle_hide_provided(val.get())
    ).grid(row=g_row, sticky="nw", padx=5, pady=5)
    g_row = g_row +1

    #select UI colours
    nb.Label(but_frame, text="Select colours to use:").grid(row=g_row, sticky="nw")
    g_row = g_row +1
    theme_var = tk.StringVar(value=theme)
    color_opt = ttk.Combobox(but_frame, textvariable=theme_var, state="readonly")
    color_opt['values'] = ("Light Mode", "Dark Mode")
    color_opt.grid(row=g_row, sticky="nw", padx=5, pady=5)
    g_row = g_row +1
    color_opt.bind("<<ComboboxSelected>>", lambda event: reset_Style(theme_var.get()))

    # Transparency, On top and Opacity Settings
    if platform.system() in ("Darwin", "Windows"):
        trans_var = tk.BooleanVar(value=trans_bg)
        nb.Checkbutton(
            but_frame,
            text="Use Transparent Background\n(Not supported in Linux)",
            variable=trans_var,
            command=lambda val=trans_var: toggle_trans_bg(val.get())
        ).grid(row=g_row, sticky="nw", padx=5, pady=5)
    else:
        ws = parent.tk.call("tk", "windowingsystem")
        if ws == "win32":
            trans_var = tk.BooleanVar(value=trans_bg)
            nb.Checkbutton(
                but_frame,
                text="Use Transparent Background\n(Not supported in Linux)",
                variable=trans_var,
                command=lambda val=trans_var: toggle_trans_bg(val.get())
            ).grid(row=g_row, sticky="nw", padx=5, pady=5)
        else:
            trans_var = tk.BooleanVar(value=False)
            nb.Checkbutton(
                but_frame,
                text="Use Transparent Background\n(Not supported in Linux)",
                variable=trans_var,
                state="disabled"
            ).grid(row=g_row, sticky="nw", padx=5, pady=5)
    g_row = g_row +1
    wintop_var = tk.BooleanVar(value=win_top)
    nb.Checkbutton(
        but_frame,
        text="Keep window on top",
        variable=wintop_var,
        command=lambda val=wintop_var: toggle_win_top(val.get())
    ).grid(row=g_row, sticky="nw", padx=5, pady=5)
    g_row = g_row +1
    s = "Window Opacity - " + str(opac_amount) + "%"
    sldr_label = nb.Label(but_frame, text=s)
    sldr_label.grid(row=g_row, sticky="nw")
    g_row = g_row +1
    onum_var = tk.IntVar(value=opac_amount)
    ttk.Scale(
        but_frame,
        from_=10, to=100, variable=onum_var,
        command=lambda val: slider_changed(sldr_label, val)
    ).grid(row=g_row, sticky="news")
    g_row = g_row +1

    #delete market data
    nb.Button(but_frame, text="Delete Market Data", command=on_delete_markets).grid(row=g_row, sticky="nsew", padx=5, pady=5)
    g_row = g_row +1
    italic_font = tkFont.Font(family="Helvetica", size=8, slant="italic")
    nb.Label(but_frame, text="Delete cannot be undone.", font=italic_font).grid(row=g_row, sticky="nw", padx=10, pady=1)
    g_row = g_row +1

    #show at startup
    show_var = tk.BooleanVar(value=globals.SHOW_UI_AT_START)
    chk_hide = nb.Checkbutton(
        but_frame,
        text="Show UI at EDMC startup",
        variable=show_var,
        command=lambda v=show_var: toggle_showUIatStart(v.get())
    ).grid(row=g_row, sticky="nw", padx=5, pady=5)
    g_row = g_row +1

    #Open Log Directory
    nb.Button(but_frame, text="Open Log Directory\\Viewer", command=on_log_open).grid(row=g_row, sticky="nsew", padx=5, pady=5)
    g_row = g_row +1

    # NOTES FRAME ************************************************
    note_frame = nb.Frame(pref_frame, border=2, relief="groove")
    note_frame.grid(row=2, column=2, columnspan=2, sticky="nsew")

    #display button and highlighting notes
    text_widget = tk.Text(note_frame, height=19, width=85, wrap='word', font=('Verdana', 9), border=0)
    text_widget.tag_configure('big', font=('Verdana', 9, 'bold'))
    text_widget.tag_configure('underline', font=('Verdana', 9, 'underline'))

    """Button Descriptions
    X - deletes the current construction site. Handy if someone else completes it.
    < and > - shows the previous or next site in the list. (Bound the '<' and '>' keys for Voice Attack users.)
    $\\Ly\\Alt - toggles between cheapest, closest and alternate market. Prices and distances are tracked whenever you open a commodity market. (This is bound the the 'p' key for Voice Attack users.)
    Pause\\Unpause - pauses and unpause updating fleet carrier cargo from Fdev servers, which can become out of sync with game data. (Bound to 'u' key)

    Row highlighting
    Depending on where you are docked, rows are highlighted to indicate:
    Markets - market is selling the item and you have shortfall.
    Fleeet Carrier - site needs it and fleet carrier has some AND starship does not have enough.
    Construction site - site needs it and starship has some.

    Other
    Selecting -All- in the station dropdown list will display materials from all construction sites in a single view.
    """

    text_widget.insert(tk.END, "Button Descriptions\n", 'underline')
    text_widget.insert(tk.END, "X", 'big')
    text_widget.insert(tk.END, " - deletes the current construction site. Handy if someone else completes it.\n")
    text_widget.insert(tk.END, "< and >", 'big')
    text_widget.insert(tk.END, " - shows the previous or next site in the list. (Bound the '<' and '>' keys for Voice Attack users.)\n")
    text_widget.insert(tk.END, "$\\Ly\\Alt", 'big')
    text_widget.insert(tk.END, " - toggles between cheapest, closest and alternate market. Prices and distances are tracked whenever you open a commodity market. (This is bound the the 'p' key for Voice Attack users.)\n")
    text_widget.insert(tk.END, "O\\S", 'big')
    text_widget.insert(tk.END, " - toggles between orbital and surface markets. Works together with cheapest, closest and alternate. (Bound to 'o' key)\n")
    text_widget.insert(tk.END, "Pause\\Unpause", 'big')
    text_widget.insert(tk.END, " - pauses and unpause updating fleet carrier cargo from Fdev servers, which can become out of sync with game data. (Bound to 'u' key)\n\n")
    text_widget.insert(tk.END, "Row highlighting\n", 'underline')
    text_widget.insert(tk.END, "Depending on where you are docked, rows are highlighted to indicate:\n")
    text_widget.insert(tk.END, "Markets", 'big')
    text_widget.insert(tk.END, " - market is selling the item and you have shortfall.\n")
    text_widget.insert(tk.END, "Fleeet Carrier", 'big')
    text_widget.insert(tk.END, " - site needs it and fleet carrier has some AND starship does not have enough.\n")
    text_widget.insert(tk.END, "Construction site", 'big')
    text_widget.insert(tk.END, " - site needs it and starship has some.\n")
    text_widget.insert(tk.END, "Undocked", 'big')
    text_widget.insert(tk.END, " - no highlighting is done.\n\n")
    text_widget.insert(tk.END, "Other\n", 'underline')
    text_widget.insert(tk.END, "Selecting -All- in the station dropdown list will display materials from all construction sites in a single view.\n")

    text_widget.config(state='disabled')
    text_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    pref_frame.grid_columnconfigure(0, minsize=5)
    return pref_frame

def open_url():
    webbrowser.open_new("https://github.com/kfpopeye/EliteDangerous")

def slider_changed(lbl, val):
    val = int(float(val))
    s = "Window Opacity = " + str(val) + "%"
    lbl.config(text=s)
    config.set('ArchTrack_opcamt', val)
    if globals.ARCHITECT_GUI and globals.ARCHITECT_GUI.winfo_exists():
        globals.ARCHITECT_GUI.setAlpha(val)

def toggle_win_top(val):
    config.set('ArchTrack_wintop', bool(val))
    if globals.ARCHITECT_GUI and globals.ARCHITECT_GUI.winfo_exists():
        globals.ARCHITECT_GUI.setStayOnTop(bool(val))

def toggle_trans_bg(val):
    config.set('ArchTrack_tbg', bool(val))
    if globals.ARCHITECT_GUI and globals.ARCHITECT_GUI.winfo_exists():
        globals.ARCHITECT_GUI.setTransparentBg(bool(val))
        globals.ARCHITECT_GUI.setStyle()
        globals.ARCHITECT_GUI.refresh()

def on_log_open():
    import subprocess
    import sys
    from log_viewer import LogViewerGUI

    if sys.platform == 'darwin':
        subprocess.Popen(['open', globals.USER_DIR])
        
    elif sys.platform.startswith('linux'):
        try:
            # --- Flatpak / sandboxed environment ---
            if helpers.is_flatpak():
                logger.info("Detected Flatpak sandbox environment")
                noOpener = True
                # Prefer portal-aware tool
                for cmd in (["gio", "open", globals.USER_DIR], ["xdg-open", globals.USER_DIR]):
                    try:
                        subprocess.Popen(cmd)
                        logger.info("Opened folder via sandbox method: %s", cmd[0])
                        noOpener = False
                        break
                    except Exception as e:
                        logger.warning("Failed sandbox open with %s: %s", cmd[0], repr(e))

                if noOpener:
                    logger.error("No sandbox-compatible opener found.")

            # --- Native Linux ---
            else:
                try:
                    subprocess.Popen(["xdg-open", globals.USER_DIR])
                    logger.info("Opened folder via xdg-open")
                except Exception as e:
                    logger.error("xdg-open failed: %s", repr(e))

        except Exception as e:
            logger.error("Failed to open folder %s: %s", globals.USER_DIR, repr(e))
        
    elif sys.platform.startswith('win'):
        subprocess.Popen(['explorer', globals.USER_DIR])
        
    logviewer = LogViewerGUI(globals.EDMC_ROOT)

def on_column_rename(c, v):
    if globals.ARCHITECT_GUI and globals.ARCHITECT_GUI.winfo_exists():
        globals.ARCHITECT_GUI.rename_column(c, v)

def toggle_column(col, val):
    c = "ArchTrack_" + col.replace(" ", "_")
    config.set(c, val)

    if globals.ARCHITECT_GUI and globals.ARCHITECT_GUI.winfo_exists():
        globals.ARCHITECT_GUI.toggle_column(col, val)

def toggle_hide_provided(val):
    config.set('ArchTrack_hide_Provided', bool(val))
    if globals.ARCHITECT_GUI and globals.ARCHITECT_GUI.winfo_exists():
        globals.ARCHITECT_GUI.toggle_hide_provided(val)

def reset_Style(style):
    config.set('ArchTrack_theme', str(style))
    if globals.ARCHITECT_GUI and globals.ARCHITECT_GUI.winfo_exists():
        globals.ARCHITECT_GUI.reset_Style(style)

def on_delete_markets():
    try:
        if os.path.exists(globals.MARKET_LIB_PATH):
            os.remove(globals.MARKET_LIB_PATH)
            if globals.ARCHITECT_GUI and globals.ARCHITECT_GUI.winfo_exists():
                globals.ARCHITECT_GUI.refresh()
        old_library = os.path.join(globals.USER_DIR, "market_library.json")
        if os.path.exists(old_library):
            os.remove(old_library)
        logger.info("Deleted all market data.")
    except Exception as e:
        logger.error("Delete market Data error: %s", e)

def toggle_showUIatStart(b):
    globals.SHOW_UI_AT_START = b

def change_fcapi_mode(mode):
    config.set('ArchTrack_fcapimode', mode)
