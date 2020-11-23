import React from 'react';
import ReactDOM from 'react-dom';


class App extends React.Component {
    render() {
        return (
            <div>
                <h1>DinoPass - Password Manager</h1>

                <input
                    type="password"
                    required
                    placeholder="Please enter master password"
                />
                <button>Submit</button>
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
