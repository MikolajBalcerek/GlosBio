import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import MUIDataTable from "mui-datatables";
import { createMuiTheme, MuiThemeProvider } from '@material-ui/core/styles';
import api_config from '../api_config.json'
import axios from 'axios';
import _ from 'lodash'
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import WykresyKolowe from './WykresyKolowe'

export default class Statystyki extends Component {
    getMuiTheme = () => createMuiTheme({
        palette: {
            type: 'dark'
          },
        overrides: {
            MUIDataTableHeadCell: {
                fixedHeader: {
                  backgroundColor: '#212121',
                  minWidth: '105px'
                },
                sortActive: {
                    color: 'white'
                },
                toolButton:{
                    margin: '5px'
                }
              },
            MUIDataTableSelectCell: {
                headerCell: {
                    backgroundColor: '#212121',
                }
              },
            MUIDataTableToolbar: {
                titleText: {
                    color: 'white !important',
                    fontFamily: 'Roboto, sans-serif'
                }
            },
            MUIDataTableToolbarSelect: {
                root: {
                    backgroundColor: 'inherit',
                },
                title: {
                    color: 'white',
                    fontFamily: 'Roboto, sans-serif'
                }
            },
            MUIDataTableViewCol: {
                label: {
                    color: 'white'
                },
                title: {
                    color: 'white'
                }
            },
            MUIDataTableFilter: {
                checkboxFormControlLabel: {
                    color: 'white'
                },
                title: {
                    color: 'white'
                } 
            },
            MuiTabScrollButton: {
                root: {
                    color: 'white'
                }
            }
          }
      })
      state= {
          userList: [],
          userFullList: [],
          value: 0
      }
      componentDidMount(){
          this.props.userList.map(user=>this.getUserTags(user))
      }
      
      componentWillReceiveProps(nextProps){
          if(!_.isEqual(nextProps.userList, this.state.userList)) {
            var newUserList = nextProps.userList.slice()
            nextProps.userList.map(user=>this.getUserTags(user))
          }

      }

      getUserTags(user) {
        var self = this
        axios({
            url: api_config.usePath +`/users/${user}/tags`,
            method: 'GET',
            headers: { 'Authorization': api_config.apiKey}
          })
            .then(function(response) {
                var tags = self.state.userTags
                var userTable = [user]
                self.props.tagNameList.map(tag=>{
                    (tag in response.data) ? userTable.push(response.data[tag]) : userTable.push('')}
                    )
                var newUserTable = self.state.userFullList
                newUserTable.push(userTable)
                self.setState({
                    userFullList: newUserTable
                })
            })
            .catch(function(error) {
                console.log(error);
			})
    }

    handleChange = (event, value) => {
        this.setState({ value });
      };

    render(){
        const columns = ['użytkownik'].concat(this.props.tagNameList)
        
        const options = {
            filterType: 'checkbox',
            responsive: 'scroll',
            expandable: true,
            textLabels: {
                body: {
                noMatch: "Brak danych",
                toolTip: "Sortuj",
                },
                pagination: {
                next: "Następna strona",
                previous: "Poprzednia strona",
                rowsPerPage: "Ilość wierszy na stronie:",
                displayRows: "z",
                },
                toolbar: {
                search: "Wyszukaj",
                downloadCsv: "Pobierz CSV",
                print: "Drukuj",
                viewColumns: "Zobacz kolumny",
                filterTable: "Filtruj tabelę",
                },
                filter: {
                all: "Wszystkie",
                title: "Filtry",
                reset: "RESETUJ",
                },
                viewColumns: {
                title: "Pokaż kolumny",
                titleAria: "Pokaż/schowaj kolumny",
                },
                selectedRows: {
                text: "zaznaczone wiersze",
                delete: "Usuń",
                deleteAria: "Usuń zaznaczone wiersze",
                },
          }
        };

        return(
            <Paper style={{paddingLeft: 30, paddingRight: 30,backgroundColor: 'rgba(0, 0, 0, .6)'}}>
                <Tabs
                    value={this.state.value}
                    onChange={this.handleChange}
                    indicatorColor="primary"
                    textColor="primary"
                    scrollable
                    scrollButtons="auto"
                    style={{backgroundColor: 'black', marginBottom: 10}}
                    >
                        <Tab label='Tabela' />
                        <Tab label='Wykresy kołowe' />
                    </Tabs>
                {this.state.value === 0 &&
                    <MuiThemeProvider theme={this.getMuiTheme()}>
                        <MUIDataTable 
                            title={"Lista użytkowników"}
                            data={this.state.userFullList}
                            columns={columns}
                            options={options}
                            />
                    </MuiThemeProvider>}
                {this.state.value === 1 &&
                    <WykresyKolowe
                        userSoundsTrainCount={this.props.userSoundsTrainCount}
                        userSoundsTestCount={this.props.userSoundsTestCount}
                        tagCount={this.props.tagCount}
                    />
                }
            </Paper>
        )
    }
}