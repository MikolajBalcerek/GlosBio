import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import MUIDataTable from "mui-datatables";
import { createMuiTheme, MuiThemeProvider } from '@material-ui/core/styles';
import 'typeface-roboto'
import labels from '../labels.json'
import axios from 'axios';

export default class Statystyki extends Component {
    getMuiTheme = () => createMuiTheme({
        palette: {
            type: 'dark'
          },
        overrides: {
            MUIDataTableHeadCell: {
                fixedHeader: {
                  backgroundColor: '#212121',
                },
                sortActive: {
                    color: 'white'
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
                    fontFamily: 'Roboto'
                }
            },
            MUIDataTableToolbarSelect: {
                root: {
                    backgroundColor: 'inherit',
                },
                title: {
                    color: 'white',
                    fontFamily: 'Roboto'
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
            }
          }
      })
      state= {
          userList: [],
          userFullList: []
      }

      componentWillReceiveProps(nextProps){
          if(nextProps.userList !== this.state.userList) {
            var newUserList = nextProps.userList.slice()
            nextProps.userList.map(user=>this.getUserTags(user))
          }

      }

      getUserTags(user) {
        var self = this
        axios({
            url: labels.usePath +`/users/${this.props.userList[this.state.user]}/tags`,
            method: 'GET',
            headers: { 'Authorization': labels.apiKey}
          })
            .then(function(response) {
                console.log(response)
                var tags = self.state.userTags
                self.setState({
                    userTags: response.data
                })
            })
            .catch(function(error) {
                self.handleClickVariant("Podczas wczytywania wykresu mfcc wystąpił błąd!", 'error')
                console.log(error);
			})
    }

    render(){
        const columns = this.props.tagNameList;
 
        const data = [
        ["Joe James", "Test Corp", "Yonkers", "NY", "Joe James", "Test Corp", "Yonkers", "NY", "Joe James", "Test Corp"],
        ["John Walsh", "Test Corp", "Hartford", "CT", "John Walsh", "Test Corp", "Hartford", "CT", "John Walsh", "Test Corp"],
        ["Bob Herm", "Test Corp", "Tampa", "FL", "Bob Herm", "Test Corp", "Tampa", "FL", "Bob Herm", "Test Corp"],
        ["James Houston", "Test Corp", "Dallas", "TX", "James Houston", "Test Corp", "Dallas", "TX", "James Houston", "Test Corp"],
        ];
        
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
            <Paper style={{paddingLeft: 200, paddingRight: 200, paddingTop: 30, paddingBottom: 30, margin: 20,backgroundColor: 'rgba(0, 0, 0, .6)'}}>
                <MuiThemeProvider theme={this.getMuiTheme()}>
                    <MUIDataTable 
                        title={"Lista użytkowników"}
                        data={data}
                        columns={columns}
                        options={options}
                        />
                </MuiThemeProvider>
            </Paper>
        )
    }
}