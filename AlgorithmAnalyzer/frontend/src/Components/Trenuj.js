import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';

class Trenuj extends Component { 
    constructor(props) {
        super(props);
        this.state = {
        }
    }

    render(){
        return(
            <Paper style={{paddingLeft: 200, paddingRight: 200, paddingTop: 30, paddingBottom: 30, margin: 20}}>   
                <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center'}}> 
                <Button variant="outlined" color="primary">
                    Trenuj
                </Button>
              </Grid>
              <Grid item xs={12} style={{display: 'flex',  justifyContent:'center', alignItems:'center' }}> 
              <Paper style={{paddingLeft: 200, paddingRight: 200, paddingTop: 30, paddingBottom: 30, margin: 20}}>
                
              </Paper>
              </Grid>
            </Paper>
        )
    }
}

export default Trenuj
