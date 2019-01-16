import React, {Component} from 'react'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import Button from '@material-ui/core/Button'
import Paper from '@material-ui/core/Paper'

export default class MFCC extends Component{
    render(){
        return(
          <Dialog open={this.props.mfccOpen} maxWidth='lg'>
                <DialogTitle id="simple-dialog-title">Wykres MFCC</DialogTitle>
                <img src={this.props.mfcc} style={{width:500, backgroundColor: 'white', borderRadius: 10, marginLeft: 30, marginRight: 30}}/>
                <Button variant="contained" onClick={this.props.handleOpenMfcc()} style={{margin: 30}}>
                    Wyjdź
                </Button>
          </Dialog> 
        )
    }
}