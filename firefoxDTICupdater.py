import re, sqlite3, os, time, shutil 
# This script transforms old DTIC pdf links to new DTIC pdf links
# Previously links where like https://apps.dtic.mil/dtic/tr/fulltext/u2/325385.pdf
# Now they have to be like https://apps.dtic.mil/sti/pdfs/AD0325385.pdf
# This script converts all the links that you input and returns a format compatible with firefox so your DTIC bookmarks are back in order

# ********* IF YOU WANT TO USE THIS SCRIPT MODIFY THE firefoxBookmarkDB VARIABLE ********* # 
# Here goes your firefox places.sqlite file, it is usually located in %APPDATA%\Mozilla\Firefox\Profiles\*user*\places.sqlite
# Leave de r and the quotes in place...
firefoxPlaces = r'C:\Users\USR\AppData\Roaming\Mozilla\Firefox\Profiles\49fkp5mq.default-release\places.sqlite'
# USE AT YOUR OWN RISK AS THIS SCRIPT MIGHT ABSOLUTELY MESS WITH YOUR BOOKMARKS, BACKUP IS RECOMMENDED 
# (SCRIPT AUTOMATICALLY DOES A BACKUP IN CASE into places.sqlite.old)

# FIREFOX MUST BE CLOSED

# First we need a function that will transform the article ID's to the new format
def transformIdWithOnlyNumbers(articleID):
	''' Transforms DTIC old article id's that only contain numbers into proper new article ID's
	args: articleID as string
	returns: articleID string
	'''
	# We have to add 0's if id is smaller than 6
	# We also have to add AD as a prefix
	TOTAL_ID_LENGTH = 7
	if len(articleID) < TOTAL_ID_LENGTH:
		numberOfZeros = "0" * (TOTAL_ID_LENGTH - len(articleID))
		articleID = f"AD{numberOfZeros}{articleID}"
	else:
		articleID = f"AD{articleID}"
	return articleID

# REGEXES that we will use
# This regex matches the last slash until it finds a dot to get article id so: https://apps.dtic.mil/dtic/tr/fulltext/u2/***325385***.pdf
regexToGetLastSlash = re.compile(r'([^\/]+)(?=\.\w+$)')
# This regex checks if string is all numbers
regexIsAllNumbers = re.compile(r'^\d+$')

# We use an existing link as model to substitute the last part of the URL with the new ID
newLinkModel = r"https://apps.dtic.mil/sti/pdfs/AD0325385.pdf"

# Before messing with the places.sqlite file we will make a backup of the file called places.sqlite.old
shutil.copy(firefoxPlaces, os.path.join(os.path.dirname(firefoxPlaces),"places.sqlite.old"))

# We connect to the firefox bookmarks which is a database file, in this case it is MY system path, modify with yours
firefoxBookmarkDB = sqlite3.connect(firefoxPlaces)
firefoxBookmarkDBcursor = firefoxBookmarkDB.cursor()
DTICUrlQuery = ("select moz_places.url,moz_places.id from moz_bookmarks, moz_places where moz_bookmarks.fk = moz_places.id and moz_places.url LIKE \"%dtic%\"")
firefoxBookmarkDBcursor.execute(DTICUrlQuery)
DTICLinkList = firefoxBookmarkDBcursor.fetchall()
for entry in DTICLinkList:
	# Now onto the conversion which depends on the type of ID...
	# We extract the ID into a string using re.search, the match object is saved as a string directly calling .group method
	try:
		# We need the ID for the DB update later
		keyID = entry[1]
		url = entry[0]
		articleID = re.search(regexToGetLastSlash, url).group()	
	except:
		continue
	# We need the article keyID for the UPDATE query later
	# Now depending on the type of Article ID extracted we have to call a different method
	# If the Article ID is only made numbers, we transform
	if re.match(regexIsAllNumbers, articleID):
		articleID = transformIdWithOnlyNumbers(articleID)
	# Else, the ID will work so there is no need to transform	
	# We will substitute the Article ID in the model link for the new one we just build with re.sub, so we now have a working link
	newLink = re.sub(regexToGetLastSlash, articleID, newLinkModel)
	# Update Firefox places file 
	firefoxBookmarkDBcursor.execute(f"UPDATE moz_places SET url = \'{newLink}\' WHERE moz_places.id = {keyID}")
	firefoxBookmarkDB.commit()
print("Update complete....")
print(f"If something is wrong, please rename places.sqlite.old to places.sqlite in {os.path.dirname(firefoxPlaces)}")
time.sleep(10)