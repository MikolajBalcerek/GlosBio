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
import AudioPlayer from "react-h5-audio-player";
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
            url: ''
        }
    }

    pressPlay (){
        this.setState({
            isPlay: !this.state.isPlay
                })  
    }

    handleChangeSound = event => {
        this.setState({ [event.target.name]: event.target.value });
      };

    handleChangeUser = event => {
        this.setState({ [event.target.name]: event.target.value });
        
        this.getAllUserSounds(this.props.userlist[event.target.value])
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
            self.getAllUserSounds(self.props.userlist[self.state.user])
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
    getSound() {
        var self = this
        axios({
            url: `http://localhost:5000/audio/${this.state.type}/${this.props.userlist[this.state.user]}/${this.state.userSounds[this.state.sound]}`,
            method: 'GET',
            responseType: 'blob',
          })
            .then(function(response) {
                console.log(response)
                const url = window.URL.createObjectURL(new Blob([response.data]));
                self.setState({
                    url: url
                })
            })
            .catch(function(error) {
                console.log(error);
			})
    }

    render(){
        return(
            <Paper style={{paddingLeft: 200, paddingRight: 200, paddingTop: 30, paddingBottom: 30, margin: 20}}>   
                <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}> 
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
                {this.props.userlist && this.props.userlist.map((user, id) => <MenuItem key={id} value={id}>{user}</MenuItem>)}

                </Select>
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
              </Grid>
              <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center', marginTop: 30 }}> 
                <Button onClick={()=>this.getSound()} color='primary' variant="contained">Załaduj próbkę</Button>
              </Grid>
              <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center', marginTop: 30 }}> 
              <Typography variant="headline" gutterBottom>
                    Analiza próbki
              </Typography>
              </Grid>
              <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center' }}> 
              <Paper style={{paddingLeft: 200, paddingRight: 200, paddingTop: 30, paddingBottom: 30, margin: 20, width: 500}}>      
                <AudioPlayer
                    autoPlay={false}
                    src={this.state.url}
                />
              </Paper>
              </Grid>
            </Paper>
        )
    }
}
Przeglad.propTypes = {
    userlist: PropTypes.array
  };
export default Przeglad
