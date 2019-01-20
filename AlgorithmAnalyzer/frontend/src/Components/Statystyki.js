import React, { Component } from 'react'
import Paper from '@material-ui/core/Paper';
import MUIDataTable from "mui-datatables";
import { createMuiTheme, MuiThemeProvider } from '@material-ui/core/styles';
import _ from 'lodash'
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import WykresyKolowe from './WykresyKolowe'
import Fade from '@material-ui/core/Fade';

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

    handleChange = (event, value) => {
        this.setState({ value });
      };

    render(){
        const columns = ['użytkownik'].concat(this.props.tagNameList)
        
        const options = {
            rowsPerPageOptions: [5, 10, 50],
            rowsPerPage: 5,
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
            <Fade in={true}>
            <Paper 
                style={{
                    paddingLeft: 30, 
                    paddingRight: 30,
                    backgroundColor: 'rgba(0, 0, 0, .6)'
                }}>
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
                                data={this.props.userFullList}
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
            </Fade>
        )
    }
}