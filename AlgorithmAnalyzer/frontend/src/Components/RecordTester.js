import React, { Component } from "react";
import { ReactMic } from "react-mic";
import axios from "axios";
import FormData from "form-data";

import PropTypes from 'prop-types';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import Paper from "@material-ui/core/Paper";
import Button from "@material-ui/core/Button";
import FiberManualRecord from "@material-ui/icons/FiberManualRecord";
import Stop from "@material-ui/icons/Stop";
import Files from 'react-files'
import FormControl from '@material-ui/core/FormControl';
import micro from '../img/micro.png'
import AudioSpectrum from "react-audio-spectrum"
import api_config from '../api_config.json'
import Fade from '@material-ui/core/Fade';

class RecordTester extends Component {
    constructor(props) {
        super(props);
        this.state = {
            algorithm: '',
            user: '',
            username: '',

            isRecording: false,
            recorded: false,

            blob_audio_data: null,
            blob_audio_data2: null,

            openErrorNoAudio: false,
            openSuccess: false,
            openErrorNoAlgorithm: false,
            openErrorNoUser: false,
            openErrorSave: false,
            openErrorFileType: false,
            openErrorFileSize: false,
            openSuccessFile: false,

            fileErr: false,
            status: "",
            predictions: []
        };
        this.onPressButtonRecord = this.onPressButtonRecord.bind(this);
        this.onPressButtonStop = this.onPressButtonStop.bind(this);
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


    handleSimpleChange = event => {
        this.setState({ [event.target.name]: event.target.value });
      };

    handleUserChange = event => {
        this.setState({
        [event.target.name]: event.target.value,
        username: this.props.userList[event.target.value]
        });
    };

    SnackbarHandleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
          }
        this.setState({ openErrorNoAudio: false, openSuccess: false, openErrorNoUser: false, openErrorSave: false });
      };

    onPressButtonUpload = () => {
        console.log(this.state.username);
        if (this.state.recorded && this.state.username && this.state.algorithm) {
            console.log("uploading to test", this.state);
            let fd = new FormData();
            fd.append("username", this.state.user);
            fd.append("file", this.state.blob_audio_data ? this.state.blob_audio_data.blob : this.state.blob_audio_data2);
            let self = this;
            axios
                .post(api_config.usePath + `/algorithms/test/${this.state.username}/${this.state.algorithm}`,
                    fd,
                    {
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
                        status: "Received prediction.",
                        predictions: response.data
                    });
                })
                .catch(function(error) {
                    self.setState({
                        openErrorSave: true
                    });
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
            if (!this.state.algorithm) {
                this.setState({
                    openErrorNoAlgorithm: !this.state.openErrorNoAlgorithm
                })
            }
        }
    };

    onStop(recordedBlob) {
        this.setState({ blob_audio_data: recordedBlob, recorded: true });
        console.log("Recorded Blob:", recordedBlob);
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
            <Fade in={true}>
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
                <div style={{paddingBottom: 10}}>
                    <Button
                        variant="contained"
                        color="default"
                        style={{ display: "block"}}
                        onClick={this.onPressButtonUpload}
                    >
                        Testuj
                    </Button>
                </div>
                <FormControl style={{ minWidth: 200, paddingBottom: 10}}>
                            <InputLabel >Wybierz algorytm</InputLabel>
                            <Select
                                value={this.state.algorithm}
                                onChange={this.handleSimpleChange}
                                inputProps={{
                                    name: 'algorithm',
                                }}
                            >
                            <MenuItem value="">
                                <em>None</em>
                            </MenuItem>
                            {this.props.algorithmList && this.props.algorithmList.map((name) => <MenuItem key={name} value={name}>{name}</MenuItem>)}
                            </Select>
                </FormControl>
                <FormControl style={{ minWidth: 200, paddingBottom: 10}}>
                            <InputLabel >Wybierz użytkownika</InputLabel>
                            <Select
                                value={this.state.user}
                                onChange={this.handleUserChange}
                                inputProps={{
                                    name: 'user',
                                }}
                            >
                            <MenuItem value="">
                                <em>None</em>
                            </MenuItem>
                            {this.props.userList && this.props.userList.map((user, id) => <MenuItem key={id} value={id}>{user}</MenuItem>)}
                            </Select>
                </FormControl>
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
            </Paper>
            </Fade>
        );
    }
}


RecordTester.propTypes = {
    algorithmList: PropTypes.array,
    userList: PropTypes.array
  };

export default RecordTester;