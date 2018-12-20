import React, { Component } from "react";
import Recorder from "./Nagrywaj";
import Przeglad from "./Przeglad";
import Trenuj from "./Trenuj";
import Testuj1 from "./Testuj1";
import Testuj2 from "./Testuj2";
import axios from 'axios';
import MiddleBar from './MiddleBar'

class MainPage extends Component {
	state = {
		value: 1,
		userList: []
	};

	handleChange1 = ()=> {
		this.setState({ value: 1 });
	};
	handleChange2 = ()=> {
		this.setState({ value: 2 });
	};
	handleChange3 = ()=> {
		this.setState({ value: 3 });
	};
	componentDidMount () {
		this.getUsers()
	}
	setData (array)  {
		this.setState({
			userList: array
		})
	}
	getUsers = () => {
		console.log('działam')
        var self = this
        axios
            .get('http://localhost:5000/users')
            .then(function(response) {
				let userLetList = []
                response.data.users.map(user => {
                    userLetList.push(user)
				})
				self.setData(userLetList)
            })
            .catch(function(error) {
                console.log(error);
			})
    }
	
	render() {
		const { value } = this.state;
		return (
			<div>
				<MiddleBar 
					value={value}
					handleChange1={this.handleChange1}
					handleChange2={this.handleChange2}
					handleChange3={this.handleChange3}
					getUsers={this.getUsers}
				/>
				{value === 1 && <Recorder getUsers={()=>this.getUsers()} />}
				{value === 2 && <Przeglad userlist={this.state.userList} />}
				{value === 3 && <Trenuj />}
				{value === 4 && <Testuj1 />}
				{value === 5 && <Testuj2 />}
			</div>
		);
	}
}

export default MainPage;
