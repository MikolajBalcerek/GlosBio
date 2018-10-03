import React, { Component } from 'react';
import MainPage from './Components/MainPage';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import green from '@material-ui/core/colors/green';
import red from '@material-ui/core/colors/red';

class App extends Component {
  render() {
    const theme = createMuiTheme({
      palette: {
        primary: { main: green[800] }, // Purple and green play nicely together.
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
