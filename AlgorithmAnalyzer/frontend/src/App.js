import React, { Component } from 'react';
import MainPage from './Components/MainPage';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import green from '@material-ui/core/colors/green';
import red from '@material-ui/core/colors/red';
import yellow from '@material-ui/core/colors/yellow';
import style from './App.css'
import 'typeface-roboto';

class App extends Component {
  render() {
    const theme = createMuiTheme({
      palette: {
        type: 'dark',
        primary: { main: yellow[800] }, // Purple and green play nicely together.
        secondary: { main: red[800] }, // This is just green.A700 as hex.
      },
    });
    return (
      <MuiThemeProvider theme={theme}>
        <MainPage />
      </MuiThemeProvider>
    );
  }
}

export default App;
