import React, { Component } from 'react'
import TextField from '@material-ui/core/TextField';
import Paper from '@material-ui/core/Paper';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import Button from '@material-ui/core/Button';
import FiberManualRecord from '@material-ui/icons/FiberManualRecord';
import PlayArrow from '@material-ui/icons/PlayArrow';
import Stop from '@material-ui/icons/Stop';
import KeyboardVoice from '@material-ui/icons/KeyboardVoice';
import Grid from '@material-ui/core/Grid';
import Pause from '@material-ui/icons/Pause';

class Nagrywaj extends Component { 
    constructor(props) {
        super(props);
        this.state = {
            isPlay: false
        }
    }
    pressPlay (){
        this.setState({
            isPlay: !this.state.isPlay
                })  
    }
    render(){
        return(
            <Paper style={{paddingLeft: 200, paddingRight: 200, paddingTop: 30, paddingBottom: 30, margin: 20}} elevation={12}>   
            <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}>       
                <KeyboardVoice style={{ fontSize: 100 }}/>
            </Grid>    
            <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}>
                <TextField
                    label="Podaj imię i nazwisko"
                    margin="normal"
                    variant="outlined"
                    />
            </Grid>          
        <Grid container spacing={24} style={{paddingLeft: 220, paddingRight: 220, paddingTop: 30}}>     
            <Grid item xs={4} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}>
                <Button variant="fab" color="secondary" aria-label="Add">
                    <FiberManualRecord />
                </Button>
            </Grid>
            <Grid item xs={4} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}>
                <Button variant="fab" color="default" aria-label="Add">
                    <Stop />
                </Button>
            </Grid>    
            <Grid item xs={4} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}>
                <Button variant="fab" color="primary" aria-label="Add" onClick={()=>{this.pressPlay()}}>
                    {this.state.isPlay ? <Pause /> : <PlayArrow />}
                </Button>
            </Grid>
        </Grid>       
        <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center', paddingTop: 40 }}>        
                <Button variant="contained" color="default" style={{display: 'block'}}>
                    Upload
                    <CloudUploadIcon />
                </Button>
        </Grid>        
            </Paper >
        )
    }
}

export default Nagrywaj
