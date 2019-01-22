import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import _ from 'lodash'
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import WykresyKolowe from './WykresyKolowe'
import Fade from '@material-ui/core/Fade';

export default class Statystyki extends Component {
      state= {
          userList: [],
          userFullList: [],
          value: 0
      }

    handleChange = (event, value) => {
        this.setState({ value });
      };

    render(){

        return(
            <Fade in={true}>
            <Paper 
                style={{
                    paddingLeft: 30, 
                    paddingRight: 30,
                    height: 500,
                    backgroundColor: 'rgba(0, 0, 0, .6)'
                }}>

                    <WykresyKolowe
                        userSoundsTrainCount={this.props.userSoundsTrainCount}
                        userSoundsTestCount={this.props.userSoundsTestCount}
                        tagCount={this.props.tagCount}
                        tagReady={this.props.tagReady}
                    />
            </Paper>
            </Fade>
        )
    }
}