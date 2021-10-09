

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

	toIndex = {"age": 3, "labels": 4, "trackers": 5, "seeders": 6, "ratio": 7, "size": 8}

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

	order, labelOrder, trackerOrder = [], [], []
	labelsPairedWithTrackers = {}

	for list_ in groupOrder:

		if "labels" in list_:
			order.append("labels")

			for item in list_[1:]:

				if isinstance(item, tuple) or isinstance(item, list):
					labelsPairedWithTrackers[item[0]] = item[1:]
					labelOrder.append(item[0])
				else:
					labelOrder.append(item)

		elif "trackers" in list_:
			order.append("trackers")
			trackerOrder = list_[1:]
		else:
			order.append("unmatched")

	ordered = {
		"labels": {label: [] for label in labelOrder} if labelOrder else [],
		"trackers": {tracker: [] for tracker in trackerOrder} if trackerOrder else [],
		"unmatched": [],
	}

	labelsOrdered = ordered["labels"]
	trackersOrdered = ordered["trackers"]
	unmatched = ordered["unmatched"]

	for torrentData in torrents:
		label = torrentData[toIndex["labels"]]
		trackers = str(torrentData[toIndex["trackers"]])

		if label in labelsOrdered:

			if label in labelsPairedWithTrackers:

				if [tracker for tracker in labelsPairedWithTrackers[label] if tracker in trackers]:
					labelsOrdered[label].append(torrentData)
					continue

			else:
				labelsOrdered[label].append(torrentData)
				continue

		if trackersOrdered:
			tracker = [tracker for tracker in trackerOrder if tracker in trackers]

			if tracker:
				trackersOrdered[tracker[0]].append(torrentData)
				continue

		unmatched.append(torrentData)

	if labelsOrdered:
		sortList(labelOrder, "labels")

	if trackersOrdered:
		sortList(trackerOrder, "trackers")

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

	for group in order:
		orderedList += ordered[group]
		ordered[group].clear()

	if unmatched:
		orderedList += unmatched

	return orderedList
