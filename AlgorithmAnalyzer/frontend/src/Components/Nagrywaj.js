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

class Recorder extends Component {
	constructor(props) {
		super(props);
		this.state = {
			isRecording: false,
			recorded: false,
			username: null,
			blob_audio_data: null,
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
	onPressButtonUpload() {
		if (this.state.recorded && this.state.username) {
			console.log("upload", this.state);
			let fd = new FormData();
			fd.append("username", this.state.username);
			fd.append("file", this.state.blob_audio_data.blob);
			let self = this;
			axios
				.post("http://127.0.0.1:5000/audio/train", fd, {
					headers: { "Content-Type": "multipart/form-data" },
				})
				.then(function(response) {
					console.log(response);
					self.setState({
						isRecording: false,
						recorded: false,
						blob_audio_data: null,
					});
				})
				.catch(function(error) {
					console.log(error);
				});
		} else {
			if (!this.state.recorded) {
				//#TODO: user feedback: jeszcze nic nie nagrano!
			}
			if (!this.state.username) {
				//#TODO: user feedback: nie wypełniono wymaganego pola!
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
							mimeType="audio/flac; codecs=opus"
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
			</Paper>
		);
	}
}

export default Recorder;