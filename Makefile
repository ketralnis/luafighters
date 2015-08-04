all:
	echo no default task
	false

INSTALLEDJS=node_modules/installed
INSTALLEDENV=.env/installed

installjs: ${INSTALLEDJS}

installenv: ${INSTALLEDENV}

${INSTALLEDENV}: setup.py
	rm -fr .env
	virtualenv .env
	touch .env/installed
	.env/bin/python ./setup.py develop

${INSTALLEDJS}: package.json
	# uses package.json to get everything
	npm install
	# mark that we've installed it
	touch ${INSTALLEDJS}

watchjs: ${INSTALLEDJS}
	node_modules/.bin/watchify -d -v -t [ reactify --es6 ] \
		luafighters/static/main.jsx -o luafighters/static/compiled.js

releasejs: ${INSTALLEDJS}
	rm -f luafighters/static/compiled.js.map
	node_modules/.bin/browserify --debug \
		-t [ reactify --es6 ] \
		-g [ uglifyify -c ] luafighters/static/main.jsx | \
		node_modules/.bin/exorcist luafighters/static/compiled.js.map \
		> luafighters/static/compiled.js

test tests: ${INSTALLEDENV}
	.env/bin/python -m luafighters.tests.tests

clean:
	rm -f luafighters/static/compiled.js
	rm -f luafighters/static/compiled.js.map
	find . -type f -name \*.pyc -delete -print

distclean: clean
	rm -fr .env
	rm -fr node_modules
	rm -fr cover
	find . -type f -name \*.pyc -delete -print

asciiplayer: ${INSTALLEDENV}
	.env/bin/python -m luafighters.asciiplayer

redisplayer: ${INSTALLEDENV}
	.env/bin/python -m luafighters.redisplayer

devserver: ${INSTALLEDENV} ${INSTALLEDJS}
	.env/bin/python -m luafighters.server --debug --logging=debug

dev: ${INSTALLEDENV} ${INSTALLEDJS}
	exec ./multiproc.py \
		-- make devserver \
		-- make watchjs
	# open http://`hostname`:5000
