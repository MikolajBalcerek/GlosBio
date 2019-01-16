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
import labels from '../labels.json'

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
            .get(labels.usePath +`/tag`, {}, { 'Authorization': labels.apiKey })
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

    handleChangeName = event => {
        this.setState({ [event.target.name]: event.target.value }, ()=>this.getUserTagValues());
      };

    handleChangeTagValue = event => {
        this.setState({ [event.target.name]: event.target.value });
      };

    onInputChange(e) {
		this.setState({ newTagName: e.target.value });
    }

    onInputChangeTag(e, i) {
        var list = this.state.newTagValues
        list[i] = e.target.value
		this.setState({ newTagValues: list });
    }

    addTagToUser(){
        var self = this
        let fd = new FormData();
        fd.append("name", this.state.tagNameList[this.state.name]);
        fd.append("value", this.state.tagValuesList[this.state.tagValue]);
        axios
            .post(labels.usePath +`/users/${this.props.user}/tags`, fd, { 'Authorization': labels.apiKey })
            .then(function() {
                self.props.getUserTags()
                self.setState({
                    tagValue: null,
                    name: ''
                })
            })
            .catch(function(error) {
                console.log(error);
			})
    }  

    getUserTagValues(){
        var self = this
        axios
            .get(labels.usePath +`/tag/${this.state.tagNameList[this.state.name]}`, {}, { 'Authorization': labels.apiKey })
            .then(function(response) {
                console.log(response.data)
				self.setState({
                    tagValuesList: response.data
                })
            })
            .catch(function(error) {
                console.log(error);
			})
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
            .post(labels.usePath +`/tag`, fd, { 'Authorization': labels.apiKey })
            .then(function() {
                self.getTagList()
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
                {this.props.user &&<Paper style={{ margin: 20, padding: 10}}>
                    <DialogTitle id="simple-dialog-title">Tagi użytkownika {this.props.user}</DialogTitle>
                    <div style={{
                                height: 260, 
                                overflow: 'auto'}}>
                        <Table >
                            <TableHead>
                            <TableRow>
                                <TableCell>Nazwa</TableCell>
                                <TableCell align="right">Wartość</TableCell>
                            </TableRow>
                            </TableHead>
                            <TableBody>
                            {this.props.tagsKeys.length > 0 && this.props.tagsKeys.map((tag, i) => {
                                return (
                                <TableRow key={i}>
                                    <TableCell component="th" scope="row">
                                    {tag}
                                    </TableCell>
                                    <TableCell align="right">
                                    {this.props.tags[tag]}
                                    </TableCell>
                                </TableRow>
                                );
                            })}
                            <TableRow>
                                    <TableCell component="th" scope="row">
                                        <Select
                                            value={this.state.name}
                                            onChange={this.handleChangeName}
                                            inputProps={{
                                            name: 'name',
                                            }}
                                        >
                                        <MenuItem value="">
                                            <em>None</em>
                                        </MenuItem>
                                        {this.state.tagNameList && this.state.tagNameList.map(
                                            (name, id) => 
                                            this.props.tagsKeys.indexOf(name) === -1 && <MenuItem key={id} value={id}>{name}</MenuItem>
                                            )
                                            }
                                        </Select>
                                    </TableCell>
                                    <TableCell align="right">
                                        <Select
                                            value={this.state.tagValue}
                                            onChange={this.handleChangeTagValue}
                                            inputProps={{
                                            name: 'tagValue',
                                            }}
                                        >
                                        <MenuItem value="">
                                            <em>None</em>
                                        </MenuItem>
                                        {this.state.tagValuesList && this.state.tagValuesList.map((val, id) => <MenuItem key={id} value={id}>{val}</MenuItem>)}
                                        </Select>
                                    </TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </div>
                    <div style={{display: 'flex'}}>
                        <Button 
                            variant="contained" 
                            onClick={()=>this.addTagToUser()} 
                            style={{margin: 30}}
                            disabled={!(this.state.tagValue || this.state.tagValue === 0)}
                            color='primary'
                            >
                            Przypisz tag
                        </Button>
                    </div>
                </Paper>}
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