import React from 'react';
import axios from 'axios';


export default class UserList extends React.Component {
    state = {
        users: []
    }

    componentDidMount() {
        axios.get(`http://127.0.0.1:5000/api/users/`)
            .then(res => {
                const users = res.data;
                this.setState({users})
            })
    }

    render() {
        return (
            <div>
                {this.state.users.map(user => (
                    <p key={user.id}>User ID: {user.id} | Username: {user.username}</p>
                ))}
            </div>
        )
    }
}