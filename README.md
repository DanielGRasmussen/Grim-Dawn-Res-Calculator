# Grim Dawn Resistance Optimizer

This tool helps Grim Dawn players optimize their character's resistances by suggesting the best combination of components and augments based on current gear, level, and faction standings.

## Files

- `optimizer.py`: Main script that runs the optimization algorithm
- `addon_parser.py`: Parses raw data for components and augments
- `resistance.csv`: Current resistance values and goals
- `slots.csv`: Equipment slots and their compatibility with components/augments
- `stats.csv`: Player statistics including level and faction standings
- `blacklist.csv`: Items to exclude from consideration
- `components_raw.txt`: Raw data for components (from Grim Tools)
- `augments_raw.txt`: Raw data for augments (from Grim Tools)

## Usage

1. Modify the CSV files to reflect your character's current state:

   a. Update `resistance.csv` with your current resistances and goals

   b. Adjust `slots.csv` to represent your available gear slots:
      - Use 0 to indicate an open slot (available for optimization)
      - Use 1 to indicate a used slot (not available for optimization)
      Example:
      ```
      Name,Component,Augment
      Head,0,0     # Both component and augment slots are open
      Body,1,0     # Component slot is used, augment slot is open
      Ring,0,1     # Component slot is open, augment slot is used
      ```

   c. Update `stats.csv` with your character's level, crafting ability, and faction standings. 
      The faction standings use the following numeric scale:
      - 1: Tolerated
      - 2: Friendly
      - 3: Honored
      - 4: Revered

      For factions you haven't interacted with, use -1.

      Example:
      ```
      player_level,crafts,devils_crossing,rovers,homestead,...
      100,1,1,1,1,...
      ```
      This indicates a level 86 character who can craft, is Revered with Devil's Crossing, 
      and Honored with the Rovers and Homestead.

      The `crafts` field should be 1 if the character can craft components, 0 if not.

   d. Add any items to `blacklist.csv` that you want to exclude

2. Ensure `components_raw.txt` and `augments_raw.txt` are up to date with the latest game data

3. Run the optimizer:
   Open a command prompt or terminal in the directory containing the script files, then type:
   
   python optimizer.py
   
   If you're using Python 3 specifically on a system where both Python 2 and 3 are installed, you might need to use:
   
   python3 optimizer.py
   
   Press Enter to run the script. The optimizer will process the data from your CSV files and the raw text files, then output the results showing the best combination of components and augments for your character, along with the final resistance values.

4. The script will output the best combination of components and augments, along with the resulting resistance values

## Requirements

- Python 3.x
- CSV module (usually included in standard Python installation)

## Notes

- The optimizer prioritizes augments over components
- It respects slot limitations and item availability based on player stats
- Blacklisted items are completely excluded from consideration
- The tool assumes you have the necessary materials to craft components and augments (I recommend blacklisting them)

## Updating Game Data

To update the raw data files:
1. Visit [Components](https://www.grimtools.com/db/category/components/items) and [Augments](https://www.grimtools.com/db/category/augments/items)
2. Copy the data from "Common (##)" to the bottom of all items
3. Remove all "Rarity (##)" and "Dropped from ___" style lines manually
4. Save the cleaned data to `components_raw.txt` and `augments_raw.txt` respectively

## Disclaimer

This tool is for informational purposes only. No clue if it will always work and no clue if it filters out everything properly. Odds are high you'll reach a better build from checking manually due to extra effects on components/augments.