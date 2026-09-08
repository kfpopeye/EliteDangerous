# EliteDangerous

## Architect Tracker
Displays commodities required, provided and needed when you land at a construction site, market or fleet carrier and tracks cargo in your fleet carrier and starship.
The focus is to create a simple to use and hands free tracker for system colonisation. I will be adding features often so check back here often. This was created using ChatGPT. It probably took me as long to create as a human could have programmed manually but I have no experience programming in Python or for the EDMC so it is kind of impressive.

<img width="833" height="593" alt="Screenshot 2026-03-20 192521" src="https://github.com/user-attachments/assets/04c893f3-c70b-4bbc-832b-5c4bed7b1abd" />

Dark mode

<img width="833" height="582" alt="Screenshot 2026-03-20 192537" src="https://github.com/user-attachments/assets/57065805-b590-4e85-bdc1-dcef7ab051d6" />

Light Mode

<img width="1121" height="813" alt="Screenshot 2026-06-11 194230" src="https://github.com/user-attachments/assets/8783bce0-6144-40a3-9726-ae3f78b6388b" />

Settings Window

### Discussion
https://forums.frontier.co.uk/threads/colonization-tool-architect-tracker.636854/#post-10621804

### Install Instructions
1. Download a zip file of the latest release <a href="https://github.com/kfpopeye/EliteDangerous/archive/refs/tags/v1.6.zip">here</a> or by clicking the "Releases" link to the right and then selecting the latest release shown.
2. Create a directory called "ArchitectTracker" (make sure there are no spaces) in the the ED: Marketplace Connector plugins folder.
3. Extract the downloaded zip file into this directory. Make sure no subdirectories are created. All files should appear directly inside the "ArchitectTracker" directory.
4. Start EDMC.

### Usage
+ When you land at a construction site the plugin will (after a few moments) list all the commodities and amounts required, provided and needed. You can switch between sites from the dropdown list in the upper left or the ">" button. The window will resize itself to fit all the commodities.
+ The "Pref Market" column displays either the cheapest, closest or alternate market where that commidity has been found. This list is further filtered by orbital or surface markets. See "Prefered Markets" section below for more information.
+ To display\update your fleet carrier cargo, open the "Carrier Management" in-game tool. The quantities will appear after a few moments (this can take a while and occasionaly display incorrect number). If you are also selling commodities from your fleet carrier, you will need to update this list as needed (sales are not tracked).
+ Starship cargo will be displayed automatically.
+ The shortfall column displays how much of a commodity you still need to aquire.
+ Settings are available in the E:D Market Connector under File menu->Settings->ArchitectTracker tab. You can choose whioch columns to display, set the text displayed in the column header and other settings (see screenshot above).
+ Rows are highlighted (see screenshots above) depending on where you are docked, rows are highlighted to indicate:
  + Markets - market is selling the item and you have shortfall.
  + Fleeet Carrier - site needs it and fleet carrier has some AND starship does not have enough.
  + Construction site - site needs it and starship has some.
+ Closing the Architect Tracker window will stop the sites, commodities and markets from being tracked. This is handy if you're landing at markets but don't want the information to override your current closest\cheapest information.
+ Buttons on the UI:
  - <b>X</b> - deletes currently shown construction site. Disabled when -ALL- sites are listed.
  - <b><</b> or <b>></b> - changes to previous or next site in list. Wraps around list.
  - <b>$\Ly\Alt</b> - toggles between showing the cheapest, closest or alternate markets in the preferred market column. See "Preferred Markets" section below for more information.
  - <b>O\S</b> - toggles between showing orbital or surface markets in the preferred market column. See "Preferred Markets" section below for more information.
  - <b>Pause</b> or <b>Unpause</b> - this button next to the Carrier name will pause or unpause updating the fleet carrier cargo quantities from Fdev's fleet carrier companion api. See section below.

### Preferred Markets
- The "Preferred Market" column displays markets you have found that sell construction commodities. The system name is not shown so it is suggested that you bookmark the stations.
- Markets can be filtered using the $\Ly\Alt and O\S buttons at the top of the inteface. Filtering includes:
  - $ : the station that has the cheapest sell price that was below your construction sites buy price.
  - Ly : the station that is closest to your colony system whose sell price was below your construction sites buy price.
  - Alt : the station that is closest to your colony system whose sell price was NOT below your construction sites buy price.
  - O : orbital stations are shown. If none have been found, a surface settlement is shown with an asterix (*) prepended to the name. Otherwise it will be blank.
  - S : surface settlement are shown. If none have been found, an orbital station is shown with an asterix (*) prepended to the name. Otherwise it will be blank.
- Note: if you started using this plugin prior to version 1.4, the old data will be shown with a double asterix (**) prepended to the name untill you have landed at the market again.

### Fleet Carrier Cargo Quantities
- Information coming from the fleet carrier CAPI (fcapi) queries can often become unsyncronized with the actual amounts shown in the game. This causes Architect Tracker to sometimes display incorrect fleet carrier cargo quantities. As a work around, I have added a pause\unpause button next to the carrier name.
- Transferring cargo to\from your starship or purchasing\selling commodities while docked at your fleet carrier are still tracked by Architect Tracker regardless.
- The pause\unpause button has 2 modes it can operate which can be set in the "Settings" of EDMC:
  - "First then pause" mode will accept the first fcapi query then ignore any others unless the pause button is clicked. This is the default mode. I have found that the first query is usually accurate if I haven't played for over an hour.
  - "Only when UNpaused" mode will accept all fcapi queries unless you pause them.
- Note: if you sell commodities to other players from your fleet carrier, pausing fcapi queries will cause the fleet carrier cargo amounts in Architect Tracker to become out of sync. Unpausing will, hopefully, restore them.

### Notes
1. VR programs like Desktop+ can display this window inside the game for you.
2. For Voice Attack users:
  - The "<", ">" buttons are bound to the keys "<", ">" respectiveley.
  - The "$\Ly\Alt" button is bound to key "p".
  - The "O\S" button is bound to key "o".
  - The pause\unpause button is bound to "u".
  - Also "t" has been bound to the Architect Tracker button on the EDMC window so you can show\hide the Architect Tracker interface to stop tracking.

### Notable Changes
+ 2025/04/12 : Added support for multiple construction sites. Sites are removed automaticly when they are completed.
+ 2025/04/19 : Added feature - commodities required for construction are highlighted when a commodity market is opened.
+ 2025/04/25 : Added fleet carrier cargo information - open the carrier management tool in-game to populate\refresh this list. NOTE: Tracks cargo transfers to/from FC but not market sales.
+ 2025/04/30 : Added starship cargo tracking and dark theme colours.
+ 2025/05/01 : Deleted unworking style , ad setings for beter use
+ 2025/05/03 : Adaptation for new naming conwention for colonisation ship
+ 2025/05/06 : Added dark\light mode, moved setting to EDMC setting tab, setting saved to EDMC settings and window auto resized to fit content.
+ 2025/05/09 : Added delete station button to remove unwanted stations, added next station button to change list to next station in list (using Desktop+ in VR doesn't show the dropdown menu also button has a hot key assigned to it ">" so it can be used by voice attack), added alternating row colours back in.
+ 2025/05/15 : Added preferred market tracking, added row highlighting, added information to settings tab and added column header renaming.
+ 2025/05/29 : Added pause to tracking. Closing the Architect Tracker window will stop the commodities from being tracked.
+ 2025/06/29 : [version 1.0] Added features - can now adjust transparent background, window opacity and stay on top of the main gui in the settings menu. Also added a verion number for bug reporting.
+ 2025/08/05 : [version 1.1] Added feature - Selecting -All- in the station dropdown list will display materials from all construction sites in a single view.
+ 2025/11/03 : [Version 1.2] Added previous site button to UI, owned fleet carrier no longer registers as market, remove version number from window title and improved start up to detect if landed on a market or carrier.
+ 2026/02/12 : [Version 1.2.2] Fixed bug that prevented Material column from displaying for some users.
+ 2026/02/23 : [Version 1.3] Added pause button for fleet carrier cargo, added totals row at bottom of list, delete site button is disabled when ALL sites are shown, smaller bug fixes.
+ 2026/03/20 : [Version 1.4] Added alternate and orbital\surface filtering to preferred markets. Renamed construction sites and markets will now be updated when you land on them the next time. Minor UI beautifications.
+ 2026/04/04 : [Version 1.5] Changed highlight rules when on fleet carrier. Now, if you have enough of a commodity on your starship to meet the needs of the construction site, the commodity will no longer be highlighted.
+ 2026/06/11 : [Version 1.6] Major bug fixes for Linux users. Special thanks to Commanders PatientNr0, mgrzegor, Fasgort and LiamtheLion879
 for taking time to report bugs and work with me to fix them. Added log viewer to settings tab which should helppeople report bugs.
+ 2026/09/08 : [Version 1.7] Commodities are now tracked even if not needed at a construction site or sold out at market, added more logging information, corrected logic error, corrected pricing error.
