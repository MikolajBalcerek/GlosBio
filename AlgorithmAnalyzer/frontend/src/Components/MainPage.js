import React, { Component } from "react";
import Recorder from "./Nagrywaj";
import Przeglad from "./Przeglad";
import Statystyki from "./Statystyki";
import Train from "./Train";
import RecordTester from "./RecordTester";
import axios from 'axios';
import MiddleBar from './MiddleBar'
import { SnackbarProvider } from 'notistack';
import api_config from '../api_config.json'

class MainPage extends Component {
	state = {
		value: 1,
		userList: [],
		tagNameList: [],
		algorithmList: [],
		userSoundsTrainCount: [],
		userSoundsTestCount: [],
		tagCount: []
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
		this.getUsers()
		this.getTagList()
		this.getAlgorithms()
	}

	setData (array)  {
		this.setState({
			userList: array
		})
	}

	getUsers = () => {
        var self = this
        axios
            .get(api_config.usePath+'/users',{} ,{ 'Authorization': api_config.apiKey })
            .then(function(response) {
				let userLetList = []
				let userTrainSounds = []
				let userTestSounds = []
                response.data.users.map((user, id) => {
					userLetList.push(user)
					userTrainSounds.push({id: id, name: user, value: 0})
					userTestSounds.push({id: id, name: user, value: 0})
					self.getAllUserSounds(user, 'test')
					self.getAllUserSounds(user, 'train')
					self.getUserTags(user)
				})
				self.setState({
					userList: userLetList,
					userSoundsTrainCount: userTrainSounds,
					userSoundsTestCount: userTestSounds
				})
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
				var tagCount = []
				response.data.map((tag, id)=>{
					tagCount.push({tagName: tag, values: []})
					axios
						.get(labels.usePath +`/tag/${tag}`, {}, { 'Authorization': labels.apiKey })
						.then(function(response) {
							console.log(response.data)
							Array.isArray(response.data)&&response.data.map(t=>
								_.find(tagCount, {tagName: tag}).values.push({id: id, name: t, value: 0})
								)
								self.setState({
									tagCount: tagCount
								})
						}
					)
				})
		})
}

getUserTags(user) {
	var self = this
	axios({
		url: labels.usePath +`/users/${user}/tags`,
		method: 'GET',
		headers: { 'Authorization': labels.apiKey}
	  })
		.then(function(response) {
			console.log('tagi', response.data, typeof response.data)
			response.data !== {} && Object.keys(response.data).map(function(key, index) {
				let values =_.find(self.state.tagCount, {tagName: key}).values
				_.find(values, {name: response.data[key]}).value +=1
				_.find(self.state.tagCount, {tagName: key}).values = values
			  })
		})
		.catch(function(error) {
			console.log(error);
		})
}
handleClickVariant(text, variant){
	// variant could be success, error, warning or info
	this.props.enqueueSnackbar(text, { variant });
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

	getAllUserSounds(user, type) {
        var self = this
        axios
            .get(labels.usePath + `/audio/${type}/${user}`, {}, { 'Authorization': labels.apiKey })
            .then(function(response) {
				var userList = []
				if(type === 'train') { 
					userList = self.state.userSoundsTrainCount
				} else
					userList = self.state.userSoundsTestCount
				_.find(userList, {name: user}).value = response.data.samples.length
				if(type === 'train') {
					self.setState({
						userSoundsTrainCount: userList
					})
				} else {
					self.setState({
						userSoundsTestCount: userList
					})
				}
				
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
							userSoundsTrainCount={this.state.userSoundsTrainCount}
							userSoundsTestCount={this.state.userSoundsTestCount}
							tagCount={this.state.tagCount}
							/>
					</SnackbarProvider>}
				{value === 4 && <Train algorithmList={this.state.algorithmList} />}
				{value === 5 && <RecordTester userList={this.state.userList} algorithmList={this.state.algorithmList}/>}
			</div>
		);
	}
}

export default MainPage;
