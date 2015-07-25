all:
	echo no default task
	false

INSTALLEDJS=node_modules/installed

installjs: ${INSTALLEDJS}

build_python:
	rm -rf build
	python ./setup.py build

${INSTALLEDJS}: package.json
	# uses package.json to get everything
	npm install
	# mark that we've installed it
	touch ${INSTALLEDJS}

watchjs: ${INSTALLEDJS}
	node_modules/.bin/watchify -d -v -t [ reactify --es6 ] \
		luafighters/static/main.jsx -o build/lib.macosx-10.4-x86_64-2.7/luafighters/static/compiled.js

releasejs: ${INSTALLEDJS}
	rm -f luafighters/static/compiled.js.map
	node_modules/.bin/browserify --debug \
		-t [ reactify --es6 ] \
		-g [ uglifyify -c ] luafighters/static/main.jsx | \
		node_modules/.bin/exorcist luafighters/static/compiled.js.map \
		> luafighters/static/compiled.js

test tests: build_python
	cd .. && PYTHONPATH=./luafighters/build/lib.macosx-10.4-x86_64-2.7 \
		python -m luafighters.tests.tests

clean:
	rm -f luafighters/static/compiled.js
	rm -f luafighters/static/compiled.js.map
	rm -rf build

distclean: clean
	rm -fr node_modules
	rm -fr cover
	find . -type f -name \*.pyc -delete -print

asciiplayer: build_python
	cd .. && PYTHONPATH=./luafighters/build/lib.macosx-10.4-x86_64-2.7 \
		python -m luafighters.asciiplayer

redisplayer: build_python
	cd .. && PYTHONPATH=./luafighters/build/lib.macosx-10.4-x86_64-2.7 \
		python -m luafighters.redisplayer

server: build_python ${INSTALLEDJS}
	make releasejs
	cd .. && PYTHONPATH=./luafighters/build/lib.macosx-10.4-x86_64-2.7 exec python -m luafighters.server

dev:
	open http://`hostname`:5000
	exec make server
