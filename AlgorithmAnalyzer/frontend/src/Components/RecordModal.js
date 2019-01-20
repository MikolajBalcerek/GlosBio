import React, {Component} from 'react'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import Button from '@material-ui/core/Button'
import FiberManualRecord from "@material-ui/icons/FiberManualRecord";
import Stop from "@material-ui/icons/Stop";
import { ReactMic } from "react-mic";

export default class RecordModal extends Component{
    componentDidMount(){
        var self = this
        document.addEventListener('keydown', (event)=> {
            if (event.keyCode === 32 || event.keyCode === 13){
                console.log('lel', self.props.isRecording)
                self.props.isRecording
                ? this.props.onPressButtonStop()
                : this.props.onPressButtonRecord()
            }
          });
    }
    render(){
        return(
          <Dialog 
            open={this.props.recordModalOpen} 
            maxWidth='lg' 
            style={{
                margin: 20
                }}>
                <DialogTitle id="simple-dialog-title">Nagraj próbkę</DialogTitle>
                <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
                    <div 
                        style={{
                            display: 'flex',
                            justifyContent: 'space-around',
                            width:'100%',
                            alignItems: 'center'
                            }}>
                        <Button
                            variant="fab"
                            color={this.props.isRecording ? "default" : "secondary"}
                            aria-label="Add"
                            style={{margin: 20}}
                            onClick={
                                this.props.isRecording
                                    ? this.props.onPressButtonStop
                                    : this.props.onPressButtonRecord
                            }
                                >
                            {this.props.isRecording ? (
                                <Stop />
                                    ) : (
                                <FiberManualRecord />
                                )}
                                </Button>
                                <Button
                                        variant="contained"
                                        color="default"
                                        style={{ 
                                            display: 'flex', 
                                            marginRight: 15,
                                            height: 40
                                        }}
                                        onClick={()=>this.props.generujTekst()}
                                    >
                                    Generuj tekst
                                </Button>
                            </div>
                        <div 
                            style={{
                                color: 'white', 
                                fontFamily: 'Roboto, sans-serif',
                                width: 600
                                }}>
                                {this.props.generowanyTekst}
                        </div>
                    </div>    
                    <div style={{
                        border: '10px solid black',
                        backgroundColor: 'black',
                        borderRadius: 10,
                        margin: 20
                        }}>
                    <ReactMic
                        record={this.props.isRecording}
                        className="sound-wave"
                        onStop={this.props.onStop()}
                        onData={this.props.onData()}
                        strokeColor="yellow"
                        style={{border: '4px solid black', borderRadius: 15}}
                        backgroundColor='black'
                        mimeType="audio/webm; codecs=opus"
                    />
                    </div>
                <Button variant="contained" onClick={()=>this.props.handleRecordChange()} style={{margin: 30}}>
                    Wyjdź
                </Button>
          </Dialog> 
        )
    }
}