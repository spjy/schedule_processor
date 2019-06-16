import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--inventory", help="Inventory CSV File", default="inventory.csv")
parser.add_argument("--bom", help="Bill of Materials CSV File", default="bom_items.csv")
parser.add_argument("--items", help="Project Status Items CSV File", default="project_status.csv")
parser.add_argument("--output", help="Output CSV File", default="output.csv")
args = parser.parse_args()

print('Evaluating items...')

# Rows to write to new CSV file
rows = []

# Dictionary of recipies
recipes = {}

# Dictionary of inventory
inventory = {}

# Open inventory csv
with open(args.inventory, newline='') as inventoryfile:
  # Open inventory
  items = csv.reader(inventoryfile)

  material = 0 # Counter variable for skipping first row of csv

  # Loop through items in the csv file
  for item in items:
    # Skip category row
    if material != 0:
      # Check if key not yet initialized
      if item[2] not in inventory:
        # Initialize key
        inventory[item[2]] = float(item[9])
      elif item[2] in inventory:
        # Accumulate key
        inventory[item[2]] = inventory[item[2]] + float(item[9])
  
    material = material + 1

# Open BOM csv for the product
with open(args.bom, newline='') as bomfile:
  # Read csv file for BOM
  bom = csv.reader(bomfile)

  recipe = 0 # Counter variable for skipping first row

  # Loop through each ingredient for product
  for subcomponent in bom:
    # Skip category row
    if recipe != 0:
      # Get all rows except for first
      if subcomponent[0] not in recipes:
        # Initialize variables
        recipes[subcomponent[0]] = {}
        recipes[subcomponent[0]][subcomponent[1]] = subcomponent[2]
      else:
        # Accumulate variables
        recipes[subcomponent[0]][subcomponent[1]] = subcomponent[2]

    recipe = recipe + 1

# Open main csv containing products
with open(args.items, newline='') as projectfile:
  # Read csv file
  projects = csv.reader(projectfile)

  product = 0 # Counter variable for skipping first row

  # Loop through projects in csv
  for project in projects:
    # Check if first row containing column names
    if product == 0:
      # Append runnable and BOM columns
      project.append('Runnable')
      project.append('BOM After Production')

      # Push to row
      rows.append(project)

    # Check if after first row containing thee data of csv
    if product != 0:

      # Dictionary for storing subcomponent and its quantity
      subcomponent_with_qty = {}

      # Check if project has a recipe
      if project[2] in recipes:
        # Loop over the dictionary of recipies for each project
        for subcomponent in recipes[project[2]]:

          if subcomponent in inventory:
            # Calculate quantity after making project (Inventory of subcomponent - product * subcomponent)
            qty_leftover = float(inventory[subcomponent]) - float(project[5]) * float(recipes[project[2]][subcomponent])

            # Store in dict for evaluating whether it can run
            subcomponent_with_qty[subcomponent] = qty_leftover
          else:
            subcomponent_with_qty[subcomponent] =  -(float(project[5]) * float(recipes[project[2]][subcomponent]))

      # Determine whether the project can run by checking if any quantity is negative.
      can_run = True # By default, the project can run.
      dictionary_to_string = '' # String to append to for the BOM statuses.

      if not subcomponent_with_qty:
        can_run = False
      else:
        item = 0 # Counter for skipping newline on first line
        for subcomponent_qty in subcomponent_with_qty:
          # Check if the inventory can dip below zero
          if subcomponent_with_qty[subcomponent_qty] < 0:
            can_run = False
          if item == 0:
            dictionary_to_string = dictionary_to_string + f'{subcomponent_qty}: {subcomponent_with_qty[subcomponent_qty]}'
          else:
            # include new line after first instance
            dictionary_to_string = dictionary_to_string + f'\n{subcomponent_qty}: {subcomponent_with_qty[subcomponent_qty]}'
          item = item + 1


      # Append to end of each row
      project.append(str(can_run))
      project.append(dictionary_to_string)

      rows.append(project)

    product = product + 1

# Write output to csv file
with open(args.output, 'w') as csvoutput:
  writer = csv.writer(csvoutput, lineterminator='\n')
  writer.writerows(rows)
  print(f'Rows written to {args.output}.')
