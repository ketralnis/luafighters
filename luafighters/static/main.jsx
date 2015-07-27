// 'use strict';

jQuery = require('jquery');
React = require('react');

React = require('react/addons');
Immutable = require('immutable');
Fynx = require('fynx');
FynxMixins = require("fynx-mixins");
_ = require('lodash');
Bootstrap = require('bootstrap');

window.$ = jQuery;

lf = window.lf = {}

// populated in configure() below
lf.defaultCodeStore = Fynx.createImmutableStore(Immutable.Map({}))

lf.codeStore = Fynx.createImmutableStore(Immutable.Map({
    'red': 'error("put some code here!")',
    'blue': 'error("put some code here!")',
}));

// we request this size from the server, but they may send us back a different
// one
var defaultHeight = 10;
var defaultWidth = 10;

lf.boardStore = Fynx.createImmutableStore(Immutable.Map({
    // the currently known state of the remote game runner, as of when we last
    // retrieved it and the according diffs
    'state': {},

    // the current board as we see it as of the currently displayed turn
    'board': {},

    // how many turns have been played so far (how many diffs have been applied)
    'turn_count': 0,

    // the entire list of diffs to represent the full game play from the
    // beginning of the game to the last-fetched turn_count
    'diffs': Fynx.createImmutableStore(Immutable.List([])),

}))

lf.actions = Fynx.createAsyncActions([
    'startGame',
    'updateGame',
    'gameTick',
])

lf.actions.startGame.listen(() => {
    var body = {};
    body.players = lf.codeStore().toObject();

    // defaults are configured above
    body.height = defaultHeight;
    body.width = defaultWidth;

    $.ajax({
        'url': '/api/start',
        'method': 'POST',
        'contentType': 'application/json',
        'data': JSON.stringify(body),
        'dataType': 'json',
    }).then((result) => {
        var store = lf.boardStore();

        store = store.set('state', result.state);
        store = store.set('board', {}); // empty this out
        store = store.set('turn_count', 0); // no turns played so far
        store = store.set('diffs', Immutable.List([])) // empty this out
        lf.boardStore(store);

        // start kicking off the game
        lf.actions.updateGame(result.state.game_id);
    });
});

function can_proceed(turn_count, out_of) {
    return out_of>0 && turn_count < out_of;
}

lf.actions.updateGame.listen((game_id) => {
    if(game_id != lf.boardStore().get('state').game_id) {
        // we're being asked to update a game that doesn't exist anymore
        console.log("Bailing old game_id ("+game_id+"/"+lf.boardStore().get('state').game_id+")")
        return
    }

    var body = {}
    body.game_id = lf.boardStore().get('state').game_id;
    body.last_offset = lf.boardStore().get('state').turn_count || null;

    console.log("Fetching new turns from "+ body.last_offset)

    $.ajax({
        'url': '/api/status',
        'method': 'POST',
        'contentType': 'application/json',
        'data': JSON.stringify(body),
        'dataType': 'json',
    }).then((result) => {
        if(game_id != lf.boardStore().get('state').game_id) {
            // we're being asked to update a game that doesn't exist anymore
            console.log("Bailing old game_id ("+game_id+"/"+lf.boardStore().get('state').game_id+")")
            return
        }

        var boardStore = lf.boardStore();

        var new_state = result.state;
        boardStore = boardStore.set('state', new_state);

        var received_diffs = result.diffs;
        var old_diffs = boardStore.get('diffs')
        var new_diffs = old_diffs.concat(received_diffs)
        boardStore = boardStore.set('diffs', new_diffs);

        // console.log("Downloaded turns "+previous_turn_count+".."+state.turn_count+"("+new_diffs.size+")")

        lf.boardStore(boardStore)

        if(!(new_state.done || new_state.error)) {
            // if we're not done, do it again until we have all of the diffs
            lf.actions.updateGame(game_id);
        }

        if(!can_proceed(boardStore.get('turn_count'), old_diffs.size)
            && can_proceed(boardStore.get('turn_count'), new_diffs.size)) {
            // we couldn't proceed before, but we can now
            lf.actions.gameTick(game_id);
        }
    });
});

lf.actions.gameTick.listen((game_id) => {
    if(game_id != lf.boardStore().get('state').game_id) {
        // we're being asked to update a game that doesn't exist anymore
        console.log("Bailing old game_id ("+game_id+"/"+lf.boardStore().get('state').game_id+")")
        return
    }

    var boardStore = lf.boardStore();

    // how many turns we've downloaded
    var fetched_turn_count = boardStore.get('diffs').size

    // how many turns we've played
    var turn_count = boardStore.get('turn_count');


    console.log("Executing turn #" + turn_count + " of "+ fetched_turn_count);

    var new_board;

    if(turn_count == 0) {
        new_board = boardStore.get('diffs').get(0);
    } else {
        var board = boardStore.get('board');
        var diff = boardStore.get('diffs').get(turn_count);
        new_board = deep_extend(board, diff);
    }
    var new_turn_count = turn_count+1;

    boardStore = boardStore.set('board', new_board);
    boardStore = boardStore.set('turn_count', new_turn_count);

    lf.boardStore(boardStore);

    if(can_proceed(new_turn_count, boardStore.get('diffs').size)) {
        setTimeout(() => lf.actions.gameTick(game_id), 0.25*1000);
    } else {
        // there's no more game available to play
        console.log("Stopping ticks at "+turn_count+"/"+fetched_turn_count);
        return;
    }
});

CodeComponent = React.createClass({
    mixins: [
        FynxMixins.connect(lf.codeStore, 'codeStore'),
        FynxMixins.connect(lf.defaultCodeStore, 'defaultCodeStore'),
    ],

    render: function() {
        var exampleStrategies = lf.defaultCodeStore();

        return (<div>
            <h2>
                Player: <span style={{color: this.props.player}}>{this.props.player}</span>
            </h2>

            <textarea onChange={this.onChangeCode}
             value={lf.codeStore().get(this.props.player)} />

            Examples: <select onChange={this.onChangeToExample}>
                <option></option>
                {exampleStrategies.map((v,k) => {
                    return <option value={k}>{k}</option>
                })};
            </select>
        </div>);
    },

    onChangeCode: function(event) {
        var codes = lf.codeStore();
        codes = codes.set(this.props.player, event.target.value);
        lf.codeStore(codes);
    },

    onChangeToExample: function(event) {
        var newCode = lf.defaultCodeStore().get(event.target.value);
        if(event.target.value == '') {
            newCode = '';
        }

        var codes = lf.codeStore();
        codes = codes.set(this.props.player, newCode);
        lf.codeStore(codes);
    }
})

GameComponent = React.createClass({
    render: function() {
        return (<div>
            <table className="game-table"><tbody>
                <tr>
                    <td className="game-table-code">
                        <CodeComponent player="red"/>
                    </td>
                    <td className="game-table-board" rowSpan="2">
                        <BoardComponent/>
                    </td>
                </tr>
                <tr>
                    <td>
                        <CodeComponent player="blue"/>
                    </td>
                </tr>
            </tbody></table>
            <button onClick={lf.actions.startGame}>Go!</button>
        </div>);
    }
})

CellComponent = React.createClass({
    render: function() {
        var cell = this.props.cell
        var planet_str = '';

        if(cell.planet) {
            planet_str = (<div className="cell-planet">
                {cell.planet.name}({cell.planet.size}):
                <span style={{color: cell.planet.owner}}>{cell.planet.owner}</span>
            </div>)
        }

        var ship_list = '';
        if(cell.ships) {
            ship_list = (<ul className="cell-ships">
                {_.map(cell.ships, (num, owner) => {
                    return <li className="cell-ships-owner" style={{color: owner}}>{owner}: {num}</li>
                })}
            </ul>)
        }

        return (<td className="cell">
            {planet_str}
            {ship_list}
        </td>);
    }
});

BoardRow = React.createClass({
    render: function() {
        return (<tr className="board-row">
            {_.map(this.props.cells, (cell) => {
                return <CellComponent key={"cell-"+cell.x+","+cell.y} cell={cell} />
            })}
        </tr>);
    }
})

BoardComponent = React.createClass({
    mixins: [FynxMixins.connect(lf.boardStore, 'boardStore')],

    render: function() {
        var boardStore = this.state.boardStore;
        var state = boardStore.get('state')
        var board = boardStore.get('board');
        var height = state && state.height || defaultHeight
        var width = state && state.width || defaultWidth
        var rows = [];

        // turn our sparse dictionary into a list of lists
        for(var y=0; y<height; y++) {
            var row = [];

            for(var x=0; x<width; x++) {
                var cell = {};

                if(board
                   && board['cells']
                   && board['cells'][y]
                   && board['cells'][y][x]) {

                    cell = _.clone(board['cells'][y][x]);
                }

                cell.x = x;
                cell.y = y;

                row.push(cell);
            }

            rows.push(row)
        }

        // TODO
        var errorText = '';
        if(state && state.error) {
            errorText = (<div class="board-error">
                {state.error}
            </div>);
        }

        var turn_text = '';
        if(board && board.victor) {
            turn_text = (<span className="board-victor" style={{color: board.victor}}>
                {board.victor} wins after {board.turn_num} turns
            </span>)
        } else if(board && board.turn) {
            turn_text = (<span className="board-turn" style={{color: board.turn}}>
                {board.turn+"'s turn"} #{board.turn_num}
            </span>)
        }

        return (<div>
            <h2>game: {boardStore.get('game_id')}</h2>
            {errorText}
            <table className="game-board"><tbody>
                {_.map(rows, (row, num)=> <BoardRow cells={row} key={"cell-row"+num} />)}
            </tbody></table>
            <p>{turn_text}</p>
        </div>);
    }
});

function deep_extend(original_data, diff) {
    var key, prop;
    var new_data = {};

    for(key in original_data) {
        new_data[key] = original_data[key];
    }

    for (key in diff) {
        prop = diff[key];
        if(_.isNull(prop)) {
            delete new_data[key];
        } else if(_.isArray(prop)) {
            new_data[key] = _.clone(prop);
        } else if(_.isObject(prop)) {
            if (!(key in original_data)) {
                new_data[key] = {};
            }
            new_data[key] = deep_extend(new_data[key], prop);
        } else {
            new_data[key] = prop;
        }
    }
    return new_data;
}

configure = function(config) {
    lf.defaultCodeStore(config.example_strategies);
}

start = function(game_board) {
    React.render(<GameComponent/>, game_board);
}
