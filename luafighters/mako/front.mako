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

        ## core JavaScript placed at the end of the document so the pages load
        ## faster
        <script src="${url_for('static', filename='compiled.js')}"></script>

    </body>
</html>
