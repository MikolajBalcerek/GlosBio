import React, { Component } from "react";
import { ReactMic } from "react-mic";
import axios from "axios";
import FormData from "form-data";


import TextField from "@material-ui/core/TextField";
import Paper from "@material-ui/core/Paper";
import CloudUploadIcon from "@material-ui/icons/CloudUpload";
import Button from "@material-ui/core/Button";
import FiberManualRecord from "@material-ui/icons/FiberManualRecord";
import Stop from "@material-ui/icons/Stop";
import Files from 'react-files'
import MySnackbarContent from './MySnackbarContent'
import Typography from '@material-ui/core/Typography';
import FormLabel from '@material-ui/core/FormLabel';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Radio from '@material-ui/core/Radio';
import Checkbox from '@material-ui/core/Checkbox';
import FormControl from '@material-ui/core/FormControl';
import micro from '../img/micro.png'
import AudioSpectrum from "react-audio-spectrum"

class Recorder extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isRecording: false,
            recorded: false,
            username: null,
            blob_audio_data: null,
            blob_audio_data2: null,
            openErrorNoAudio: false,
            openSuccess: false,
            openErrorNoUser: false,
            openErrorSave: false,
            openErrorFileType: false,
            openErrorFileSize: false,
            openSuccessFile: false,
            recognizedText: '',
            type: 'test',
            fileErr: false,
            fake: false
        };
        this.onPressButtonRecord = this.onPressButtonRecord.bind(this);
        this.onPressButtonStop = this.onPressButtonStop.bind(this);
        this.onPressButtonUpload = this.onPressButtonUpload.bind(this);
        this.onStop = this.onStop.bind(this);
    }

    onPressButtonRecord() {
        console.log("record", this.state);
        this.setState({
            isRecording: true,
            recorded: false,
        });
    }
    onPressButtonStop() {
        console.log("stop", this.state);
        this.setState({
            isRecording: false,
        });
    }
    handleChangeFake = event => {
        this.setState({fake: !this.state.fake});
    }

    SnackbarHandleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
          }
        this.setState({ openErrorNoAudio: false, openSuccess: false, openErrorNoUser: false, openErrorSave: false });
      };

    onPressButtonUpload() {
        if (this.state.recorded && this.state.username) {
            console.log("upload", this.state);
            let fd = new FormData();
            fd.append("username", this.state.username);
            fd.append("file", this.state.blob_audio_data ? this.state.blob_audio_data.blob : this.state.blob_audio_data2);
            fd.append("fake", this.state.fake);
            let self = this;
            axios
                .post(`http://127.0.0.1:5000/audio/${this.state.type}`, fd, {
                    headers: { "Content-Type": "multipart/form-data" },
                })
                .then(function(response) {
                    console.log(response);
                    self.setState({
                        openSuccess: true,
                        isRecording: false,
                        recorded: false,
                        blob_audio_data: null,
                        blob_audio_data2: null,
                        recognizedText: response.data.text
                    });
                })
                .catch(function(error) {
                    self.setState({
                        openErrorSave: true
                    })
                    console.log(error);
                });
        } else {
            if (!this.state.recorded) {
                this.setState({
                    openErrorNoAudio: !this.state.openErrorNoAudio
                })
            }
            if (!this.state.username) {
                this.setState({
                    openErrorNoUser: !this.state.openErrorNoUser
                })
            }
        }
        setTimeout(() => {
            console.log('odświerzam userów')
            this.props.getUsers()
        }, 2000);
    }
    onInputChange(e) {
        this.setState({ username: e.target.value });
    }
    onStop(recordedBlob) {
        this.setState({ blob_audio_data: recordedBlob, recorded: true });
        console.log("Recorded Blob:", recordedBlob);
    }
    onData(recordedBlob) {
        // console.log("real time data", recordedBlob);
    }
    handleTypeChange = event => {
        this.setState({ type: event.target.value });
      };

    onFilesChange(file) {
        file.splice()
        console.log('lol', file)
        this.setState({
            fileErr: false
        })
        this.onFilesError.bind(this)
        if(!this.state.fileErr){
            this.setState({
                blob_audio_data: null,
                blob_audio_data2: file[file.length-1],
                recorded: true,
                openUploadSuccess: true
            })
            setTimeout(() => {
                this.setState({
                    openUploadSuccess: false
                })
            }, 2000);
            console.log(this.state.blob_audio_data2)
        } else{
            console.log('błąd')
        }
      }

    onFilesError(error, file) {
        if(error.code === 1) {
                this.setState({
                    fileErr: true,
                    openErrorFileType: true
                })
            setTimeout(() => {
                this.setState({
                    openErrorFileType: false
                })
            }, 2000);
        } else if(error.code === 2) {
            this.setState({
                fileErr: true,
                openErrorFileSize: true
            })
        setTimeout(() => {
            this.setState({
                openErrorFileSize: false
            })
        }, 2000);
    }
        console.log('error code ' + error.code + ': ' + error.message)
    }
    render() {
        return (
            <Paper
                style={{
                    paddingBottom: 30,
                    margin: 20,
                    backgroundColor: 'transparent',
                    backgroundSize: 'cover',
                    height: 'calc(100% - 245px)'
                }}
                elevation={12}
            >
            <div
                style={{display: 'flex', flexDirection: 'row', width: '100%', height: '100%'}}
            >
            <div
                style={{
                    backgroundColor: 'rgba(0, 0, 0, .8)',
                    width: '25%',
                    minHeight: 350,
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
            {this.state.recorded && !this.state.username ? (
                        <TextField
                            error
                            label="Podaj imię i nazwisko"
                            margin="normal"
                            variant="outlined"
                            style={{borderColor: 'white'}}
                            onChange={event => {
                                this.onInputChange(event);
                            }}
                        />
                    ) : (
                        <TextField
                            label="Podaj imię i nazwisko"
                            margin="normal"
                            variant="outlined"
                            outliner="red"
                            onChange={event => {
                                this.onInputChange(event);
                            }}
                        />
                    )}
                    <FormControl component="fieldset">
                            <FormLabel component="legend">Wybierz typ nagrania:</FormLabel>
                            <RadioGroup
                                value={this.state.type}
                                onChange={this.handleTypeChange}
                                style={{flexDirection: 'row', alignItems: 'center'}}
                            >
                                <FormControlLabel value="train" control={<Radio />} label="Trenowanie" />
                                <FormControlLabel value="test" control={<Radio />} label="Test" />
                            </RadioGroup>
                    </FormControl>
                    <FormControlLabel
                      control={
                            <Checkbox
                              checked={this.state.fake}
                              onChange={this.handleChangeFake}
                              value="fake"
                            />
                          }
                          label="Fake"
                          style={{paddingBottom: 10}}
                    />
                    <Button
                        variant="contained"
                        color="default"
                        style={{ display: "block", display: 'flex' }}
                        onClick={this.onPressButtonUpload}
                    >
                        Save
                        <CloudUploadIcon style={{paddingLeft: 5}}/>
                    </Button>
                <Typography
                    variant="subheading"
                    gutterBottom
                >
                    {this.state.recognizedText!== 'None' && this.state.recognizedText}
                </Typography>
            </div>
            <div
                style={{
                    backgroundColor: 'rgba(0, 0, 0, .6)',
                    width: '75%',
                    margin: 20,
                    borderRadius: 5,
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    padding: 5,
                    border: '3px solid rgba(120, 0, 0, .6)',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}
            >
                <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-around', width: '100%', paddingTop: 20,paddingBottom: 20}}>
                <img
                    src={micro}
                    style={{width: 60, margin: 0}}
                />
                    <Button
                            variant="fab"
                            color={this.state.isRecording ? "default" : "secondary"}
                            aria-label="Add"
                            style={{margin: 20}}
                            onClick={
                                this.state.isRecording
                                    ? this.onPressButtonStop
                                    : this.onPressButtonRecord
                            }
                        >
                            {this.state.isRecording ? (
                                <Stop />
                            ) : (
                                <FiberManualRecord />
                            )}
                        </Button>
                        <Files
                            className='files-dropzone'
                            onChange={this.onFilesChange.bind(this)}
                            onError={this.onFilesError.bind(this)}
                            accepts={['.wav']}
                            multiple
                            maxFiles={1}
                            maxFileSize={10000000}
                            minFileSize={0}
                            clickable
                            style={{width: 300}}
                            >
                            <Button
                                color='primary'
                                variant="contained"
                                >
                                Upuść tutaj plik, lub kliknij aby wybrać plik z komputera
                            </Button>
                        </Files>
                    </div>
            {this.state.recorded ? (
                <Paper style={{ padding: 5, width: '100%', backgroundColor: 'transparent'}}>
                    <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                        <audio id="audio-element"
                            src={this.state.blob_audio_data ? this.state.blob_audio_data.blobURL : window.URL.createObjectURL(this.state.blob_audio_data2)}
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
                        </div>
                </Paper>
            ) : (
                <div style={{
                    border: '10px solid black',
                    backgroundColor: 'black',
                    borderRadius: 10,
                    marginTop: 43,
                    marginBottom: 43
                    }}>
                <ReactMic
                    record={this.state.isRecording}
                    className="sound-wave"
                    onStop={this.onStop}
                    onData={this.onData}
                    strokeColor="yellow"
                    style={{border: '4px solid black', borderRadius: 15}}
                    backgroundColor='black'
                    mimeType="audio/webm; codecs=opus"
                />
                </div>
            )}
            </div>
            </div>
                <MySnackbarContent
                    recognizedText={this.state.recognizedText}
                    openErrorNoAudio={this.state.openErrorNoAudio}
                    openSuccess={this.state.openSuccess}
                    openErrorNoUser={this.state.openErrorNoUser}
                    openErrorSave={this.state.openErrorSave}
                    SnackbarHandleClose={()=>this.SnackbarHandleClose}
                    openErrorFileType={this.state.openErrorFileType}
                    openErrorFileSize={this.state.openErrorFileSize}
                    openUploadSuccess={this.state.openUploadSuccess}
                />
            </Paper>
        );
    }
}

export default Recorder;