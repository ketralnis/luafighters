<%! import simplejson as json %>
<!doctype html>
<html>
    <head>
        <title>Lua Fighters</title>

        <link rel="stylesheet" href="${url_for('static', filename='style.css')}" />

    </head>
    <body>
        <!--<h1>Welcome to Lua Fighters!</h1>-->

        <div id="game_board">
            <h2>Loading</h2>
        </div>

        <h3>What is this?</h3>
        <p>

            Lua Fighters is a game played by robots. Players design their
            strategies in the <a href="http://www.lua.org/">Lua</a> programming
            language and duke it out.
        </p>
        <h4>The rules of the game</h4>
        <ul>
            <li>The game board consists in a grid containing cells</li>
            <li>Cells may contain ships belonging to one or more players</li>
            <li>Cells may also contain a planet, which has an owner and a size</li>
            <li>Every tick, planets produce ships for their owner in relation to their size</li>
            <li>Every tick that ships are in the same cell as enemy ships, half of each army does battle, destroying some of each army in relation to their sizes</li>
            <li>A player is eliminated when they own no planets</li>
            <li>The game is won when no opponents remain</li>
        </ul>

        ## core JavaScript placed at the end of the document so the pages load
        ## faster
        <script src="${url_for('static', filename='compiled.js')}"></script>

        <script>
            $(function() {
                configure(${json.dumps(config)|n});
                start(document.getElementById('game_board'));
            });
        </script>

    </body>
</html>
