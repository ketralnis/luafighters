jQuery = $ = require('jquery');
React = require('react')

React = require('react/addons');
Immutable = require('immutable');
Fynx = require('fynx');
_ = require('lodash');
jQuery = require('jquery');
Bootstrap = require('bootstrap');
Base64 = require('Base64');

// the defaults before we start a game
boardHeight = 50;
boardWidth = 50;

window.$ = jQuery;

lf = window.lf = {}

lf.actions = Fynx.createAsyncActions([
    'startGame',
    'updateGame',
    'finishGame',
])

lf.boardStore = Fynx.createImmutableStore({})

CodeComponent = React.createClass({
    render: function() {
        return <div>code for {this.props.name}</div>;
    }
})

BoardComponent = React.createClass({
    render: function() {
        return <div>board</div>;
    }
})

GameComponent = React.createClass({
    render: function() {
        return (<div>
            <CodeComponent name="red"/>
            <CodeComponent name="blue"/>
            <BoardComponent/>
        </div>);
    }
})

React.render(<GameComponent/>, document.getElementById('game_board'));
