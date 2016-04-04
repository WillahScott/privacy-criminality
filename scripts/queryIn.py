#!/usr/bin/python 2.7.5

##  - LinkedIn Scraper -
## Brief version (Oct 2015)


from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


search_query = 'https://www.linkedin.com/pub/dir/?first={f}&last={l}&search=Search'


'''
Compares to company names
@return: Tuple: (match, matched string)
'''
def word_comp(comp1, comp2):
    # Common terms not to be considered matches
    common_terms = ['inc', 'inc.', 'corporation', 'corp', 'co', 'systems', 'fund', 'ltd']
    
    # Get lowercase separate words
    words1 = [ w for w in term1.lower().split() if w not in common_terms and len(w) > 1 ]
    words2 = [ w for w in term2.lower().split() if w not in common_terms and len(w) > 1 ]

    # sort words from biggest to smalles so as to get greatest match
    words1.sort(key = lambda s: len(s), reverse=True)
    words2.sort(key = lambda s: len(s), reverse=True)

    for w in words1:
        if any(map(lambda x: w in x, words2)):
            return (True, w)
    
    for w in words2:
        if any(map(lambda x: w in x, words1)):
            return (True, w)
    
    return (False, '')


'''
Checks for a match when obtained just a single result
@return: Tuple: (match, matched_token, 'current' or 'past')
'''
def match_company(_current, _past, company):

	# Parse commas
	current = re.sub(',', ' ', _current)
	past = re.sub(',', ' ', _past)

	_inCurrent = word_comp(company, current)

	if _inCurrent[0]:
		return (True, _inCurrent[1], 'current')
	else:
		_inPast = word_comp(company, past)
		if _inPast[0]:
			return (True, _inPast[1], 'past')

	return (False, '', '')


'''
Extract information from public profile (only one result)
@return: expanded entry dictionary
'''
def parse_public_prof(vcard, entry):

	overview = vcard.find_element_by_class_name("profile-photo")

	_entry['URL'] = overview.get_attribute("href")
	_entry['Title'] = overview.get_attribute("title")

	# Basic Info : location & industry
	basic = vcard.find_element_by_class_name("vcard-basic")

	try:
		_entry['Location'] = basic.find_element_by_class_name("location").text
	except NoSuchElementException:
		_entry['Location'] = "N/A"

	try:
		_entry['Industry'] = basic.find_element_by_class_name("industry").text
	except NoSuchElementException:
		_entry['Industry'] = "N/A"

	# Expanded Info : education
	expanded = vcard.find_element_by_class_name("vcard-expanded")
	try:
		_entry['Education'] = expanded.find_element_by_class_name("education-content").text
	except NoSuchElementException:
		_entry['Education'] = "N/A"

	return entry


'''
Extract information from public profile (only one result)
@return: expanded entry dictionary
'''
def parse_vcard(vcard, entry):
	entry['URL'] = vcard.find_element_by_xpath('//*[@id="top-card"]/div[2]/div[1]/div[1]/a').get_attribute("href")
	entry['Title'] = vcard.find_element_by_xpath('//*[@id="headline"]/p').text

	try:
		entry['Location'] = vcard.find_element_by_xpath('//*[@id="wrapper"]/div[2]/div[1]/ul/li[1]/div/div/dl/dd[1]').text
	except NoSuchElementException:
		entry['Location'] = "N/A"

	try:
		entry['Industry'] = vcard.find_element_by_xpath('//*[@id="location"]/dl/dd[2]').text
	except NoSuchElementException:
		entry['Industry'] = "N/A"

	try:
		entry['Education'] = vcard.find_element_by_xpath('//*[@id="overview-summary-education"]/td/ol/li/a').text
	except NoSuchElementException:
		entry['Education'] = "N/A"

	return entry


'''
Queries LinkedIn filtering for matching Company in the current or past LinkedIn fields.
 - Only parses further information for matches.
@return: list of matching entry dictionaries.
'''
def match_query(browser, search_first, search_last, company):

	# Search LinkedIn
	browser.get(search_query.format(f=search_first, l=search_last))

	# List results
	hits = browser.find_elements_by_class_name('vcard')
	if len(hits) == 1:
		# Get current and past
		current = hits[0].find_element_by_xpath('//*[@id="overview-summary-current"]/td').text
		past = hits[0].find_element_by_xpath('//*[@id="overview-summary-past"]/td/ol').text

		# Check for match
		_match = match_company(company, current, past)
		if _match[0]:
			_template = {'FirstName':search_first, 'LastName':search_last, 'Match': _match[1], 'MatchOn': _match[2], 'Current': current, 'Past': past}
			matched_obs = parse_public_prof(hits[0], _template)
			return [ matched_obs ] 
	
	elif len(hits) > 1:

		matched_list = []

		for h in hits:

			try:
				current = expanded.find_element_by_class_name("current-content").text
			except NoSuchElementException:
				current = "N/A"

			try:
				past = expanded.find_element_by_class_name("past-content").text
			except NoSuchElementException:
				past = "N/A"

			# Check for match
			_match = match_company(company, current, past)
			if _match[0]:
				_template = {'FirstName':search_first, 'LastName':search_last, 'Match': _match[1], 'MatchOn': _match[2], 'Current': current, 'Past': past}
				matched_obs = parse_vcard(h, _template)
				matched_list.append(matched_obs)

		return matched_list

	return []


