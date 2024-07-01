import csv
from addon_parser import AddonParser, StatsReader

class Slot:
	def __init__(self, name, can_use_component, can_use_augment):
		self.name = name
		self.can_use_component = can_use_component
		self.can_use_augment = can_use_augment

class Resistance:
	def __init__(self, name, current, goal):
		self.name = name
		self.current = current
		self.goal = goal

class Addon:
	def __init__(self, type, name, slot_compatibility, resistances, available):
		self.type = type
		self.name = name
		self.slot_compatibility = slot_compatibility
		self.resistances = resistances
		self.available = available

class ResistanceOptimizer:
	def __init__(self, slots_file, resistances_file, components_file, augments_file):
		self.slots = self._read_slots(slots_file)
		self.resistances = self._read_resistances(resistances_file)
		self.addons = self._read_addons(components_file, augments_file)
		self.component_slots = [slot for slot in self.slots if slot.can_use_component]
		self.augment_slots = [slot for slot in self.slots if slot.can_use_augment]
		self.components = [addon for addon in self.addons if addon.type == "Component" and addon.available]
		self.augments = [addon for addon in self.addons if addon.type == "Augment" and addon.available]

	def _read_csv(self, filename):
		with open(filename, "r") as f:
			return list(csv.DictReader(f))

	def _read_slots(self, filename):
		raw_slots = self._read_csv(filename)
		return [Slot(s["Name"], int(s["Component"]) == 0, int(s["Augment"]) == 0) for s in raw_slots]

	def _read_resistances(self, filename):
		raw_resistances = self._read_csv(filename)
		return [Resistance(r["Name"], int(r["Current"]), int(r["Goal"])) for r in raw_resistances]

	def _read_addons(self, components_file, augments_file):
		addons = []
		
		# Read components
		parser = AddonParser(components_file)
		parser.parse()
		parser.extract_slots()
		parser.process_addons()
		stats = StatsReader.read_stats("stats.csv")
		parser.set_player_stats(stats)
		parser.check_addon_availability()

		for component in parser.addons:
			slot_compatibility = {slot.name: 1 if slot.name in component.slots else 0 for slot in self.slots}
			resistances = {r.name: float(res[0]) for r in self.resistances for res in component.resistances if r.name.lower() in res[1].lower()}
			addons.append(Addon("Component", component.name, slot_compatibility, resistances, component.available))

		# Read augments
		parser = AddonParser(augments_file)
		parser.parse()
		parser.extract_slots()
		parser.process_addons()
		parser.set_player_stats(stats)
		parser.check_addon_availability()

		for augment in parser.addons:
			slot_compatibility = {slot.name: 1 if slot.name in augment.slots else 0 for slot in self.slots}
			resistances = {r.name: float(res[0]) for r in self.resistances for res in augment.resistances if r.name.lower() in res[1].lower()}
			addons.append(Addon("Augment", augment.name, slot_compatibility, resistances, augment.available))

		return addons

	def calculate_score(self, addon, current_resistances):
		score = 0
		for resistance in self.resistances:
			goal = resistance.goal - resistance.current
			addon_resistance = addon.resistances.get(resistance.name, 0)  # Default to 0 if resistance not present
			contribution = min(addon_resistance, max(0, goal - current_resistances[resistance.name]))
			score += contribution
		return score


	def find_best_addon(self, available_addons, available_slots, current_resistances):
		best_score = 0
		best_addon = None
		best_slot = None

		for addon in available_addons:
			for slot in available_slots:
				if addon.slot_compatibility[slot.name]:
					score = self.calculate_score(addon, current_resistances)
					if score > best_score:
						best_score = score
						best_addon = addon
						best_slot = slot

		return best_addon, best_slot, best_score

	def goals_met(self, current_resistances):
		return all(current_resistances[r.name] >= r.goal - r.current for r in self.resistances)

	def optimize_resistances(self):
		current_resistances = {r.name: 0 for r in self.resistances}
		used_components = []
		used_augments = []
		available_component_slots = self.component_slots.copy()
		available_augment_slots = self.augment_slots.copy()

		while not self.goals_met(current_resistances):
			best_augment, best_aug_slot, aug_score = self.find_best_addon(self.augments, available_augment_slots, current_resistances)
			
			if aug_score > 0:
				used_augments.append((best_augment, best_aug_slot))
				available_augment_slots.remove(best_aug_slot)
				for res in self.resistances:
					current_resistances[res.name] += best_augment.resistances.get(res.name, 0)
			else:
				best_component, best_comp_slot, comp_score = self.find_best_addon(self.components, available_component_slots, current_resistances)
				
				if comp_score > 0:
					used_components.append((best_component, best_comp_slot))
					available_component_slots.remove(best_comp_slot)
					for res in self.resistances:
						current_resistances[res.name] += best_component.resistances.get(res.name, 0)
				else:
					break # No improvement possible

		return used_components, used_augments, current_resistances

	def print_results(self, used_components, used_augments, final_resistances):
		print("Best combination:")
		for component, slot in used_components:
			print(f"Component for {slot.name}: {component.name}")
		for augment, slot in used_augments:
			print(f"Augment for {slot.name}: {augment.name}")

		print("\nFinal resistances:")
		for resistance in self.resistances:
			value = final_resistances[resistance.name]
			print(f"{resistance.name}: {(value + resistance.current):.0f}/{resistance.goal}")

def main():
	optimizer = ResistanceOptimizer("slots.csv", "resistance.csv", "components_raw.txt", "augments_raw.txt")
	used_components, used_augments, final_resistances = optimizer.optimize_resistances()
	optimizer.print_results(used_components, used_augments, final_resistances)

if __name__ == "__main__":
	main()