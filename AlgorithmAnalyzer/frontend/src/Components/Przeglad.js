import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Pause from '@material-ui/icons/Pause';
import PlayArrow from '@material-ui/icons/PlayArrow';

class Przeglad extends Component { 
    constructor(props) {
        super(props);
        this.state = {
            isPlay: false,
            age: '',
            name: 'hai',
        }
    }

    pressPlay (){
        this.setState({
            isPlay: !this.state.isPlay
                })  
    }
    
    handleChange = event => {
        this.setState({ [event.target.name]: event.target.value });
      };

    render(){
        return(
            <Paper style={{paddingLeft: 200, paddingRight: 200, paddingTop: 30, paddingBottom: 30, margin: 20}}>   
                <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}> 
                <FormControl style={{ minWidth: 200 }}>
                    <InputLabel htmlFor="age-simple">Wybierz próbkę</InputLabel>
                    <Select
                        value={this.state.age}
                        onChange={this.handleChange}
                        inputProps={{
                        name: 'age',
                        id: 'age-simple',
                        }}
                    >
                    <MenuItem value="">
                    <em>None</em>
                  </MenuItem>
                  <MenuItem value={10}>Próbka 1</MenuItem>
                  <MenuItem value={20}>Próbka 2</MenuItem>
                  <MenuItem value={30}>Próbka 3</MenuItem>
                </Select>
              </FormControl>
              </Grid>
              <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center', marginTop: 30 }}> 
              <Typography variant="headline" gutterBottom>
                    Analiza próbki
              </Typography>
              </Grid>
              <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center' }}> 
              <Paper style={{paddingLeft: 200, paddingRight: 200, paddingTop: 30, paddingBottom: 30, margin: 20}}>
                <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}>
                    <Button variant="fab" color="primary" aria-label="Add" onClick={()=>{this.pressPlay()}}>
                        {this.state.isPlay ? <Pause /> : <PlayArrow />}
                    </Button>
                </Grid>
              </Paper>
              </Grid>
            </Paper>
        )
    }
}

export default Przeglad
