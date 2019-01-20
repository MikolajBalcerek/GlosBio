import React, {Component} from 'react'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import Button from '@material-ui/core/Button'
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';

export default class TestModal extends Component {
    render(){
        return(
            <Dialog 
            open={this.props.testModalOpen} 
            maxWidth='lg' 
            style={{
                margin: 20
                }}>
                <DialogTitle id="simple-dialog-title">Wyniki testu</DialogTitle>
                <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
                    <div 
                        style={{
                            display: 'flex',
                            justifyContent: 'space-around',
                            width:'100%',
                            alignItems: 'center'
                            }}>
                        </div>
                    </div>
                    <Table>
                        <TableBody>
                            <TableRow>
                                <TableCell style={{textAlign: 'center'}}>Prognozowany wynik:</TableCell>
                                <TableCell style={{textAlign: 'center'}}>{this.props.predictions&&this.props.predictions.prediction ? 
                                    <div style={{backgroundColor: 'green', padding: 15, borderRadius: 10}}>Użytkownik potrwierdzony</div> : 
                                    <div style={{backgroundColor: 'red', padding: 15, borderRadius: 10}}>Użytkownik odrzucony</div>  }</TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                    <Table>
                        <TableBody>
                            {this.props.predictions && this.props.predictions.meta.length > 0 &&this.props.predictions.meta.map(
                                key=>
                                <TableRow>
                                    <TableCell style={{textAlign: 'center'}}>{key}</TableCell>
                                    <TableCell style={{textAlign: 'center'}}>{this.props.predictions.meta[key]}</TableCell>
                                </TableRow>
                                     )}
                        </TableBody>
                    </Table>
                <Button variant="contained" onClick={()=>this.props.handleTestChange()} style={{margin: 30}}>
                    Wyjdź
                </Button>
          </Dialog> 
        )
    }
}