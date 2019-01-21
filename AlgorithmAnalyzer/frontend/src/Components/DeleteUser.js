import React, {Component} from 'react'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import Button from '@material-ui/core/Button'

export default class DeleteUser extends Component{
    render(){
        return(
          <Dialog open={this.props.deleteOpen} maxWidth='lg'>
                <DialogTitle id="simple-dialog-title">Czy na pewno chcesz usunąć użytkownika {this.props.user}</DialogTitle>
                <div style={{display: 'flex', justifyContent: 'center'}}>
                    <Button onClick={()=>this.props.handleOpenDelete()} style={{margin: 30}} secondary>
                        Anuluj
                    </Button>
                    <Button  onClick={(u)=>this.props.deleteUser(u)} style={{margin: 30, backgroundColor: 'red'}}>
                        Usuń
                    </Button>
                </div>
          </Dialog> 
        )
    }
}