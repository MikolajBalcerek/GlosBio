import React, {Component} from 'react'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import Button from '@material-ui/core/Button'
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Select from '@material-ui/core/Select';
import axios from 'axios';
import MenuItem from '@material-ui/core/MenuItem';
import _ from 'lodash'
import TextField from "@material-ui/core/TextField";
import Paper from '@material-ui/core/Paper';
import DeleteIcon from '@material-ui/icons/Delete';
import { withSnackbar } from 'notistack'
import PropTypes from 'prop-types';
import api_config from '../api_config.json'

class Tags extends Component{
    state = {
        tagValuesList: [],
        tagValue: null,
        tagNameList: [],
        name: '',
        disabled: true,
        newTagValues: [''],
        newTagName: ''
    }

    componentDidMount(){
        this.getTagList()
    }

    getTagList() {
        var self = this
        axios
            .get(api_config.usePath +`/tag`, {}, { 'Authorization': api_config.apiKey })
            .then(function(response) {
				self.setState({
                    tagNameList: response.data
                })
            })
            .catch(function(error) {
                console.log(error);
			})
    }

    handleClickVariant(text, variant){
		// variant could be success, error, warning or info
		this.props.enqueueSnackbar(text, { variant });
      }

    onInputChange(e) {
		this.setState({ newTagName: e.target.value });
    }

    onInputChangeTag(e, i) {
        var list = this.state.newTagValues
        list[i] = e.target.value
		this.setState({ newTagValues: list });
    }

    closeTags(){
        this.props.handleOpenTags()
        this.setState({
            tagValue: null,
            name: '',
            newTagValues: [''],
            newTagName: ''
        })
    }

    addPlace(){
        var list = this.state.newTagValues
        list.push('')
        this.setState({
            newTagValues: list
        })
    }

    deletePlace(i){
        var list = this.state.newTagValues
        console.log(list)
        list.splice(i, 1)
        console.log(list)
        this.setState({
            newTagValues: list
        })
    }
    saveTag(){
        var self = this
        let fd = new FormData();
        fd.append("name", this.state.newTagName);
        fd.append("values", JSON.stringify(this.state.newTagValues));
        axios
            .post(api_config.usePath +`/tag`, fd, { 'Authorization': api_config.apiKey })
            .then(function() {
                self.props.getTagList()
                self.setState({
                    newTagValues: [''],
                    newTagName: ''
                })
                self.handleClickVariant("Dodano nowy tag!", 'success')
            })
            .catch(function(error) {
                self.handleClickVariant("Podczas dodawania nastąpił błąd!", 'error')
			})
    }
      render(){
        return(
          <Dialog open={this.props.tagsOpen} maxWidth='lg' >
          <div style={{display: 'flex', flexDirection: 'row', backgroundColor: 'rgb(20, 21, 25)'}}>
                <Paper style={{ margin: 20, padding: 10, height: 400}}>
                    <DialogTitle id="simple-dialog-title">Dodaj nowy tag</DialogTitle>
                    <div style={{display: 'flex'}}>
                        <TextField
                                label="Podaj nazwę taga"
                                margin="normal"
                                variant="outlined"
                                style={{borderColor: 'white'}}
                                value={this.state.newTagName}
                                onChange={event => {
                                    this.onInputChange(event);
                                }}
                            />
                        <div style={{
                                marginLeft: 10, 
                                display: 'flex', 
                                flexDirection: 'column', 
                                height: 260, 
                                overflow: 'auto'
                                }}>
                            {this.state.newTagValues &&this.state.newTagValues.map((tag, i)=>
                                <div >
                                    <TextField
                                        label="Podaj wartość taga"
                                        margin="normal"
                                        variant="outlined"
                                        style={{
                                            borderColor: 'white',
                                            minHeight: 55,
                                            maxHeight: 55
                                        }}
                                        value={this.state.newTagValues[i]}
                                        onChange={event => {
                                            this.onInputChangeTag(event, i);
                                        }}
                                        />
                                        {
                                            i === 0 &&
                                            <Button 
                                                color='primary'
                                                variant="contained" 
                                                onClick={()=>this.addPlace()} style={{ height: 40, marginLeft: 10, marginTop: 25}}
                                                >
                                                Dodaj pole
                                            </Button> 
                                        }
                                    {i !== 0 && <Button 
                                        color='red'
                                        variant="contained" 
                                        onClick={()=>this.deletePlace(i)} style={{ height: 40, marginLeft: 10, marginTop: 25}}
                                        >
                                        <DeleteIcon />
                                    </Button>}
                                </div>
                            )}
                        </div>
                    </div>
                    <div style={{display: 'flex', justifyContent: 'center'}}>
                        <Button 
                            variant="contained" 
                            onClick={()=>this.saveTag()} 
                            style={{margin: 30}}
                            disabled={this.state.newTagName === ''}
                        >
                                Zapisz tag
                            </Button>
                    </div>
                </Paper>
            </div>
            <div style={{ backgroundColor: 'rgb(20, 21, 25)', display: 'flex', justifyContent: 'center'}}>
                <Button variant="contained" onClick={()=>this.closeTags()} style={{margin: 30}}>
                                Wyjdź
                            </Button>
            </div>
          </Dialog> 
        )
    }
}
Tags.propTypes = {
    enqueueSnackbar: PropTypes.func.isRequired
  };
  
  export default withSnackbar(Tags)