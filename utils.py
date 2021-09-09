
def convertRules(mode, dic):

	if "include" in mode:

		for ruleName in mode["include"]:
			dic[ruleName] = "include"

	if "exclude" in mode:

		for ruleName in mode["exclude"]:
			dic[ruleName] = "exclude"

	for ruleName, rules in mode.items():

		if ruleName not in ("include", "exclude"):

			if "include" in rules:

				if isinstance(ruleName, tuple):

					for item in ruleName:
						dic[item] = rules

				else:
					dic[ruleName] = rules

				continue

			minAge = rules["age"] if "age" in rules else False
			minRatio = rules["ratio"] if "ratio" in rules else False
			minSeeders = rules["seeders"] if "seeders" in rules else False
			minSize = rules["size"] if "size" in rules else False

			if "fb_mode" in rules and rules["fb_mode"] != 0:
				fbMode = rules["fb_mode"]
				fbAge = rules["fb_age"] if "fb_age" in rules else False
				fbRatio = rules["fb_ratio"] if "fb_ratio" in rules else False
				fbSeeders = rules["fb_seeders"] if "fb_seeders" in rules else False
				fbSize = rules["fb_size"] if "fb_size" in rules else False
			else:
				fbMode = fbAge = fbRatio = fbSeeders = fbSize = False

			if "blacklist" in rules:
				filter_ = "blacklist"
				filterList = rules["blacklist"]
			elif "whitelist" in rules:
				filter_ = "whitelist"
				filterList = rules["whitelist"]
			else:
				filter_ = filterList = False

			if isinstance(ruleName, tuple):

				for item in ruleName:
					dic[item] = (
						minAge,
						minRatio,
						minSeeders,
						minSize,
						fbMode,
						fbAge,
						fbRatio,
						fbSeeders,
						fbSize,
						filter_,
						filterList,
					)

			else:
				dic[ruleName] = (
					minAge,
					minRatio,
					minSeeders,
					minSize,
					fbMode,
					fbAge,
					fbRatio,
					fbSeeders,
					fbSize,
					filter_,
					filterList,
				)


def sortTorrents(sortOrder, groupOrder, torrents):

	def sortList(list_, key):
		ordered[key] = [
			torrentData
			for i in list_
			for torrentData in sorted(
				ordered[key][i],
				key=lambda x: (
					-x[toIndex[sortOrder[0]]],
					-x[toIndex[sortOrder[1]]],
					-x[toIndex[sortOrder[2]]],
					-x[toIndex[sortOrder[3]]],
				),
			)
		]

	toIndex = {"age": 3, "ratio": 7, "seeders": 6, "size": 8}

	while len(sortOrder) < 4:
		sortOrder.append(sortOrder[-1])

	if not groupOrder:
		return sorted(
			torrents,
			key=lambda x: (
				-x[toIndex[sortOrder[0]]],
				-x[toIndex[sortOrder[1]]],
				-x[toIndex[sortOrder[2]]],
				-x[toIndex[sortOrder[3]]],
			),
		)

	labelOrder = trackerOrder = False
	order = []

	for list_ in groupOrder:

		if "label" in list_:
			order.append("label")
			labelOrder = list_[1:]
		elif "tracker" in list_:
			order.append("tracker")
			trackerOrder = list_[1:]
		else:
			order.append("unmatched")

	ordered = {
		"label": {label: [] for label in labelOrder} if labelOrder else [],
		"tracker": {tracker: [] for tracker in trackerOrder} if trackerOrder else [],
		"unmatched": [],
	}

	labelsOrdered = ordered["label"]
	trackersOrdered = ordered["tracker"]
	unmatched = ordered["unmatched"]

	for torrentData in torrents:
		label = torrentData[3]
		trackers = str(torrentData[4])

		if label in labelsOrdered:
			labelsOrdered[label].append(torrentData)
			continue

		if trackersOrdered:
			tracker = [tracker for tracker in trackerOrder if tracker in trackers]

			if tracker:
				trackersOrdered[tracker[0]].append(torrentData)
				continue

		unmatched.append(torrentData)

	if labelsOrdered:
		sortList(labelOrder, "label")

	if trackersOrdered:
		sortList(trackerOrder, "tracker")

	if unmatched:
		unmatched.sort(
			key=lambda x: (
				-x[toIndex[sortOrder[0]]],
				-x[toIndex[sortOrder[1]]],
				-x[toIndex[sortOrder[2]]],
				-x[toIndex[sortOrder[3]]],
			)
		)

	orderedList = []

	for element in order:
		orderedList += ordered[element]
		ordered[element].clear()

	if unmatched:
		orderedList += unmatched

	return orderedList
