import React, {Component} from 'react'
import MUIDataTable from "mui-datatables";
import { createMuiTheme, MuiThemeProvider } from '@material-ui/core/styles';

export default class TagPrzegladComponent extends Component {
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
    render(){
        const columns = ['użytkownik'].concat(this.props.tagNameList)
        
        const options = {
            rowsPerPageOptions: [5, 10, 50],
            rowsPerPage: 5,
            filterType: 'dropdown',
            responsive: "scroll",
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
            <MuiThemeProvider theme={this.getMuiTheme()}>
            <div style={{maxWidth: '800px'}}>
                            <MUIDataTable 
                                title={"Lista użytkowników"}
                                data={this.props.userFullList}
                                columns={columns}
                                options={options}
                                />
                                </div>

                    </MuiThemeProvider>
        )
    }
}