import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import FiberManualRecord from '@material-ui/icons/FiberManualRecord';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';

class Testuj2 extends Component { 
    constructor(props) {
        super(props);
        this.state = {
            age: '',
            name: 'hai',
        }
    }

    render(){
        return(
            <Paper style={{paddingLeft: 200, paddingRight: 200, paddingTop: 30, paddingBottom: 30, margin: 20}}>  
              <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}> 
                <Grid container spacing={24} style={{ paddingTop: 30}}>  
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
                    <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}>
                        <Button variant="outlined" color="primary">
                            Trenuj
                        </Button>             
                    </Grid>
                </Grid>
              </Grid>  
            </Paper>
        )
    }
}

export default Testuj2
