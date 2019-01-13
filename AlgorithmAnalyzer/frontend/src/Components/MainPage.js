import React, { Component } from "react";
import Recorder from "./Nagrywaj";
import Przeglad from "./Przeglad";
import Statystyki from "./Statystyki";
import Trenuj from "./Trenuj";
import Testuj1 from "./Testuj1";
import Testuj2 from "./Testuj2";
import axios from 'axios';
import MiddleBar from './MiddleBar'
import { SnackbarProvider } from 'notistack';
import labels from '../labels.json'

class MainPage extends Component {
	state = {
		value: 1,
		userList: [],
		tagNameList: []
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
	componentDidMount () {
		this.getUsers()
		this.getTagList()
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
            .get(labels.usePath+'/users',{} ,{ 'Authorization': labels.apiKey })
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

	getTagList() {
        var self = this
        axios
            .get(labels.usePath +`/tag`, {}, { 'Authorization': labels.apiKey })
            .then(function(response) {
				self.setState({
                    tagNameList: response.data
                })
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
					handleChange4={this.handleChange4}
					getUsers={this.getUsers}
				/>
				{value === 1 && 
					<SnackbarProvider maxSnack={20}>
						<Recorder getUsers={()=>this.getUsers()} />
					</SnackbarProvider>}
				{value === 2 && 
					<SnackbarProvider maxSnack={20}>
						<Przeglad 
							userList={this.state.userList} 
							tagNameList={this.state.tagNameList}
							getTagList={()=>this.getTagList()}
							/>
					</SnackbarProvider>}
				{value === 3 && 
					<SnackbarProvider maxSnack={20}>
						<Statystyki 
							userList={this.state.userList} 
							tagNameList={this.state.tagNameList}
							/>
					</SnackbarProvider>}
				{value === 4 && <Trenuj />}
				{value === 5 && <Testuj1 />}
				{value === 6 && <Testuj2 />}
			</div>
		);
	}
}

export default MainPage;
