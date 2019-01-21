import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import PropTypes from 'prop-types';
import axios from 'axios';
import { withSnackbar } from 'notistack'
import MFCC from './MFCC'
import Tags from './Tags'
import api_config from '../api_config.json'
import UserPrzeglad from './UserPrzeglad' 
import Fade from '@material-ui/core/Fade';
import UserPrzegladComponent from './UserPrzegladComponent';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import TagPrzeglad from './TagPrzeglad'
import TagPrzegladComponent from './TagPrzegladComponent'
import DeleteUser from './DeleteUser'

class Przeglad extends Component { 
    constructor(props) {
        super(props);
        this.state = {
            isPlay: false,
            user: '',
            name: 'hai',
            userSounds: [],
            type: 'train',
            sound: '',
            url: '',
            mfcc: null,
            mfccOpen: false,
            userTags: [],
            tagsOpen: false,
            value: 0,
            userValue: 0,
            userTagCount:[],
            tagValue: null,
            tabPrzeglad: 0,
            tag: '',
            tagValuesList: [],
            tagValues: [],
            deleteOpen: false
        }
    }
    handleOpenDelete = () =>{
        this.setState({
            deleteOpen: !this.state.deleteOpen
        })
    }
    handleChangeName = event => {
        this.setState({ [event.target.name]: event.target.value }, ()=>this.getUserTagValues());
      };

      handleChangeTagValue = event => {
        this.setState({ [event.target.name]: event.target.value });
      };

    getUserTagValues(){
        var self = this
        axios
            .get(api_config.usePath +`/tag/${this.props.tagNameList[this.state.name]}`, {}, { 'Authorization': api_config.apiKey })
            .then(function(response) {
                console.log(response.data)
				self.setState({
                    tagValuesList: response.data
                })
            })
            .catch(function(error) {
                console.log(error);
			})
    }

    addTagToUser(){
        var self = this
        let fd = new FormData();
        fd.append("name", this.props.tagNameList[this.state.name]);
        fd.append("value", this.state.tagValuesList[this.state.tagValue]);
        axios
            .post(api_config.usePath +`/users/${this.props.userList[this.state.user]}/tags`, fd, { 'Authorization': api_config.apiKey })
            .then(function() {
                self.getUserTags()
                self.setState({
                    tagValue: null,
                    name: ''
                })
            })
            .catch(function(error) {
                console.log(error);
			})
    }  

    pressPlay (){
        this.setState({
            isPlay: !this.state.isPlay
                })  
    }
    handleOpenMfcc =()=>{
        this.setState({
            mfccOpen: !this.state.mfccOpen
        })
    }
    
    handleOpenTags =()=>{
        this.setState({
            tagsOpen: !this.state.tagsOpen
        })
    }

    handleChangeSound = event => {
        console.log(event.target.value)
        this.setState({ [event.target.name]: event.target.value });
      };

    handleChangeUser = event => {
        this.setState({ [event.target.name]: event.target.value }, ()=>{
            this.getUserTags(this.props.userList[event.target.value])
        });
        
      };

      deleteUser(user){
        var self = this
        axios
            .delete(api_config.usePath + `/users/${user}`, {}, { 'Authorization': api_config.apiKey })
            .then(function(response) {
                self.handleClickVariant(`Poprawnie usunięto użytkownika ${user}!`, 'success')   
                self.handleOpenDelete()
                self.props.getUsers()
                self.setState({
                    user: ''
                })
            })
            .catch(function(error) {
                self.handleClickVariant(`Poczas usuwania użytkownika nastąpił błąd!`, 'error')
			})
      }

      deleteTag(){
        var self = this
        axios
            .delete(api_config.usePath + `/tag/${this.props.tagNameList[this.state.tag]}`, {}, { 'Authorization': api_config.apiKey })
            .then(function(response) {
                self.handleClickVariant(`Poprawnie usunięto tag ${self.props.tagNameList[self.state.tag]}!`, 'success')   
                self.setState({
                    tag: '',
                    tagValues: []
                })
            })
            .catch(function(error) {
                console.log(error)
                self.handleClickVariant(`Poczas usuwania taga nastąpił błąd!`+error.response&&error.response.data, 'error')
			})
      }
      deleteUserTag(tag){
        var self = this
        axios
            .delete(api_config.usePath + `/users/${this.props.userList[this.state.user]}/tags/${tag}`, {}, { 'Authorization': api_config.apiKey })
            .then(function(response) {
                self.handleClickVariant(`Poprawnie usunięto tag ${tag} użytkownika ${self.props.userList[self.state.user]}!`, 'success')   
                self.getUserTags()
            })
            .catch(function(error) {
                console.log(error)
                self.handleClickVariant(`Poczas usuwania taga nastąpił błąd!`, 'error')
			})
      }
      deleteUserSound(){
		var self = this
        axios
            .delete(api_config.usePath +`/audio/${this.state.type}/${this.props.userList[this.state.user]}/${this.state.userSounds[this.state.sound]}`, {}, { 'Authorization': api_config.apiKey })
            .then(function(response) {
                self.handleClickVariant(`Poprawnie usunięto próbkę ${self.state.userSounds[self.state.sound]}!`, 'success')   
                self.getAllUserSounds(self.props.userList[self.state.user])
                self.setState({
                    sound: ''
                })
            })
            .catch(function(error) {
                console.log(error)
                self.handleClickVariant(`Poczas usuwania próbki nastąpił błąd!`, 'error')
			})
    }
    
    handleChangeTag = event => {
        this.setState({ [event.target.name]: event.target.value }, ()=>this.getTagValues(this.props.tagNameList[event.target.value]))
        
      };

    handleTypeChange = event => {
        let self = this
        this.setState({ type: event.target.value, sound: '' }, ()=>this.getAllUserSounds(this.props.userList[this.state.user]));
      };
    getTagCount(user){
        var self = this
        axios
            .get(api_config.usePath + `/users/${user}`, {}, { 'Authorization': api_config.apiKey })
            .then(function(response) {
                let userTagCount = []
                userTagCount.push({name: 'test', value: response.data.samples[0].test})
                userTagCount.push({name: 'train', value: response.data.samples[0].train})
				self.setState({
                    userTagCount: userTagCount
                })
            })
            .catch(function(error) {
                console.log(error);
			})
    }
    getAllUserSounds(user) {
        var self = this
        axios
            .get(api_config.usePath + `/audio/${this.state.type}/${user}`, {}, { 'Authorization': api_config.apiKey })
            .then(function(response) {
				let userLetSounds = []
                response.data.samples.map(user => {
                    userLetSounds.push(user)
				})
				self.setState({
                    userSounds: userLetSounds
                }, ()=>self.getTagCount(user))
            })
            .catch(function(error) {
                console.log(error);
			})
    }

    getTagValues(tag){
        var self = this
        axios
            .get(api_config.usePath + `/tag/${tag}`, {}, { 'Authorization': api_config.apiKey })
            .then(function(response) {
				let tagValues = []
                response.data.map(user => {
                    tagValues.push(user)
				})
				self.setState({
                    tagValues: tagValues
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

    getSound() {
        var self = this
        axios({
            url: api_config.usePath +`/audio/${this.state.type}/${this.props.userList[this.state.user]}/${this.state.userSounds[this.state.sound]}`,
            method: 'GET',
            responseType: 'blob',
            headers: { 
                'Authorization': api_config.apiKey}
          })
            .then(function(response) {
                console.log(response)
                self.getMfcc()
                const url = window.URL.createObjectURL(new Blob([response.data]));
                self.setState({
                    url: url
                })
                self.handleClickVariant("Plik wczytano poprawnie!", 'success')
            })
            .catch(function(error) {
                self.handleClickVariant("Podczas wczytywania pliku wystąpił błąd!", 'error')
                console.log(error);
			})
    }

    handleChange = (event, value) => {
        this.setState({ value });
      }
    handleChangeUserTab = (event, value) => {
        console.log('kurwa',event, value)
        this.setState({ userValue: value });
      }

    getMfcc() {
        var self = this
        var data = JSON.stringify({ 
            "type": "mfcc"
        })
        axios({
            url: api_config.usePath +`/plot/${this.state.type}/${this.props.userList[this.state.user]}/${this.state.userSounds[this.state.sound]}`,
            method: 'GET',
            params: {"type": "mfcc"},
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                //'Authorization': api_config.apiKey
            },
            responseType: 'arraybuffer'
          })
            .then(function(response) {
                console.log(response)
                let blob = new Blob(
                    [response.data], 
                    { type: response.headers['content-type'] }
                  )
                  let image = URL.createObjectURL(blob)
                self.setState({
                    mfcc: image
                })
                self.handleClickVariant("Wykres mfcc wczytano poprawnie!", 'success')
            })
            .catch(function(error) {
                self.handleClickVariant("Podczas wczytywania wykresu mfcc wystąpił błąd!", 'error')
                console.log(error);
			})
    }

    getUserTags(user) {
        var self = this
        axios({
            url: api_config.usePath +`/users/${this.props.userList[this.state.user]}/tags`,
            method: 'GET',
            headers: { 'Authorization': api_config.apiKey}
          })
            .then(function(response) {
                console.log(response)
                var tags = self.state.userTags
                self.setState({
                    userTags: response.data
                }, ()=>self.getAllUserSounds(user))
            })
            .catch(function(error) {
                self.handleClickVariant("Podczas wczytywania wykresu mfcc wystąpił błąd!", 'error')
                console.log(error);
			})
    }
    handleChangePrzeglad= (event, value) =>{
        this.setState({
            tabPrzeglad: value
        })
    }
    render(){
        return(
            <Fade in={true}>
            <Paper style={{ backgroundColor: 'rgba(0, 0, 0, .6)'}}>   
                <div
				    style={{display: 'flex', flexDirection: 'row'}}
			        >
                    <div 
                        style={{
                            backgroundColor: 'rgba(0, 0, 0, .8)',
                            width: 360,
                            margin: 20,
                            borderRadius: 5,
                            textAlign: 'center',
                            display: 'flex',
                            flexDirection: 'column',
                            paddingLeft: 25,
                            paddingRight: 25,
                            paddingTop: 15,
                            border: '3px solid rgba(120, 0, 0, .6)',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    > 
            <Tabs
                value={this.state.tabPrzeglad}
                onChange={(e, v)=>this.handleChangePrzeglad(e,v)}
                indicatorColor="primary"
                textColor="primary"
                fixed
                style={{backgroundColor: 'black', marginBottom: 10, width: 320}}
                >
                <Tab label='Użytkownicy' />
                <Tab label='Tagi' />
            </Tabs>
                {this.state.tabPrzeglad === 0 &&<UserPrzeglad
                    user={this.state.user}
                    handleChangeUser={(e)=>this.handleChangeUser(e)} 
                    userList={this.props.userList}
                    userValue={this.state.userValue}
                    handleChangeUserTab={(e, v)=>this.handleChangeUserTab(e, v)}
                    userTagCount={this.state.userTagCount}
                    userTags={this.state.userTags}
                    name={this.state.name}
                    handleChangeName={(e)=>this.handleChangeName(e)}
                    tagNameList={this.props.tagNameList}
                    tagValue={this.state.tagValue}
                    handleChangeTagValue={(e)=>this.handleChangeTagValue(e)}
                    tagValuesList={this.state.tagValuesList}
                    addTagToUser={()=>this.addTagToUser()}
                    handleOpenDelete={()=>this.handleOpenDelete()}
                    deleteUserTag={(tag)=>this.deleteUserTag(tag)}
                />}
                {this.state.tabPrzeglad === 1 &&<TagPrzeglad
                    tagNameList={this.props.tagNameList}
                    handleOpenTags={()=>this.handleOpenTags()}
                    tag={this.state.tag}
                    tagValuesList={this.state.tagValues}
                    handleChangeTag={(e,v)=>this.handleChangeTag(e,v)}
                    deleteTag={()=>this.deleteTag()}
                />}
                </div>
                <div
                    style={{
                        backgroundColor: 'rgba(0, 0, 0, .6)',
                        width: '100%',
                        height: 440,
                        margin: 20,
                        borderRadius: 5,
                        textAlign: 'center',
                        display: 'flex',
                        flexDirection: 'column',
                        padding: 15,
                        border: '3px solid rgba(120, 0, 0, .6)',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                >
                {this.state.tabPrzeglad === 0 &&<UserPrzegladComponent 
                    userList={this.props.userList}
                    user={this.state.user}
                    type={this.state.type}
                    handleTypeChange={(e)=>this.handleTypeChange(e)}
                    sound={this.state.sound}
                    handleChangeSound={(e)=>this.handleChangeSound(e)}
                    userSounds={this.state.userSounds}
                    getSound={()=>this.getSound()}
                    url={this.state.url}
                    value={this.state.value}
                    handleChange={(e, v)=>this.handleChange(e,v)}
                    mfcc={this.state.mfcc}
                    handleOpenMfcc={()=>this.handleOpenMfcc()}
                    deleteUserSound={()=>this.deleteUserSound()}
                />}
                {this.state.tabPrzeglad === 1 &&
                    <TagPrzegladComponent
                        tagNameList={this.props.tagNameList}
                        userFullList={this.props.userFullList}
                    />}
                </div>
              </div>
              <MFCC 
                mfcc={this.state.mfcc} 
                mfccOpen={this.state.mfccOpen}
                handleOpenMfcc={()=>this.handleOpenMfcc}
                />
                <Tags 
                    tags={this.state.userTags}
                    tagsKeys={this.state.userTags !== [] ? Object.keys(this.state.userTags) : []}
                    user={this.props.userList[this.state.user]}
                    tagsOpen={this.state.tagsOpen}
                    handleOpenTags={()=>this.handleOpenTags()}
                    getUserTags={()=>this.getUserTags()}
                    getTagList={()=>this.props.getTagList()}
                    tagNameList={this.props.tagNameList}
                />
                <DeleteUser 
                    deleteOpen={this.state.deleteOpen}
                    user={this.props.userList[this.state.user]}
                    handleOpenDelete={()=>this.handleOpenDelete()}
                    deleteUser={()=>this.deleteUser(this.props.userList[this.state.user])}
                />
            </Paper>
            </Fade>
        )
    }
}
Przeglad.propTypes = {
    enqueueSnackbar: PropTypes.func.isRequired,
    userList: PropTypes.array
  };
  
  export default withSnackbar(Przeglad)