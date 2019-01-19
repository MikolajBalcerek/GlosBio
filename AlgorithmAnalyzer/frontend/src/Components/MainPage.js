import React, { Component } from "react";
import Recorder from "./Nagrywaj";
import Przeglad from "./Przeglad";
import Trenuj from "./Trenuj";
import Train from "./Train";
import RecordTester from "./RecordTester";
import Testuj2 from "./Testuj2";
import axios from 'axios';
import MiddleBar from './MiddleBar'
import { SnackbarProvider } from 'notistack';
import api_config from '../api_config.json'

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
            .get(api_config.usePath+'/users',{} ,{ 'Authorization': api_config.apiKey })
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
            .get(api_config.usePath + '/algorithms')
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
				{value === 1 &&
					<SnackbarProvider maxSnack={20}>
						<Recorder getUsers={()=>this.getUsers()} />
					</SnackbarProvider>}
				{value === 2 &&
					<SnackbarProvider maxSnack={20}>
						<Przeglad userList={this.state.userList} />
					</SnackbarProvider>}
				{value === 3 && <Train algorithmList={this.state.algorithmList} />}
				{value === 4 && <RecordTester userList={this.state.userList} algorithmList={this.state.algorithmList}/>}
				{value === 5 && <Testuj2 />}
			</div>
		);
	}
}

export default MainPage;
