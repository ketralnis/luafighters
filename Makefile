all:
	echo no default task
	false

INSTALLEDJS=node_modules/installed

installjs: ${INSTALLEDJS}

${INSTALLEDJS}: package.json
	# uses package.json to get everything
	npm install
	# mark that we've installed it
	touch ${INSTALLEDJS}

watchjs: ${INSTALLEDJS}
	exec node_modules/.bin/watchify -d -v -t [ reactify --es6 ] \
		luafighters/static/main.jsx -o luafighters/static/compiled.js

releasejs: ${INSTALLEDJS}
	rm -f luafighters/static/compiled.js.map
	node_modules/.bin/browserify --debug \
		-t [ reactify --es6 ] \
		-g [ uglifyify -c ] luafighters/static/main.jsx | \
		node_modules/.bin/exorcist luafighters/static/compiled.js.map \
		> luafighters/static/compiled.js

test tests:
	python -m luafighters.tests.tests

clean:
	rm -f luafighters/static/compiled.js
	rm -f luafighters/static/compiled.js.map
	find luafighters -type f -name \*.pyc -delete -print

distclean: clean
	rm -rf build # only to deal with old style installs
	rm -fr node_modules
	rm -fr cover
	rm -fr luafighters.egg-info

asciiplayer:
	python -m luafighters.asciiplayer

redisplayer:
	python -m luafighters.redisplayer

devserver:
	exec python -m luafighters.server --debug --logging=debug

dev: ${INSTALLEDJS}
	./multiproc.py \
		-- make devserver \
		-- make watchjs
	# open http://`hostname`:5000
