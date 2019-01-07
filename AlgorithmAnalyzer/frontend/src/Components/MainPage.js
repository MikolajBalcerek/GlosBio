import React, { Component } from "react";
import Recorder from "./Nagrywaj";
import Przeglad from "./Przeglad";
import Trenuj from "./Trenuj";
import Train from "./Train";
import RecordTester from "./RecordTester";
import Testuj2 from "./Testuj2";
import axios from 'axios';
import MiddleBar from './MiddleBar'

class MainPage extends Component {
	state = {
		value: 1,
		userList: [],
		algorithmList: []
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
	handleChange4 = ()=> {
		this.setState({ value: 4 });
	};
	handleChange5 = ()=> {
		this.setState({ value: 5 });
	};
	componentDidMount () {
		this.getUsers();
		this.getAlgorithms()
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
    getAlgorithms = () => {
    	var self = this;
        axios
            .get('http://localhost:5000/algorithms')
            .then(function(response) {
				let algorithmsList = []
                response.data.algorithms.map(alg => {
                    algorithmsList.push(alg)
				})
				self.setState({
					algorithmList: algorithmsList
				})
            })
            .catch(function(error) {
                console.log(error);
			})
    }

	render() {
		const { value } = this.state;
		console.log(value)
		return (
			<div>
				<MiddleBar
					value={value}
					handleChange1={this.handleChange1}
					handleChange2={this.handleChange2}
					handleChange3={this.handleChange3}
					handleChange4={this.handleChange4}
					handleChange5={this.handleChange5}
					getUsers={this.getUsers}
					getAlgorithms={this.getAlgorithms}
				/>
				{value === 1 && <Recorder getUsers={()=>this.getUsers()} />}
				{value === 2 && <Przeglad userlist={this.state.userList} />}
				{value === 3 && <Train algorithmList={this.state.algorithmList} />}
				{value === 4 && <RecordTester userList={this.state.userList} algorithmList={this.state.algorithmList}/>}
			</div>
		);
	}
}

export default MainPage;
