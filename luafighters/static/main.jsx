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

lf.defaultCodeStore = Fynx.createImmutableStore(Immutable.Map({}))

lf.codeStore = Fynx.createImmutableStore(Immutable.Map({
    'red': 'error("put some code here!")',
    'blue': 'error("put some code here!")',
}));

lf.boardStore = Fynx.createImmutableStore(Immutable.Map({
    // the defaults before we start a game
    'height': 10,
    'width': 10,
    'board': {},
}))

lf.diffsStore = Fynx.createImmutableStore(Immutable.List([]))

lf.actions = Fynx.createAsyncActions([
    'startGame',
    'updateGame',
    'gameTick',
])

lf.actions.startGame.listen(() => {
    var body = {};
    body.players = lf.codeStore().toObject();

    // defaults are configured above
    body.height = lf.boardStore().get('height');
    body.width = lf.boardStore().get('width');

    $.ajax({
        'url': '/api/start',
        'method': 'POST',
        'contentType': 'application/json',
        'data': JSON.stringify(body),
        'dataType': 'json',
    }).then((result) => {
        var store = lf.boardStore();

        store = store.set('game_id', result.game_id);
        store = store.set('error', null);
        store = store.set('width', result.width);
        store = store.set('height', result.height);
        store = store.set('board', {});
        store = store.set('turn_count', null); // the last turn we rendered
        store = store.set('fetched_turn_count', null); // how many turns are available
        lf.boardStore(store);

        // empty this out
        lf.diffsStore(Immutable.List([]));

        // start kicking off the game
        lf.actions.updateGame();
    });
});

// TODO: neither updateGame nor gameTick should overwrite the current game if we
// start another one after they start

lf.actions.updateGame.listen(() => {
    var body = {}
    body.game_id = lf.boardStore().get('game_id');
    body.last_offset = lf.boardStore().get('fetched_turn_count');

    $.ajax({
        'url': '/api/status',
        'method': 'POST',
        'contentType': 'application/json',
        'data': JSON.stringify(body),
        'dataType': 'json',
    }).then((result) => {
        var boardStore = lf.boardStore();
        var previous_turn_count = boardStore.get('turn_count')
        var previous_fetched_turn_count = boardStore.get('fetched_turn_count')
        var state = result.state;
        var diffs = result.diffs;

        // add these diffs into the list
        var diffsStore = lf.diffsStore()
        diffsStore = diffsStore.concat(diffs)
        lf.diffsStore(diffsStore);

        if(state.error) {
            boardStore = boardStore.set('error', state.error)
            return
        }

        console.log("Downloaded turns "+previous_fetched_turn_count+".."+state.turn_count)
        boardStore = boardStore.set('fetched_turn_count', state.turn_count);

        lf.boardStore(boardStore);

        if(!(state.done || state.error)) {
            // if we're not done, do it again until we have all of the diffs
            lf.actions.updateGame();
        }

        if(!previous_turn_count || previous_turn_count>=previous_fetched_turn_count) {
            // we need to start processing game ticks if (1) we haven't
            // processed any before or (2) the old ticker game up because it ran
            // out of turns to process
            lf.actions.gameTick();
        }
    });
});

lf.actions.gameTick.listen(() => {
    var boardStore = lf.boardStore();

    // how many turns we've downloaded
    var fetched_turn_count = boardStore.get('fetched_turn_count');

    // how many turns we've played
    var turn_count = boardStore.get('turn_count');

    console.log("Executing turn #" + turn_count + " of "+ fetched_turn_count
                +"("+lf.diffsStore().size+")");

    if(!fetched_turn_count || turn_count == fetched_turn_count) {
        // there's no more game available to play
        console.log("Stopping ticks at "+turn_count+"/"+fetched_turn_count)
        return
    }

    var new_board;

    if(turn_count == null) {
        new_board = lf.diffsStore().get(0);
        turn_count = 0;
    } else {
        var board = boardStore.get('board');
        var diff = lf.diffsStore().get(turn_count+1);
        new_board = deep_extend(board, diff);

        turn_count += 1
    }

    console.log(new_board);

    boardStore = boardStore.set('board', new_board);
    boardStore = boardStore.set('turn_count', turn_count);

    lf.boardStore(boardStore);

    setTimeout(lf.actions.gameTick, 0.25*1000);
    return;
})

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

            <textarea rows="30" style={{width: '100%'}}
             onChange={this.onChangeCode}
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
            <table className="game-table" border="1" width="100%"><tbody>
                <tr>
                    <td width="25%">
                        <CodeComponent player="red"/>
                    </td>
                    <td width="75%" rowSpan="2">
                        <BoardComponent/>
                    </td>
                </tr>
                <tr>
                    <td width="25%">
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

        if(cell.ships) {
            return (<td className="cell">
                {planet_str}
                {ship_list}
            </td>);
        } else {
            return <td className="cell">{planet_str}</td>
        }
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
        var board = boardStore.get('board').board
        var height = boardStore.get('height');
        var width = boardStore.get('width');
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

        var errorText = '';
        if(boardStore.get('error')) {
            errorText = (<div style="board-error">
                {boardStore.get('error')}
            </div>);
        }

        var turn_text = '';
        console.log(board)
        if(board && board.turn) {
            turn_text = <span className="board-turn" style={{color: board.turn}}>
                {board.turn+"'s turn"} #{board.turn_count}
            </span>
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
