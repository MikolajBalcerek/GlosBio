import React, { Component } from "react";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Paper from "@material-ui/core/Paper";
import Tabs from "@material-ui/core/Tabs";
import Tab from "@material-ui/core/Tab";
import Recorder from "./Nagrywaj";
import Przeglad from "./Przeglad";
import Trenuj from "./Trenuj";
import Testuj1 from "./Testuj1";
import Testuj2 from "./Testuj2";
import Avatar from "@material-ui/core/Avatar";
import logo from "../img/GLOSBIO.png";

class MainPage extends Component {
	state = {
		value: 0,
	};

	handleChange = (event, value) => {
		this.setState({ value });
	};

	render() {
		const { value } = this.state;
		return (
			<div>
				<AppBar position="static" color="primary">
					<Toolbar>
						<Avatar
							alt="Głos Bio"
							src={logo}
							style={{ marginRight: 15 }}
						/>
						<Typography variant="title" color="inherit">
							Głos Biometryczny
						</Typography>
					</Toolbar>
				</AppBar>
				<Paper>
					<Tabs
						value={value}
						onChange={this.handleChange}
						indicatorColor="primary"
						textColor="primary"
						centered
					>
						<Tab label="Nagrywaj" />
						<Tab label="Przegląd" />
						<Tab label="Trenuj" />
						<Tab label="Testuj ( zidentyfikuj )" />
						<Tab label="Testuj ( all )" />
					</Tabs>
				</Paper>
				{value === 0 && <Recorder />}
				{value === 1 && <Przeglad />}
				{value === 2 && <Trenuj />}
				{value === 3 && <Testuj1 />}
				{value === 4 && <Testuj2 />}
			</div>
		);
	}
}

export default MainPage;
