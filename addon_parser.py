import re
import csv

unavailable = ["Ugdenbog Leather", "Spellscorched Plating", "Titan Plating", "Tainted Heart", "Sacred Plating"]

class Addon:
	def __init__(self, name, raw_text):
		self.name = name
		self.raw_text = raw_text
		self.item_level = None
		self.required_player_level = None
		self.crafted = False
		self.resistances = []
		self.factions = []
		self.required_status = 0
		self.slots = []
		self.available = False

	def __str__(self):
		return (f"Name: {self.name}\n"
				f"Item Level: {self.item_level}\n"
				f"Required Player Level: {self.required_player_level}\n"
				f"Crafted: {self.crafted}\n"
				f"Resistances: {', '.join(f'{r[0]}% {r[1]}' for r in self.resistances)}\n"
				f"Factions: {', '.join(self.factions)}\n"
				f"Required Status: {self.required_status}\n"
				f"Slots: {', '.join(self.slots)}\n"
				f"Available: {self.available}\n")

	def process_line(self, line):
		if "Item Level: " in line:
			self.item_level = int(line.split("Item Level: ")[1])
		
		if "Required Player Level: " in line:
			self.required_player_level = int(line.split("Required Player Level: ")[1])
		
		if f"Blueprint: {self.name}" in line:
			self.crafted = True

	def extract_resistances_and_factions(self):
		# Ensure extraction only takes place for effects on the player without skills being involved
		splitters = ["Granted Skills", "Bonus to All Pets"]
		text = self.raw_text
		for splitter in splitters:
			text = self.raw_text.split(splitter)[0]
		
		resistance_pattern = r"(\d+\.?\d*)%\s+([A-Z][a-z]+(?:\s+&+\s+[A-Z][a-z]+)?) Resistance"
		faction_pattern = r"Faction:\s+(.*?)\n"

		self.resistances = re.findall(resistance_pattern, text)
		self.factions = re.findall(faction_pattern, text)

	def set_required_status(self):
		status = 0
		# This is all just from going around to the various vendors and marking down their required player level & tier
		# Honestly a bad practice but I have no other ideas and this seems to be somehow consistant throughout the game
		match self.item_level:
			case 1:
				status = 1
			case 40:
				status = 3
			case 50:
				status = 4
			case 65:
				status = 3
			case 70:
				status = 4
			case 90:
				status = 4
		
		self.required_status = status

	def add_slot(self, slot):
		if slot == "all armor":
			self.slots.extend(["Head", "Body", "Leg", "Shoulder", "Arm", "Feet", "Belt"])
		elif slot in ["head", "head armor"]:
			self.slots.append("Head")
		elif slot in ["chest", "chest armor"]:
			self.slots.append("Body")
		elif slot in ["leg", "leg armor"]:
			self.slots.append("Leg")
		elif slot in ["shoulder", "shoulder armor"]:
			self.slots.append("Shoulder")
		elif slot in ["hand", "hand armor"]:
			self.slots.append("Arm")
		elif slot == "boots":
			self.slots.append("Feet")
		elif slot == "rings":
			self.slots.append("Ring")
		elif slot == "amulets":
			self.slots.append("Amulet")
		elif slot == "medals":
			self.slots.append("Medal")

	def is_valid(self):
		return len(self.slots) > 0 and len(self.resistances) > 0
	
	def check_availability(self, player_stats):
		if self.name in unavailable:
			return False
		
		if self.required_player_level > player_stats["player_level"]:
			return False
		
		if self.crafted and player_stats["crafts"] == 1:
			return True
		
		for faction in self.factions:
			faction_key = faction.lower().replace(" ", "_").replace("'", "")
			if faction_key in player_stats:
				if self.required_status <= player_stats[faction_key]:
					return True
		
		if len(self.factions) == 0:
			return True
		
		return False


class AddonParser:
	def __init__(self, filename):
		self.filename = filename
		self.addons = []
		self.player_stats = None

	def print_all_addons(self):
		for i, addon in enumerate(self.addons, 1):
			print(f"Addon {i}:")
			print(str(addon))
			print("-" * 50)  

	def parse(self):
		content = self.read_file()
		content = self.remove_expansion_names(content)
		lines = self.split_into_lines(content)
		self.process_lines(lines)

	def read_file(self):
		with open(self.filename, "r") as file:
			return file.read()

	def remove_expansion_names(self, content):
		expansion_names = ["Forgotten Gods", "Ashes of Malmouth"]
		for name in expansion_names:
			content = content.replace(name, "")
		return content

	def split_into_lines(self, content):
		lines = [line.strip() for line in content.split("\n") if line.strip()]
		return [line for line in lines if line != "MI"]

	def process_lines(self, lines):
		i = 0
		while i < len(lines):
			name = lines[i]
			raw_text = name + "\n"
			end = self.find_end_of_addon(lines, i, name)
			
			for j in range(i + 1, end):
				raw_text += lines[j] + "\n"
			
			addon = Addon(name, raw_text.strip())
			for j in range(i + 1, end):
				addon.process_line(lines[j])
			
			self.addons.append(addon)
			i = end

	def find_end_of_addon(self, lines, start, name):
		end = start + 1
		found = False
		recent = False
		potential_end = 0
		while end < len(lines):
			if lines[end] == name or lines[end] == f"Blueprint: {name}":
				end += 1
				found = True
				break
			if ("Item Level: " in lines[end] or "Faction: " in lines[end]) and (recent or potential_end == 0):
				recent = True
				potential_end = end + 1
			else:
				recent = False
			end += 1

		if not found and potential_end != 0:
			end = potential_end
		
		return end

	def extract_slots(self):
		for addon in self.addons:
			component_pattern = r"\(Used in (.*?)\)\n"
			augment_pattern = r"\(Applied to (.*?)\)\n"

			component_matches = re.search(component_pattern, addon.raw_text)
			augment_matches = re.search(augment_pattern, addon.raw_text)

			matches = component_matches if component_matches else augment_matches
			
			if matches:
				items_string = matches.group(1)
				items = re.split(r",\s*|\s+and\s+", items_string)
				for item in items:
					addon.add_slot(item.strip())

	def process_addons(self):
		for addon in self.addons:
			addon.extract_resistances_and_factions()
			addon.set_required_status()

		self.addons = [addon for addon in self.addons if addon.is_valid()]

	def set_player_stats(self, stats):
		self.player_stats = stats

	def check_addon_availability(self):
		if self.player_stats is None:
			raise ValueError("Player stats have not been set. Call set_player_stats() first.")
		
		for addon in self.addons:
			addon.available = addon.check_availability(self.player_stats)

class StatsReader:
	@staticmethod
	def read_stats(filename):
		with open(filename, "r") as file:
			reader = csv.DictReader(file)
			stats = next(reader)
		
		for key, value in stats.items():
			stats[key] = int(value)
		
		return stats

def main():
	parser = AddonParser("components_raw.txt")
	parser.parse()
	parser.extract_slots()
	parser.process_addons()

	stats = StatsReader.read_stats("stats.csv")
	parser.set_player_stats(stats)
	parser.check_addon_availability()

	parser.print_all_addons()


if __name__ == "__main__":
	main()