import os
import json
import math
from typing import Union
import traceback

from config import appname, appversion, config

import globals
from globals import logger

# for linux
def is_flatpak():
    return (
        os.path.exists("/.flatpak-info") or
        "FLATPAK_SANDBOX_DIR" in os.environ or
        os.environ.get("FLATPAK_ID") is not None
    )

# --- Settings persistence ---
def load_gui_settings():
    try:
        vis = {}
        cols = list(globals.DEFAULT_COLUMNS.keys())
        for c in cols:
            key = "ArchTrack_" + c.replace(" ", "_")
            if config.get(key) is None:
                vis[c] = True
                logger.info(f"Key: %s not found using default setting.", key)
            else:
                vis[c] = config.get_bool(key)
        vis["Material"] = True

        if config.get('ArchTrack_hide_Provided') is None:
            hid = False
            logger.info(f"Hid not found using default settings.")
        else:
            hid = config.get_bool('ArchTrack_hide_Provided')

        if config.get('ArchTrack_theme') is None:
            theme = "Dark Mode"
            logger.info(f"Theme not found using default settings.")
        else:
            theme = config.get_str('ArchTrack_theme')

        if config.get('ArchTrack_cols') is None:
            col_display = cols
            logger.info(f"Column names not found using default settings.")
        else:
            col_display = config.get_list('ArchTrack_cols')

        if config.get('ArchTrack_tbg') is None:
            trans_bg = False
            logger.info(f"trans_bg not found using default settings.")
        else:
            trans_bg = config.get_bool('ArchTrack_tbg')

        if config.get('ArchTrack_wintop') is None:
            win_top = False
            logger.info(f"win_top not found using default settings.")
        else:
            win_top = config.get_bool('ArchTrack_wintop')

        if config.get('ArchTrack_opcamt') is None:
            opac_amt = 100
            logger.info(f"opac_amt not found using default settings.")
        else:
            opac_amt = config.get_int('ArchTrack_opcamt')

        return vis, hid, theme, col_display, trans_bg, win_top, opac_amt
    except Exception as e:
        logger.error(f"Error loading GUI settings: {e}")
        return globals.DEFAULT_COLUMNS, False, "Dark Mode", cols

def save_gui_settings():
    logger.info(f"Saving settings.")
    if not globals.ARCHITECT_GUI or not globals.ARCHITECT_GUI.winfo_exists():
        return
    try:
        for col, vis in globals.ARCHITECT_GUI.column_visibility.items():
            c = "ArchTrack_" + col.replace(" ", "_")
            config.set(c, vis)
        config.set('ArchTrack_hide_Provided', bool(globals.ARCHITECT_GUI.hide_provided))
        config.set('ArchTrack_theme', str(globals.ARCHITECT_GUI.theme))
        config.set('ArchTrack_showUI', bool(globals.SHOW_UI_AT_START))
        config.set('ArchTrack_cols', list(globals.ARCHITECT_GUI.column_names))
        config.set('ArchTrack_tbg', bool(globals.ARCHITECT_GUI.trans_bg))
        config.set('ArchTrack_wintop', bool(globals.ARCHITECT_GUI.win_top))
        config.set('ArchTrack_opcamt', int(globals.ARCHITECT_GUI.opac_amount))
    except Exception as e:
        logger.error(f"Error saving GUI settings: {e}")

def compare_material_to_list(materials):
    global COMMODITIES
    
    for name in materials:
        if name and not isItemConstructionCommodity(name):
            logger.warning("%s not found in commodity list, adding it.", name)
            with open(globals.COMMODITY_FILE, "a", encoding="utf-8") as f:
                f.write(name + "\n")
                COMMODITIES.add(name)

# --- Helpers ---
def calculate_distance(x1: Union[int, float], y1: Union[int, float], z1: Union[int, float], x2: Union[int, float], y2: Union[int, float], z2: Union[int, float]):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

def is_station_complete(materials):
    return all(info["ProvidedAmount"] >= info["RequiredAmount"] for info in materials.values())
    
def get_current_location_from_journal():
    journal_dir = os.path.dirname(globals.CARGO_JSON)
    if not os.path.exists(journal_dir):
        return None
    journal_files = [f for f in os.listdir(journal_dir) if f.startswith("Journal.") and f.endswith(".log")]
    if not journal_files:
        return None
    latest_journal = max(journal_files, key=lambda f: os.path.getmtime(os.path.join(journal_dir, f)))
    with open(os.path.join(journal_dir, latest_journal), "r") as f:
        for line in reversed(f.readlines()):
            if '"StarPos"' in line:
                data = json.loads(line)
                if "StarPos" in data:
                    logger.info("Found current location in journal.")
                    return tuple(data["StarPos"])
    return None

def save_facility_requirements(resources, station_name, mID):
    materials = {r["Name"]: {"Name_Localised": r["Name_Localised"],
                                   "RequiredAmount": r["RequiredAmount"],
                                   "ProvidedAmount": r["ProvidedAmount"],
                                   "Price": r["Payment"]}
                     for r in resources}
    try:
        with open(globals.SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}

    compare_material_to_list(materials)

    if station_name in data and not data[station_name].get("ID"):   #because we only tracked ID's after 1.3
        data[station_name]["ID"] = mID
        logger.debug("Added ID to: %s", station_name)

    if station_name in data and data[station_name]["ID"] == mID:
        if is_station_complete(materials):
            logger.info("Facility %s is complete. Removing from list.", station_name)
            data.pop(station_name, None)
        else:
            data[station_name]["materials"] = materials
            logger.info("Updating facility %s.", station_name)
    else:
        for s, info in data.items():
            if mID == info.get("ID"): #check for renamed construction sites
                data.pop(s, None)
                logger.info("Removed facility %s because it is now %s.", s, station_name)
                break
        if not is_station_complete(materials):
            data[station_name] = {"Location": globals.CURRENT_LOCATION, "ID": mID, "materials": materials}
            logger.info("Adding facility %s to list.", station_name)

    try:
        with open(globals.SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error("Error saving data: %s", e)

def load_facility_requirements():
    if not os.path.exists(globals.SAVE_FILE):
        return {}
    try:
        with open(globals.SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error("Error reading save file: %s", e)
        return {}
    cleaned = {s: info for s, info in data.items() if not is_station_complete(info.get("materials", {}))}
    if cleaned != data:
        try:
            with open(globals.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(cleaned, f, indent=4)
        except Exception as e:
            logger.error("Error writing cleaned data: %s", e)

    if not globals.SITE_LOCATION and cleaned:
        first_site = next(iter(cleaned.values()))
        if first_site and first_site.get("Location"):
            globals.SITE_LOCATION = first_site.get("Location")
            logger.info("Set site location to: %s", globals.SITE_LOCATION)
        else:
            globals.SITE_LOCATION = None

    return cleaned

def is_facility(station):
    # Load new data
    data = load_facility_requirements()
    # Prepare data for display
    cleaned = [
        (
          (full.split(':', 1)[-1].strip() if ':' in full else
           full.split(';', 1)[-1].strip() if ';' in full else full)
        )
        for full in data
    ]

    return station in cleaned

# load cargo for currently piloted ship
def load_starship_cargo_data():
    if not os.path.exists(globals.CARGO_JSON):
        return []
    try:
        with open(globals.CARGO_JSON, "r", encoding="utf-8") as f:
            cargo = json.load(f)
        return cargo.get("Inventory", [])
    except Exception as e:
        logger.error("Error loading cargo data: %s", e)
        return []

# is the item a construction commodity
COMMODITIES = None
def ensure_commodities_loaded() -> bool:
    global COMMODITIES

    if COMMODITIES is None:
        if not os.path.exists(globals.COMMODITY_FILE):
            logger.error("Commodity data file does not exist: %s", globals.COMMODITY_FILE)
            return False

        with open(globals.COMMODITY_FILE, "r") as f:
            COMMODITIES = [line.strip() for line in f]
    return True

def isItemConstructionCommodity(item_name) -> bool:
    if not ensure_commodities_loaded():
        return False

    if item_name in COMMODITIES:
        logger.debug("Item: %s is a construction commodity.", item_name)
        return True
    else:
        logger.debug("Item: %s is NOT a construction commodity.", item_name)
        return False

# does the item cost less than all buy prices at construction sites
def isItemBelowConstructionCost(item_name, item_price) -> bool:
    prices = []

    site_data = load_facility_requirements()
    for site in site_data.values():  # iterate over site dicts directly
        materials = site.get("materials", {})
        for mat, vals in materials.items():
            if mat == item_name:
                price = vals.get("Price")
                if price is not None:
                    prices.append(price)

    in_demand = all(item_price < price for price in prices)
    if in_demand:
        logger.info("Item '%s' is in demand (price: %s < all site prices: %s)", item_name, item_price, prices)
    else:
        logger.info("Item '%s' is NOT in demand (price: %s vs site prices: %s)", item_name, item_price, prices)
    return in_demand

def check_if_market_renamed(market_lib, market):
    station_name = market.get("StationName")
    station_id = market.get("MarketID")
    m = get_market_by_station_id(market_lib, station_id)
    if m and m["StationName"] != station_name:
        logger.info("Updating station name: '%s' [%s] to %s", m["StationName"], station_id, station_name)
        m["StationName"] = station_name

def get_market_by_station_id(data, station_id):
    for market in data["Markets"]:
        if market["StationID"] == station_id:
            return market
    return None

def ensure_market_exists(market_lib, station_name, station_id):
    if get_market_by_station_id(market_lib, station_id) is None:
        market_lib["Markets"].append({
            "StationName": station_name,
            "Location": globals.CURRENT_LOCATION,
            "StationID": station_id,
            "Type": globals.DOCKED_STATION_TYPE.name
        })
        logger.debug("Adding new market: %s", station_name)

def get_market_library():
    # Load existing persistent dictionary if available or create default
    if os.path.exists(globals.MARKET_LIB_PATH):
        with open(globals.MARKET_LIB_PATH, "r", encoding="utf-8") as f:
            market_lib = json.load(f)
    else:
        market_lib = {}
        market_lib.setdefault("Commodities", {})
        market_lib.setdefault("Markets", [])
    return market_lib

#a list of the cheapest and closest markets that are selling an item
def update_market_library() -> None:
    if not os.path.exists(globals.MARKET_JSON):
        logger.warning("Market data file does not exist: %s", globals.MARKET_JSON)
        return

    #do not update unless we know where we are landed at
    if globals.DOCKED_STATION_TYPE == globals.STATION_TYPE.Unknown:
        logger.warning("Station type unknown.")
        return

    try:
        market_lib = get_market_library()

        # Load market data from EDMC
        with open(globals.MARKET_JSON, "r", encoding="utf-8") as f:
            market = json.load(f)

        check_if_market_renamed(market_lib, market)

        station_name = market.get("StationName")
        items = market.get("Items", [])
        station_id = market.get("MarketID")

        if not station_name or not station_id:
            logger.warning("Invalid market data")
            return
            
        not_selling_list = None
        if ensure_commodities_loaded():
            not_selling_list = list(COMMODITIES)

        for item in items:
            if item.get("BuyPrice", 0) > 0:  # Item is sold here but may be out of stock
                item_name = item.get("Name")
                m_price = item.get("BuyPrice")

                if item_name and isItemConstructionCommodity(item_name):
                    not_selling_list.remove(item_name)
                    commodity = market_lib["Commodities"].setdefault(item_name, {})

                    if isItemBelowConstructionCost(item_name, m_price):
                        cheap_markets = commodity.setdefault("CheapMarkets", {})
                        cheap_entry = cheap_markets.get(globals.DOCKED_STATION_TYPE.name)

                        if not cheap_entry or m_price < cheap_entry["Price"]: # Update CheapMarket if cheaper or no entry
                            ensure_market_exists(market_lib, station_name, station_id)
                            logger.debug("Updating CheapMarket for: %s", item_name)
                            cheap_markets[globals.DOCKED_STATION_TYPE.name] = {
                                "Price": m_price,
                                "StationID": station_id
                            }
                        elif station_id == cheap_entry.get("StationID"): #update price if station is already cheapest entry
                            logger.debug("Updating price for: %s", item_name)
                            cheap_entry["Price"] = m_price

                        # Update ClosestMarket if closer or no entry
                        close_markets = commodity.setdefault("ClosestMarkets", {})
                        close_entry = close_markets.get(globals.DOCKED_STATION_TYPE.name)
                        if close_entry:
                            m = get_market_by_station_id(market_lib, close_entry["StationID"])
                            existing_distance = calculate_distance(*m["Location"], *globals.SITE_LOCATION)
                        else:
                            existing_distance = float("inf")
                        if globals.CURRENT_LOCATION and globals.SITE_LOCATION:
                            new_distance = calculate_distance(*globals.CURRENT_LOCATION, *globals.SITE_LOCATION)
                        else:
                            new_distance = float("inf")
                        if new_distance < existing_distance:
                            ensure_market_exists(market_lib, station_name, station_id)
                            logger.debug("Updating ClosestMarket for: %s", item_name)
                            close_markets[globals.DOCKED_STATION_TYPE.name] = {
                                "Price": m_price,
                                "StationID": station_id
                            }
                    else:
                        logger.debug("Item %s was expensive.", item_name)
                        # Update alternate market if closer or no entry
                        cheap_m_list = commodity.setdefault("CheapMarkets", {})
                        cheap_entry = cheap_m_list.get(globals.DOCKED_STATION_TYPE.name)
                        close_m_list = commodity.setdefault("ClosestMarkets", {})
                        close_entry = close_m_list.get(globals.DOCKED_STATION_TYPE.name)
                        alt_m_list = commodity.setdefault("AlternateMarkets", {})
                        alt_entry = alt_m_list.get(globals.DOCKED_STATION_TYPE.name)

                        #if this market is already listed as cheap or closest market for item, skip it
                        if (cheap_entry and cheap_entry.get("StationID") == station_id) or (close_entry and close_entry.get("StationID") == station_id):
                            logger.debug("%s was already a cheap or closest entry.", station_name)
                            continue

                        if alt_entry:
                            m = get_market_by_station_id(market_lib, alt_entry["StationID"])
                            existing_distance = calculate_distance(*m["Location"], *globals.SITE_LOCATION)
                        else:
                            existing_distance = float("inf")
                        if globals.CURRENT_LOCATION and globals.SITE_LOCATION:
                            new_distance = calculate_distance(*globals.CURRENT_LOCATION, *globals.SITE_LOCATION)
                        else:
                            new_distance = float("inf")
                        if new_distance < existing_distance:
                            ensure_market_exists(market_lib, station_name, station_id)
                            logger.debug("Updating AlternateMarket for: %s", item_name)
                            alt_m_list[globals.DOCKED_STATION_TYPE.name] = {
                                "Price": m_price,
                                "StationID": station_id
                            }
                        else:
                            logger.debug("%s has a closer AlternateMarket", item_name)
                            
                    market_lib["Commodities"][item_name] = commodity
        
        if not_selling_list != None:
            purge_market_from_other_commodities(market_lib, not_selling_list, station_id, station_name) #removes station ID if no longer selling commodities
        # Save updated dictionary
        with open(globals.MARKET_LIB_PATH, "w", encoding="utf-8") as f:
            json.dump(market_lib, f, indent=2)
        remove_from_old_market_library(station_name) #purge old v1.3 library

    except json.JSONDecodeError as e:
        logger.error("JSON decode error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        logger.error("Traceback:\n%s", traceback.format_exc())
        
#remove station ID if no longer selling commodities
def purge_market_from_other_commodities(market_lib, comm_list, station_id, station_name):
    for comm in comm_list:
        commodity = market_lib["Commodities"].get(comm)
        if not commodity:
            continue
        cheap_m_list = commodity.setdefault("CheapMarkets", {})
        cheap_entry = cheap_m_list.get(globals.DOCKED_STATION_TYPE.name)
        close_m_list = commodity.setdefault("ClosestMarkets", {})
        close_entry = close_m_list.get(globals.DOCKED_STATION_TYPE.name)
        alt_m_list = commodity.setdefault("AlternateMarkets", {})
        alt_entry = alt_m_list.get(globals.DOCKED_STATION_TYPE.name)

        if (cheap_entry and cheap_entry.get("StationID") == station_id):
            del cheap_m_list[globals.DOCKED_STATION_TYPE.name]
            logger.info("%s is no longer selling %s", station_name, comm)
        if (close_entry and close_entry.get("StationID") == station_id):
            del close_m_list[globals.DOCKED_STATION_TYPE.name]
            logger.info("%s is no longer selling %s", station_name, comm)
        if (alt_entry and alt_entry.get("StationID") == station_id):
            del alt_m_list[globals.DOCKED_STATION_TYPE.name]
            logger.info("%s is no longer selling %s", station_name, comm)

def getPreferedMarket()->globals.MARKET_MODE:
    if config.get('ArchTrack_prefCheap') is not None:   #setting not used since v1.3
        config.delete('ArchTrack_prefCheap')

    if config.get('ArchTrack_prefMarket') is None:
        mode = globals.MARKET_MODE.Cheapest
        config.set('ArchTrack_prefMarket', mode.value)
    else:
        value = config.get_int('ArchTrack_prefMarket')
        mode = globals.MARKET_MODE(value)
    return mode

def getPreferedType()->globals.STATION_TYPE:
    if config.get('ArchTrack_prefType') is None:
        type = globals.STATION_TYPE.Orbital
        config.set('ArchTrack_prefType', type.value)
    else:
        value = config.get_int('ArchTrack_prefType')
        type = globals.STATION_TYPE(value)
    return type
    
    #purge old v1.3 library until it is empty
def remove_from_old_market_library(station_name):
    # Load existing persistent dictionary if available
    old_library = os.path.join(globals.USER_DIR, "market_library.json")
    if os.path.exists(old_library):
        with open(old_library, "r", encoding="utf-8") as f:
            market_lib = json.load(f)
    else:
        return

    location = globals.CURRENT_LOCATION
    commodities_to_delete = []

    for commodity, markets in market_lib.items():
        markets_to_delete = []

        for market_type, market_data in markets.items():
            if (
                market_data["StationName"] == station_name and
                tuple(market_data["Location"]) == location
            ):
                markets_to_delete.append(market_type)

        # remove matching markets
        for market_type in markets_to_delete:
            del markets[market_type]

        # mark empty commodities
        if not markets:
            commodities_to_delete.append(commodity)

    # remove empty commodities
    for commodity in commodities_to_delete:
        del market_lib[commodity]

    # if no commodities remain, delete file
    if not market_lib:
        os.remove(old_library)
        logger.info(f"{old_library} deleted (no commodities left).")
        return

    # otherwise save cleaned data
    with open(old_library, "w") as f:
        json.dump(market_lib, f, indent=2)

    logger.info("Matching stations removed and file updated.")
    
def get_old_prefMarket_name(material): #see if pre v1.3 market library has an entry
    try:
        # Load existing persistent dictionary if available
        old_library = os.path.join(globals.USER_DIR, "market_library.json")
        if os.path.exists(old_library):
            with open(old_library, "r", encoding="utf-8") as f:
                market_lib = json.load(f)
        else:
            return ""

        resource = market_lib.get(material)
        if not resource:
            return ""

        pref = getPreferedMarket()
        if pref == globals.MARKET_MODE.Cheapest:
            market = resource.get("CheapMarket")
        elif pref == globals.MARKET_MODE.Closest:
            market = resource.get("ClosestMarket")
        else:
            market = resource.get("AlternateMarket")
            
        if not market:
            return ""

        if market.get("StationName"):
            station_name = market.get("StationName")
            return "**" + station_name    

    except json.JSONDecodeError as e:
        logger.error("JSON decode error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        logger.error("Traceback:\n%s", traceback.format_exc())
    
    return "Old Err"

def get_prefMarket_name(material):
    try:
        market_lib = get_market_library()
        resource = market_lib["Commodities"].get(material)
        if not resource:
            return get_old_prefMarket_name(material)

        pref = getPreferedMarket()
        if pref == globals.MARKET_MODE.Cheapest:
            markets = resource.get("CheapMarkets")
        elif pref == globals.MARKET_MODE.Closest:
            markets = resource.get("ClosestMarkets")
        else:
            markets = resource.get("AlternateMarkets")

        if not markets:
            markets = resource.get("AlternateMarkets")
            if not markets:
                return get_old_prefMarket_name(material)
        
        if getPreferedType() == globals.STATION_TYPE.Orbital:
            m = markets.get(globals.STATION_TYPE.Orbital.name)
            if not m:
                m = markets.get(globals.STATION_TYPE.Surface.name)
                if m:
                    #return non-prefered type as marked alternate
                    return "*" + get_market_by_station_id(market_lib, m["StationID"]).get("StationName")
            if not m:
                return get_old_prefMarket_name(material)
        else:
            m = markets.get(globals.STATION_TYPE.Surface.name)
            if not m:
                m = markets.get(globals.STATION_TYPE.Orbital.name)
                if m:
                    #return non-prefered type as marked alternate
                    return "*" + get_market_by_station_id(market_lib, m["StationID"]).get("StationName")
            if not m:
                return get_old_prefMarket_name(material)

        return get_market_by_station_id(market_lib, m["StationID"]).get("StationName")

    except json.JSONDecodeError as e:
        logger.error("JSON decode error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        logger.error("Traceback:\n%s", traceback.format_exc())

    return "Error"

def is_mat_in_stock(material) -> bool:
    # Load market data from EDMC
    with open(globals.MARKET_JSON, "r", encoding="utf-8") as f:
        market = json.load(f)

    # Load market info
    station_name = market.get("StationName")
    items = market.get("Items", [])

    for item in items:
        if material == item.get("Name"):
            if item and item.get("Stock", 0) > 0: #if item is for sale
                return True
    return False

# --- Plugin Hooks ---
def show_gui():
    from architecttrackergui import ArchitectTrackerGUI
    if not globals.ARCHITECT_GUI or not globals.ARCHITECT_GUI.winfo_exists():
        globals.ARCHITECT_GUI = ArchitectTrackerGUI(globals.EDMC_ROOT)
    else:
        globals.ARCHITECT_GUI.lift()
        globals.ARCHITECT_GUI.refresh()
    globals.AT_BUTTON.set("Hide Architect Tracker (tracking)")

def toggle_gui():
    from architecttrackergui import ArchitectTrackerGUI
    if not globals.ARCHITECT_GUI or not globals.ARCHITECT_GUI.winfo_exists():
        globals.AT_BUTTON.set("Hide Architect Tracker (tracking)")
        globals.ARCHITECT_GUI = ArchitectTrackerGUI(globals.EDMC_ROOT)
    else:
        globals.AT_BUTTON.set("Show Architect Tracker (tracking disabled)")
        globals.ARCHITECT_GUI.destroy()

def on_key_press(event):
    if event.char == 't':
       toggle_gui()
       return

    if not globals.ARCHITECT_GUI or not globals.ARCHITECT_GUI.winfo_exists() or not globals.SITE_LOCATION:
        return

    if event.char == '>':
        globals.ARCHITECT_GUI.on_next_station()
    elif event.char == '<':
        globals.ARCHITECT_GUI.on_prev_station()
    elif event.char == 'p':
        globals.ARCHITECT_GUI.on_toggle_prefMarket()
    elif event.char == 'o':
        globals.ARCHITECT_GUI.on_toggle_prefType()
    elif event.char == 'u':
        globals.ARCHITECT_GUI.on_canvas_click(event)
