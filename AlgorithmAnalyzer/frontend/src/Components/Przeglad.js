import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import PropTypes from 'prop-types';
import axios from 'axios';
import FormLabel from '@material-ui/core/FormLabel';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Radio from '@material-ui/core/Radio';
import AudioSpectrum from "react-audio-spectrum"
import { withSnackbar } from 'notistack'
import MFCC from './MFCC'
import Tags from './Tags'

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
            tagsOpen: false
        }
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
        this.setState({ [event.target.name]: event.target.value });
      };

    handleChangeUser = event => {
        this.setState({ [event.target.name]: event.target.value }, ()=>this.getUserTags());
        this.getAllUserSounds(this.props.userList[event.target.value])
      };

    setData (array)  {
		this.setState({
			userSounds: array
		})
    }

    handleTypeChange = event => {
        let self = this
        this.setState({ type: event.target.value });
        setTimeout(function(){
            self.getAllUserSounds(self.props.userList[self.state.user])
        }, 300);
      };
    
    getAllUserSounds(user) {
        var self = this
        axios
            .get(`http://localhost:5000/audio/${this.state.type}/${user}`)
            .then(function(response) {
				let userLetSounds = []
                response.data.samples.map(user => {
                    userLetSounds.push(user)
				})
				self.setData(userLetSounds)
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
        this.getMfcc()
        var self = this
        axios({
            url: `http://localhost:5000/audio/${this.state.type}/${this.props.userList[this.state.user]}/${this.state.userSounds[this.state.sound]}`,
            method: 'GET',
            responseType: 'blob',
          })
            .then(function(response) {
                console.log(response)
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

    getMfcc() {
        var self = this
        var data = JSON.stringify({ 
            "type": "mfcc"
        })
        axios({
            url: `http://localhost:5000/plot/${this.state.type}/${this.props.userList[this.state.user]}/${this.state.userSounds[this.state.sound]}`,
            method: 'GET',
            data: data,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
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

    getUserTags() {
        console.log('ahoj')
        var self = this
        axios({
            url: `http://localhost:5000/users/${this.props.userList[this.state.user]}/tags`,
            method: 'GET'
          })
            .then(function(response) {
                console.log(response)
                var tags = self.state.userTags
                self.setState({
                    userTags: response.data
                })
            })
            .catch(function(error) {
                self.handleClickVariant("Podczas wczytywania wykresu mfcc wystąpił błąd!", 'error')
                console.log(error);
			})
    }
    render(){
        return(
            <Paper style={{ margin: 20,backgroundColor: 'rgba(0, 0, 0, .6)'}}>   
                <div
				    style={{display: 'flex', flexDirection: 'row'}}
			        >
                    <div 
                        style={{
                            backgroundColor: 'rgba(0, 0, 0, .8)',
                            width: '100%',
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
                    <Grid item xs={12} style={{display: 'flex',  justifyContent:'space-around', alignItems:'center', width: '100%'}}> 
                    <FormControl style={{ minWidth: 200, paddingRight: 10 }}>
                        <InputLabel >Wybierz użytkownika</InputLabel>
                        <Select
                            value={this.state.user}
                            onChange={this.handleChangeUser}
                            inputProps={{
                            name: 'user',
                            }}
                        >
                        <MenuItem value="">
                        <em>None</em>
                    </MenuItem>
                    {this.props.userList && this.props.userList.map((user, id) => <MenuItem key={id} value={id}>{user}</MenuItem>)}

                    </Select>
                </FormControl>
                <FormControl component="fieldset">
                    <FormLabel component="legend">Wybierz typ nagrania:</FormLabel>
                                <RadioGroup
                                    value={this.state.type}
                                    onChange={this.handleTypeChange}
                                    style={{flexDirection: 'row'}}
                                >
                                    <FormControlLabel value="train" control={<Radio />} label="Trenowanie" />
                                    <FormControlLabel value="test" control={<Radio />} label="Test" />
                                </RadioGroup>
                            </FormControl>
                <FormControl style={{ minWidth: 200, paddingRight: 10 }}>
                        <InputLabel >Wybierz próbkę</InputLabel>
                        <Select
                            value={this.state.sound}
                            onChange={this.handleChangeSound}
                            inputProps={{
                            name: 'sound'
                            }}
                        >
                        <MenuItem value=""/>
                        {this.state.userSounds && this.state.userSounds.map((sound, id) => <MenuItem key={id} value={id}>{sound}</MenuItem>)}
                    </Select>
                </FormControl>
                    <Button 
                        onClick={()=>this.getSound()} 
                        color='primary' 
                        variant="contained">
                        Załaduj próbkę
                    </Button>
                    <Button 
                        onClick={()=>this.handleOpenTags()}
                        color='primary' 
                        variant="contained">
                         Tagi
                    </Button>
                </Grid>
                <Grid item xs={12} style={{display: 'flex',  justifyContent:'space-around', alignItems:'center', width: '100%', marginTop: 30, minHeight: 300 }}> 
                <Typography variant="headline" gutterBottom>
                        Analiza próbki
                </Typography>
                <audio id="audio-element"
                            src={this.state.url}
                            controls
                            >
                        </audio>
                        <AudioSpectrum
                            id="audio-canvas"
                            height={200}
                            width={300}
                            audioId={'audio-element'}
                            capColor={'red'}
                            capHeight={2}
                            meterWidth={2}
                            meterCount={512}
                            meterColor={[
                                {stop: 0, color: '#f00'},
                                {stop: 0.5, color: '#0CD7FD'},
                                {stop: 1, color: 'red'}
                            ]}
                            gap={4}
                            />
                            {this.state.mfcc &&<Button onClick={()=>this.handleOpenMfcc()}>
                              <img 
                                src={this.state.mfcc} 
                                style={{
                                    width:280, backgroundColor: 'white', borderRadius: 10
                                    }} 
                                    />
                            </Button>}
                </Grid>
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
                />
            </Paper>
        )
    }
}
Przeglad.propTypes = {
    enqueueSnackbar: PropTypes.func.isRequired,
    userList: PropTypes.array
  };
  
  export default withSnackbar(Przeglad)