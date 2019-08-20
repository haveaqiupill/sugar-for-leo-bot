task:
	git add main.py
	git commit -m "test main.py"
	git push --force heroku master
	heroku logs --tail

database:
	git add dbhelper.py
	git commit -m "test dbhelper.py"
	git push --force heroku master
	heroku logs --tail

