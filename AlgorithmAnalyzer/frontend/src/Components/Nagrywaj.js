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
import KeyboardVoice from "@material-ui/icons/KeyboardVoice";
import Grid from "@material-ui/core/Grid";
import MySnackbarContent from './MySnackbarContent'
import Typography from '@material-ui/core/Typography';
import FormLabel from '@material-ui/core/FormLabel';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Radio from '@material-ui/core/Radio';
import FormControl from '@material-ui/core/FormControl';

class Recorder extends Component {
	constructor(props) {
		super(props);
		this.state = {
			isRecording: false,
			recorded: false,
			username: null,
			blob_audio_data: null,
			openErrorNoAudio: false,
			openSuccess: false,
			openErrorNoUser: false,
			openErrorSave: false,
			recognizedText: '',
			type: 'test'
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
			fd.append("file", this.state.blob_audio_data.blob);
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
	render() {
		return (
			<Paper
				style={{
					paddingLeft: 200,
					paddingRight: 200,
					paddingTop: 30,
					paddingBottom: 30,
					margin: 20,
				}}
				elevation={12}
			>
				<Grid
					item
					xs={12}
					style={{
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
					}}
				>
					<KeyboardVoice style={{ fontSize: 100 }} />
				</Grid>
				<Grid
					item
					xs={12}
					style={{
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
					}}
				>
					{this.state.recorded && !this.state.username ? (
						<TextField
							error
							label="Podaj imię i nazwisko"
							margin="normal"
							variant="outlined"
							outliner="red"
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
				</Grid>
				<Grid
					item
					xs={12}
					style={{
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
						paddingTop: 20,
					}}
				>
					<FormControl component="fieldset">
							<FormLabel component="legend">Wybierz typ nagrania:</FormLabel>
							<RadioGroup
								value={this.state.type}
								onChange={this.handleTypeChange}
								style={{flexDirection: 'row'}}
							>
								<FormControlLabel value="train" control={<Radio />} label="Trenowanie" />
								<FormControlLabel value="test" control={<Radio />} label="Test" />
							</RadioGroup>
						</FormControl>
				</Grid>
				<Grid
					container
					style={{
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
					}}
				>
					<Button
						variant="fab"
						color={this.state.isRecording ? "default" : "secondary"}
						aria-label="Add"
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
				</Grid>
				<Grid
					item
					xs={12}
					style={{
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
						paddingTop: 20,
					}}
				>
					{this.state.recorded ? (
						<audio
							ref="audioSource"
							controls="controls"
							src={this.state.blob_audio_data.blobURL}
						/>
					) : (
						<ReactMic
							record={this.state.isRecording}
							className="sound-wave"
							onStop={this.onStop}
							onData={this.onData}
							strokeColor="#2e7d32"
							backgroundColor="#ffffff"
							mimeType="audio/webm; codecs=opus"
						/>
					)}
				</Grid>
				<Grid
					item
					xs={12}
					style={{
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
						paddingTop: 40,
					}}
				>
				<Typography 
					variant="subheading" 
					gutterBottom
				>
					{this.state.recognizedText}
				</Typography>
				</Grid>
				<Grid
					item
					xs={12}
					style={{
						display: "flex",
						justifyContent: "center",
						alignItems: "center",
						paddingTop: 40,
					}}
				>
					<Button
						variant="contained"
						color="default"
						style={{ display: "block" }}
						onClick={this.onPressButtonUpload}
					>
						Save
						<CloudUploadIcon />
					</Button>
				</Grid>
				<MySnackbarContent 
					recognizedText={this.state.recognizedText}
					openErrorNoAudio={this.state.openErrorNoAudio}
					openSuccess={this.state.openSuccess}
					openErrorNoUser={this.state.openErrorNoUser}
					openErrorSave={this.state.openErrorSave}
					SnackbarHandleClose={()=>this.SnackbarHandleClose}
				/>
			</Paper>
		);
	}
}

export default Recorder;