import React, { Component } from "react";
import { ReactMic } from "react-mic";
import axios from "axios";
import FormData from "form-data";
import PropTypes from 'prop-types';
import TextField from "@material-ui/core/TextField";
import Paper from "@material-ui/core/Paper";
import CloudUploadIcon from "@material-ui/icons/CloudUpload";
import Button from "@material-ui/core/Button";
import FiberManualRecord from "@material-ui/icons/FiberManualRecord";
import Stop from "@material-ui/icons/Stop";
import Files from 'react-files'
import Typography from '@material-ui/core/Typography';
import FormLabel from '@material-ui/core/FormLabel';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Radio from '@material-ui/core/Radio';
import FormControl from '@material-ui/core/FormControl';
import micro from '../img/micro.png'
import spinner from '../img/spinner.gif'
import AudioSpectrum from "react-audio-spectrum"
import Tabs from '@material-ui/core/Tabs'
import Tab from '@material-ui/core/Tab'
import AppBar from '@material-ui/core/AppBar'
import _ from 'lodash'
import { withSnackbar } from 'notistack'

class Recorder extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isRecording: false,
            recorded: false,
            username: null,
            blob_audio_data: [],
            recognizedText: '',
            type: 'train',
            fileErr: false,
            value: 0,
            uploaded: [],
            apiError: false
        };
        this.onPressButtonRecord = this.onPressButtonRecord.bind(this);
        this.onPressButtonStop = this.onPressButtonStop.bind(this);
        this.onPressButtonUpload = this.onPressButtonUpload.bind(this);
        this.onStop = this.onStop.bind(this);
    }

    handleClickVariant(text, variant){
        // variant could be success, error, warning or info
        this.props.enqueueSnackbar(text, { variant });
      }

    onPressButtonRecord() {
        console.log("record", this.state);
        this.setState({
            isRecording: true,
            recorded: false,
            value: this.state.blob_audio_data.length
        });
    }
    onPressButtonStop() {
        console.log("stop", this.state);
        this.setState({
            isRecording: false,
        });
    }

      saveAll(){
        if(this.state.blob_audio_data.length > 0){
            this.onPressButtonUpload(0, false, 0)
        } else
        this.handleClickVariant("Nie można zapisać pliku, nie został nagrany!", 'error')
    }

    onPressButtonUpload(value, onlyOne, counter) {
        if (this.state.recorded && this.state.username) {
            let fd = new FormData();
            fd.append("username", this.state.username);
            fd.append("file", this.state.blob_audio_data[value].blob ? this.state.blob_audio_data[value].blob : this.state.blob_audio_data[value] )
            let uploadedlist = this.state.uploaded
            uploadedlist.push({id: value})
            this.setState({
                uploaded: uploadedlist
            })
            let newlist = this.state.blob_audio_data.slice()
            newlist.splice(value, 1)
            let isRecorded = newlist.length > 0 ? true : false
            let self = this;
             return axios
                .post(`http://127.0.0.1:5000/audio/${this.state.type}`, fd, {
                    headers: { "Content-Type": "multipart/form-data" },
                })
                .then(function(response) {
                    self.handleClickVariant(`Plik ${value} zapisano poprawnie! ${response.data.text} `, 'success')
                    self.setState({
                        isRecording: false,
                        recorded: isRecorded,
                        blob_audio_data: newlist,
                        recognizedText: response.data.text,
                        uploaded: [],
                        value: 0,
                        apiError: false
                    });
                    !onlyOne && (value < self.state.blob_audio_data.length) && self.onPressButtonUpload(value, false, counter+1)
                    if(counter === self.state.blob_audio_data.length)
                    {
                        self.setState({
                            blob_audio_data: [],
                            recorded: false
                        }, ()=>self.props.getUsers())
                    }
                    onlyOne &&setTimeout(() => {
                        console.log('odświerzam userów')
                        self.props.getUsers()
                    }, 2000)
                })
                .catch(function(error) {
                    self.setState({
                        apiError: true
                    })
                    self.handleClickVariant(`Podczas zapisu pliku ${value} wystąpił błąd!`, 'error')
                    console.log(error);
                })
        } else {
            if (!this.state.recorded) {
                return this.handleClickVariant("Nie można zapisać pliku, nie został nagrany!", 'error')
            }
            if (!this.state.username) {
                return this.handleClickVariant("Nie można zapisać pliku, podaj imię i nazwisko!", 'error')
            }
        }

    }
    onInputChange(e) {
        this.setState({ username: e.target.value });
    }
    onStop(recordedBlob) {
        let blobList = this.state.blob_audio_data
        blobList.push(recordedBlob)
        this.setState({ blob_audio_data: blobList, recorded: true });
        console.log("Recorded Blob:", recordedBlob);
    }
    onData(recordedBlob) {
        // console.log("real time data", recordedBlob);
    }
    handleTypeChange = event => {
        this.setState({ type: event.target.value });
      };

    onFilesChange(file) {
        this.setState({
            fileErr: false
        })
        this.onFilesError.bind(this)
        if(!this.state.fileErr){
            let blobList = this.state.blob_audio_data
            let copy = file.slice()
            copy.map(el=>blobList.push(el))
            while(file.length !== 0){
                file.pop()
            }
            console.log('lol', blobList.length-1)
            this.setState({
                blob_audio_data: blobList,
                recorded: true,
                value: blobList.length-1
            })
            this.handleClickVariant('Plik wczytano poprawnie!', 'success')
        } else{
            console.log('błąd')
        }
      }

    onFilesError(error, file) {
        if(error.code === 1) {
                this.setState({
                    fileErr: true
                })
                this.handleClickVariant("Niepoprawny format pliku!", 'error')
        } else if(error.code === 2) {
            this.setState({
                fileErr: true
            })
            this.handleClickVariant("Plik jest zbyt duży!", 'error')
    }
        console.log('error code ' + error.code + ': ' + error.message)
    }

    handleChange = (event, value) => {
        this.setState({ value });
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
                        <Button
                            variant="contained"
                            color="default"
                            style={{ display: "block", display: 'flex' }}
                            onClick={()=>this.onPressButtonUpload(this.state.value, true, 0)}
                        >
                            Save
                            <CloudUploadIcon style={{paddingLeft: 5}}/>
                        </Button>
                        <Button
                            variant="contained"
                            color="default"
                            style={{ display: "block", display: 'flex', marginTop: 20 }}
                            onClick={()=>this.saveAll()}
                        >
                            Save all
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
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-around',
                    width: '100%',
                    paddingTop: 20,
                    paddingBottom: 20}}>
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
                            maxFiles={200}
                            maxFileSize={10000000}
                            minFileSize={0}
                            clickable
                            style={{width: 300}}
                            >
                            <Button
                                color='primary'
                                variant="contained"
                                >
                                Upuść tutaj plik/i, lub kliknij aby wybrać plik/i z komputera
                            </Button>
                        </Files>
                    </div>
            {this.state.recorded ? (
                <div style={{width: '100%'}}>
                <AppBar position="static" color="default">
                    <Tabs
                        value={this.state.value}
                        onChange={this.handleChange}
                        indicatorColor="primary"
                        textColor="primary"
                        scrollable
                        scrollButtons="auto"
                        style={{backgroundColor: 'black'}}
                        >
                        {this.state.blob_audio_data.map((sound, i)=>
                            _.find(this.state.uploaded, {id: i}) && !this.state.apiError ?
                                <Tab icon={<img src={spinner} style={{width:30, height: 30}} />} />:
                                <Tab label={i+1} />
                        )}
                    </Tabs>
                </AppBar>
                {this.state.blob_audio_data.map((sound, i)=>
                    this.state.value === i &&
                            <Paper style={{ padding: 5, width: '100%', backgroundColor: 'transparent'}}>
                                <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                                    <audio id="audio-element"
                                        src={sound.blobURL ? sound.blobURL : window.URL.createObjectURL(sound)}
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
                )}
                </div>
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
        );
    }
}

Recorder.propTypes = {
    enqueueSnackbar: PropTypes.func.isRequired,
    getUsers: PropTypes.func
  };

export default withSnackbar(Recorder);